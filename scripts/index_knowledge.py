import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.ingestion.extractors import SUPPORTED_EXTENSIONS
from app.ingestion.indexer import process_document
from app.retrieval.vector_store import get_collection, index_document


KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "knowledge"


def main():
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(
        path
        for path in KNOWLEDGE_DIR.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not files:
        print("No supported knowledge documents found.")
        return

    collection = get_collection()

    print(f"Knowledge directory: {KNOWLEDGE_DIR}")
    print(f"Documents discovered: {len(files)}")
    print(f"Existing indexed chunks: {collection.count()}")
    print("-" * 55)

    for path in files:
        try:
            processed = process_document(
                path=path,
                original_filename=path.name,
            )

            result = index_document(processed)

            if result["duplicate"]:
                print(f"[SKIPPED] {path.name}: already indexed")
            else:
                print(
                    f"[INDEXED] {path.name}: "
                    f"{result['indexed_chunks']} chunks"
                )

        except Exception as error:
            print(f"[FAILED] {path.name}: {error}")
            raise

    print("-" * 55)
    print(f"Total indexed chunks: {collection.count()}")


if __name__ == "__main__":
    main()
