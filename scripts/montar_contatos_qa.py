from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "qa_final"
pages = sorted(QA.glob("page-*.png"), key=lambda p: int(p.stem.split("-")[-1]))

for group_index in range(0, len(pages), 6):
    group = pages[group_index:group_index + 6]
    sheet = Image.new("RGB", (1500, 1950), "#d8d8d8")
    draw = ImageDraw.Draw(sheet)
    for slot, path in enumerate(group):
        image = Image.open(path).convert("RGB")
        image.thumbnail((475, 900))
        x = 20 + (slot % 3) * 495
        y = 35 + (slot // 3) * 955
        sheet.paste(image, (x, y))
        draw.text((x, 10 + (slot // 3) * 955), f"Página {int(path.stem.split('-')[-1])}", fill="black")
    sheet.save(QA / f"contato-{group_index // 6 + 1}.png")
