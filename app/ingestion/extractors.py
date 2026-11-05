import csv
from pathlib import Path

from docx import Document
from openpyxl import load_workbook
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".csv",
    ".xlsx",
}


def extract_pdf(path: Path) -> str:
    reader = PdfReader(str(path))

    if reader.is_encrypted:
        raise ValueError("Encrypted PDF files are not supported.")

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        content = page.extract_text() or ""

        if content.strip():
            pages.append(
                f"Page {page_number}\n{content}"
            )

    return "\n\n".join(pages)


def extract_docx(path: Path) -> str:
    document = Document(str(path))
    sections = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            sections.append(text)

    for table_number, table in enumerate(document.tables, start=1):
        sections.append(f"Table {table_number}")

        for row in table.rows:
            cells = [
                cell.text.strip().replace("\n", " ")
                for cell in row.cells
            ]

            if any(cells):
                sections.append(" | ".join(cells))

    return "\n\n".join(sections)


def extract_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def extract_csv(path: Path) -> str:
    sections = []

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        reader = csv.reader(csv_file)

        headers = next(reader, None)

        if not headers:
            return ""

        headers = [str(value).strip() for value in headers]

        sections.append("CSV columns: " + " | ".join(headers))

        for row_number, row in enumerate(reader, start=1):
            values = []

            for index, value in enumerate(row):
                column = (
                    headers[index]
                    if index < len(headers)
                    else f"Column {index + 1}"
                )

                values.append(f"{column}: {value.strip()}")

            if values:
                sections.append(
                    f"Row {row_number}: " + " | ".join(values)
                )

    return "\n\n".join(sections)


def extract_xlsx(path: Path) -> str:
    workbook = load_workbook(
        filename=path,
        read_only=True,
        data_only=True,
    )

    sections = []

    try:
        for worksheet in workbook.worksheets:
            sections.append(
                f"Worksheet: {worksheet.title}"
            )

            rows = worksheet.iter_rows(values_only=True)

            headers = next(rows, None)

            if not headers:
                continue

            headers = [
                str(value).strip() if value is not None else f"Column {i + 1}"
                for i, value in enumerate(headers)
            ]

            sections.append(
                "Columns: " + " | ".join(headers)
            )

            for row_number, row in enumerate(rows, start=1):
                values = []

                for index, value in enumerate(row):
                    if value is None:
                        continue

                    column = (
                        headers[index]
                        if index < len(headers)
                        else f"Column {index + 1}"
                    )

                    values.append(f"{column}: {value}")

                if values:
                    sections.append(
                        f"Row {row_number}: " + " | ".join(values)
                    )

    finally:
        workbook.close()

    return "\n\n".join(sections)


def extract_document(path: Path) -> str:
    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported document format: {extension}"
        )

    extractors = {
        ".pdf": extract_pdf,
        ".docx": extract_docx,
        ".txt": extract_txt,
        ".csv": extract_csv,
        ".xlsx": extract_xlsx,
    }

    return extractors[extension](path)
