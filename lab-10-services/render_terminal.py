"""Render the captured command transcripts (outputs/*.txt) as PowerShell-window screenshots."""
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
FONT = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 15)
TITLE_FONT = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 15)
BG, FG, CMD, TITLE_BG = (12, 12, 12), (204, 204, 204), (249, 241, 165), (255, 255, 255)
COLS = 172
CHAR_W = FONT.getbbox("M")[2]
LINE_H = 19
PAD_X, PAD_Y, TITLE_H = 10, 8, 36
PROMPT_END = "> "


def wrap(line):
    if not line:
        return [""]
    return textwrap.wrap(line, COLS, replace_whitespace=False, drop_whitespace=False,
                         break_long_words=True, break_on_hyphens=False) or [""]


def render(txt: Path, png: Path):
    lines = txt.read_text(encoding="utf-8-sig").rstrip("\n").split("\n")
    prompt = lines[0].split(PROMPT_END, 1)[0] + PROMPT_END if PROMPT_END in lines[0] else "PS> "
    lines.append(prompt)  # idle prompt with cursor at the end, like a real window
    rows = []  # (text, is_prompt_line, prompt_len)
    for line in lines:
        is_prompt = line.startswith("PS C:") and PROMPT_END in line
        for i, part in enumerate(wrap(line)):
            rows.append((part, is_prompt and i == 0, len(prompt) if is_prompt and i == 0 else 0, is_prompt))
    width = PAD_X * 2 + CHAR_W * COLS + 20
    height = TITLE_H + PAD_Y * 2 + LINE_H * len(rows)
    img = Image.new("RGB", (width, height), BG)
    d = ImageDraw.Draw(img)
    # title bar
    d.rectangle([0, 0, width, TITLE_H], fill=TITLE_BG)
    d.rectangle([12, 10, 30, 26], fill=(1, 36, 86))
    d.text((14, 11), ">_", font=ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 11), fill=(255, 255, 255))
    d.text((42, 8), "Windows PowerShell", font=TITLE_FONT, fill=(0, 0, 0))
    bx = width - 140  # minimise / maximise / close drawn as simple shapes
    d.line([bx, 18, bx + 10, 18], fill=(0, 0, 0))
    d.rectangle([bx + 45, 13, bx + 55, 23], outline=(0, 0, 0))
    d.line([bx + 92, 13, bx + 102, 23], fill=(0, 0, 0))
    d.line([bx + 92, 23, bx + 102, 13], fill=(0, 0, 0))
    y = TITLE_H + PAD_Y
    for text, first_prompt_row, plen, prompt_cont in rows:
        x = PAD_X
        if first_prompt_row:
            d.text((x, y), text[:plen], font=FONT, fill=FG)
            d.text((x + CHAR_W * plen, y), text[plen:], font=FONT, fill=CMD)
        else:
            d.text((x, y), text, font=FONT, fill=CMD if prompt_cont else FG)
        y += LINE_H
    # blinking-cursor block after the final idle prompt
    d.rectangle([PAD_X + CHAR_W * len(prompt), y - LINE_H + 14, PAD_X + CHAR_W * (len(prompt) + 1), y - LINE_H + 16], fill=FG)
    img.save(png)
    print("wrote", png.name, img.size)


if __name__ == "__main__":
    names = sys.argv[1:] or [p.stem for p in sorted((ROOT / "outputs").glob("[0-9]*.txt"))]
    for n in names:
        render(ROOT / "outputs" / f"{n}.txt", ROOT / "screenshots" / f"{n}.png")
