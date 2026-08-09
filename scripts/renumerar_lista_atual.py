from pathlib import Path
import re

from docx import Document


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "MEE610_lista_exercicios_transcal.docx"


def replace_number(paragraph, new_number: str) -> None:
    match = re.match(r"^(\d+\.\d+)(\s*[–-])", paragraph.text)
    if not match:
        return

    remaining = match.group(1)
    inserted = False
    for run in paragraph.runs:
        if not remaining:
            return
        if not run.text:
            continue
        take = min(len(run.text), len(remaining))
        if run.text[:take] != remaining[:take]:
            raise RuntimeError(f"Numeração fragmentada de forma inesperada: {paragraph.text[:80]}")
        run.text = (new_number if not inserted else "") + run.text[take:]
        inserted = True
        remaining = remaining[take:]

    if remaining:
        raise RuntimeError(f"Não foi possível renumerar: {paragraph.text[:80]}")


def main() -> None:
    doc = Document(PATH)
    current_section = None
    counts = {number: 0 for number in range(1, 7)}

    for paragraph in doc.paragraphs:
        heading = re.match(r"^\[([1-6])\]\s*[–-]", paragraph.text)
        if heading:
            current_section = int(heading.group(1))
            continue

        if current_section is None:
            continue

        if re.match(r"^\d+\.\d+\s*[–-]", paragraph.text):
            counts[current_section] += 1
            replace_number(paragraph, f"{current_section}.{counts[current_section]}")

    doc.save(PATH)
    print(PATH)
    print(counts)


if __name__ == "__main__":
    main()
