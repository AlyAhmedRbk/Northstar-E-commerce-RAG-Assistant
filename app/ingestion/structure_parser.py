import re


def parse_document_structure(text: str) -> list[dict]:
    paragraphs = re.split(r"\n\s*\n", text)

    sections = []
    current_heading = "General Content"

    for paragraph in paragraphs:
        content = paragraph.strip()

        if not content:
            continue

        lines = content.splitlines()
        first_line = lines[0].strip()

        is_heading = (
            len(lines) == 1
            and len(first_line) <= 120
            and (
                first_line.endswith(":")
                or first_line.isupper()
                or first_line.lower().startswith(
                    ("section ", "chapter ", "category ")
                )
            )
        )

        if is_heading:
            current_heading = first_line.rstrip(":")
            continue

        sections.append({
            "section": current_heading,
            "content": content,
        })

    return sections
