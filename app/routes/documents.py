import zipfile
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from app.ingestion.extractors import SUPPORTED_EXTENSIONS
from app.ingestion.indexer import process_document

from app.retrieval.vector_store import (
    delete_document,
    index_document,
    list_documents,
)

from app.retrieval.retriever import search_documents


documents_bp = Blueprint("documents", __name__)


def production_access_blocked():
    if current_app.config["APP_ENV"] == "production":
        return jsonify({
            "error": "Document management requires authentication. "
                     "Admin authentication is not implemented yet."
        }), 503

    return None


def validate_uploaded_file(path: Path) -> None:
    extension = path.suffix.lower()

    with path.open("rb") as file:
        header = file.read(8192)

    if extension == ".pdf":
        if not header.startswith(b"%PDF-"):
            raise ValueError("Invalid PDF file.")

    elif extension in {".docx", ".xlsx"}:
        if not header.startswith(b"PK"):
            raise ValueError("Invalid Office document.")

        try:
            with zipfile.ZipFile(path) as archive:
                names = set(archive.namelist())

                total_uncompressed = sum(
                    item.file_size
                    for item in archive.infolist()
                )

                if len(names) > 5000 or total_uncompressed > 100 * 1024 * 1024:
                    raise ValueError(
                        "Office document exceeds safety limits."
                    )

                required_file = (
                    "word/document.xml"
                    if extension == ".docx"
                    else "xl/workbook.xml"
                )

                if required_file not in names:
                    raise ValueError(
                        "Invalid Office document structure."
                    )

                if archive.testzip() is not None:
                    raise ValueError("Office document is corrupted.")

        except zipfile.BadZipFile as error:
            raise ValueError(
                "Invalid Office document archive."
            ) from error

    elif extension in {".txt", ".csv"}:
        try:
            path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError as error:
            raise ValueError(
                "Only UTF-8 encoded text and CSV files are supported."
            ) from error


@documents_bp.post("/upload")
def upload_document():
    blocked = production_access_blocked()

    if blocked:
        return blocked

    if "file" not in request.files:
        return jsonify({
            "error": "No file was provided. Use the 'file' field."
        }), 400

    uploaded_file = request.files["file"]

    if not uploaded_file.filename:
        return jsonify({
            "error": "Please select a document."
        }), 400

    original_filename = secure_filename(
        uploaded_file.filename
    )

    if not original_filename:
        return jsonify({
            "error": "Invalid filename."
        }), 400

    extension = Path(original_filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        return jsonify({
            "error": "Unsupported file type.",
            "supported_formats": sorted(SUPPORTED_EXTENSIONS),
        }), 415

    upload_directory = Path(
        current_app.config["UPLOAD_FOLDER"]
    )

    upload_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    stored_filename = f"{uuid4().hex}{extension}"
    destination = upload_directory / stored_filename

    try:
        uploaded_file.save(destination)

        validate_uploaded_file(destination)

        processed = process_document(
            path=destination,
            original_filename=original_filename,
        )

        indexing_result = index_document(processed)

        if indexing_result["duplicate"]:
            destination.unlink(missing_ok=True)

            return jsonify({
                "error": "Duplicate document.",
                "message": indexing_result["message"],
                "existing_document_id": (
                    indexing_result["existing_document_id"]
                ),
            }), 409

        current_app.logger.info(
            "Document indexed: %s | chunks=%s",
            original_filename,
            indexing_result["indexed_chunks"],
        )

        return jsonify({
            "message": "Document uploaded and indexed successfully.",
            "document": processed["document"],
            "statistics": {
                "total_characters": processed["total_characters"],
                "total_tokens": processed["total_tokens"],
                "total_chunks": processed["total_chunks"],
            },
            "indexing": indexing_result,
        }), 201

    except ValueError as error:
        destination.unlink(missing_ok=True)

        return jsonify({
            "error": str(error),
        }), 400

    except Exception:
        destination.unlink(missing_ok=True)

        current_app.logger.exception(
            "Document indexing failed: %s",
            original_filename,
        )

        return jsonify({
            "error": "Document processing or indexing failed. "
                     "Check application logs."
        }), 500


@documents_bp.get("/")
def get_documents():
    blocked = production_access_blocked()

    if blocked:
        return blocked

    try:
        documents = list_documents()

        return jsonify({
            "total_documents": len(documents),
            "documents": documents,
        }), 200

    except Exception:
        current_app.logger.exception(
            "Failed to retrieve document list."
        )

        return jsonify({
            "error": "Unable to retrieve documents."
        }), 500


@documents_bp.post("/search")
def search():
    blocked = production_access_blocked()

    if blocked:
        return blocked

    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify({
            "error": "A JSON request body is required."
        }), 400

    query = payload.get("query")

    if not isinstance(query, str) or not query.strip():
        return jsonify({
            "error": "A valid search query is required."
        }), 400

    if len(query) > 2000:
        return jsonify({
            "error": "Search query cannot exceed 2000 characters."
        }), 400

    n_results = payload.get("n_results", 5)

    if type(n_results) is not int or not 1 <= n_results <= 10:
        return jsonify({
            "error": "n_results must be an integer between 1 and 10."
        }), 400

    document_id = payload.get("document_id")

    if document_id is not None and (
        not isinstance(document_id, str)
        or not document_id.strip()
    ):
        return jsonify({
            "error": "document_id must be a non-empty string."
        }), 400

    try:
        matches = search_documents(
            query=query,
            n_results=n_results,
            document_id=document_id,
        )

        return jsonify({
            "query": query,
            "total_results": len(matches),
            "results": matches,
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error),
        }), 400

    except Exception:
        current_app.logger.exception(
            "Semantic search failed."
        )

        return jsonify({
            "error": "Search failed. Check application logs."
        }), 500


@documents_bp.delete("/<document_id>")
def remove_document(document_id):
    blocked = production_access_blocked()

    if blocked:
        return blocked

    try:
        deleted = delete_document(document_id)

        if not deleted:
            return jsonify({
                "error": "Document not found."
            }), 404

        current_app.logger.info(
            "Deleted indexed document: %s",
            document_id,
        )

        return jsonify({
            "message": "Document and its indexed chunks deleted.",
            "document_id": document_id,
        }), 200

    except Exception:
        current_app.logger.exception(
            "Document deletion failed."
        )

        return jsonify({
            "error": "Unable to delete document."
        }), 500
