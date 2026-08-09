from pathlib import Path
import re

from docx import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "MEE610_lista_exercicios_transcal.docx"


# Ordem crescente de dificuldade, avaliada pelo número de balanços, mecanismos,
# geometrias, incógnitas acopladas e necessidade de iteração/interpretação.
ORDER = {
    1: ["1.1", "1.2", "1.3", "1.5", "1.4"],
    2: ["2.6", "2.9", "2.4", "2.1", "2.8", "2.2", "2.7", "2.3", "2.5"],
    3: ["3.4", "3.6", "3.2", "3.10", "3.5", "3.8", "3.9", "3.1", "3.7", "3.3"],
    4: ["4.3", "4.2", "4.8", "4.4", "4.1", "4.7", "4.11", "4.6", "4.10", "4.9", "4.14", "4.5", "4.13", "4.15", "4.12"],
    5: ["5.3", "5.8", "5.1", "5.6", "5.4", "5.9", "5.7", "5.5", "5.10", "5.13", "5.2", "5.11", "5.12", "5.14", "5.15"],
    6: ["6.10", "6.4", "6.8", "6.9", "6.1", "6.3", "6.6", "6.12", "6.14", "6.15", "6.11", "6.2", "6.5", "6.7", "6.13"],
}

LEVELS = {
    1: [2, 2, 1],
    2: [3, 4, 2],
    3: [4, 3, 3],
    4: [5, 6, 4],
    5: [3, 7, 5],
    6: [5, 6, 4],
}


def text_of(element) -> str:
    return "".join(element.itertext()).strip()


def replace_number(paragraph, replacement: str) -> None:
    match = re.match(r"^(\d+\.\d+)", paragraph.text)
    if not match:
        raise RuntimeError(f"Número não encontrado: {paragraph.text[:80]}")
    remaining = match.group(1)
    inserted = False
    for run in paragraph.runs:
        if not remaining:
            return
        if not run.text:
            continue
        take = min(len(run.text), len(remaining))
        if run.text[:take] != remaining[:take]:
            raise RuntimeError(f"Numeração fragmentada inesperadamente: {paragraph.text[:80]}")
        run.text = (replacement if not inserted else "") + run.text[take:]
        inserted = True
        remaining = remaining[take:]
    if remaining:
        raise RuntimeError(f"Não foi possível substituir: {paragraph.text[:80]}")


def difficulty_labels(section: int) -> list[str]:
    basic, intermediate, advanced = LEVELS[section]
    return ["Básico"] * basic + ["Intermediário"] * intermediate + ["Avançado"] * advanced


def main() -> None:
    doc = Document(PATH)
    body = doc._element.body

    for section in range(1, 7):
        children = list(body)
        heading_index = next(
            index
            for index, child in enumerate(children)
            if child.tag == qn("w:p") and re.match(rf"^\[{section}\]\s*[–-]", text_of(child))
        )
        next_heading_index = next(
            (
                index
                for index in range(heading_index + 1, len(children))
                if children[index].tag == qn("w:p")
                and re.match(r"^\[[1-6]\]\s*[–-]", text_of(children[index]))
            ),
            next((i for i, child in enumerate(children) if child.tag == qn("w:sectPr")), len(children)),
        )

        starts = []
        for index in range(heading_index + 1, next_heading_index):
            child = children[index]
            if child.tag != qn("w:p"):
                continue
            match = re.match(r"^(\d+\.\d+)\s*[–-]", text_of(child))
            if match:
                starts.append((index, match.group(1)))

        blocks = {}
        for position, (start, exercise_id) in enumerate(starts):
            end = starts[position + 1][0] if position + 1 < len(starts) else next_heading_index
            blocks[exercise_id] = children[start:end]

        expected = set(ORDER[section])
        if set(blocks) != expected:
            raise RuntimeError(
                f"Seção {section}: exercícios atuais {sorted(blocks)} não correspondem ao plano {sorted(expected)}"
            )

        first_exercise = starts[0][0]
        insertion_point = children[first_exercise - 1]
        for index in range(first_exercise, next_heading_index):
            body.remove(children[index])

        labels = difficulty_labels(section)
        for sequence, exercise_id in enumerate(ORDER[section], start=1):
            block = blocks[exercise_id]
            paragraph = Paragraph(block[0], body)
            replace_number(paragraph, f"{section}.{sequence} [{labels[sequence - 1]}]")
            for element in block:
                insertion_point.addnext(element)
                insertion_point = element

    doc.core_properties.comments = (
        "Exercícios ordenados por dificuldade crescente em cada seção: "
        "Básico, Intermediário e Avançado."
    )
    doc.save(PATH)
    print(PATH)


if __name__ == "__main__":
    main()
