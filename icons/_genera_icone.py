#!/usr/bin/env python3
"""
Generatore delle icone PWA e dell'immagine Open Graph per Cyber Hub.
Si esegue UNA volta in locale (richiede Pillow):  python3 icons/_genera_icone.py
Produce file PNG statici: nessuna dipendenza a runtime, nessun servizio esterno.
"""
from PIL import Image, ImageDraw, ImageFont

CYAN = (34, 211, 238, 255)
BG1  = (5, 7, 13, 255)
BG2  = (11, 19, 32, 255)
TXT  = (214, 230, 242, 255)
DIM  = (111, 129, 152, 255)

def shield(draw, cx, cy, w, h, stroke, width):
    """Disegna lo scudo (stesso simbolo del logo nell'header) + spunta."""
    top = cy - h / 2
    bot = cy + h / 2
    pts = [
        (cx,            top),
        (cx + w/2,      top + h*0.13),
        (cx + w/2,      top + h*0.52),
        (cx,            bot),
        (cx - w/2,      top + h*0.52),
        (cx - w/2,      top + h*0.13),
    ]
    draw.line(pts + [pts[0]], fill=stroke, width=width, joint="curve")
    # spunta (check)
    s = w
    draw.line(
        [(cx - s*0.22, cy + s*0.02),
         (cx - s*0.05, cy + s*0.20),
         (cx + s*0.26, cy - s*0.16)],
        fill=stroke, width=width, joint="curve")

def gradient_bg(size_w, size_h):
    img = Image.new("RGBA", (size_w, size_h), BG1)
    for y in range(size_h):
        t = y / max(1, size_h - 1)
        r = int(BG1[0] + (BG2[0]-BG1[0]) * t)
        g = int(BG1[1] + (BG2[1]-BG1[1]) * t)
        b = int(BG1[2] + (BG2[2]-BG1[2]) * t)
        for x in range(size_w):
            img.putpixel((x, y), (r, g, b, 255))
    return img

def make_icon(size, path, maskable=False, transparent_bg=False):
    SS = 4  # supersampling per bordi morbidi
    S = size * SS
    if transparent_bg:
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    else:
        img = Image.new("RGBA", (S, S), BG2)
        d0 = ImageDraw.Draw(img)
        # angoli arrotondati su sfondo pieno (non per maskable)
        if not maskable:
            mask = Image.new("L", (S, S), 0)
            ImageDraw.Draw(mask).rounded_rectangle([0, 0, S-1, S-1], radius=int(S*0.22), fill=255)
            bg = Image.new("RGBA", (S, S), BG2)
            img = Image.composite(bg, Image.new("RGBA", (S, S), (0,0,0,0)), mask)
    d = ImageDraw.Draw(img)
    # zona sicura: per le maskable lo scudo sta nel 66% centrale
    scale = 0.50 if maskable else 0.60
    sw = S * scale
    sh = S * scale * 1.12
    shield(d, S/2, S/2, sw, sh, CYAN, int(S*0.05))
    img = img.resize((size, size), Image.LANCZOS)
    img.save(path)
    print("scritto", path)

def load_font(size, bold=True):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            continue
    return ImageFont.load_default()

def make_og(path):
    W, H = 1200, 630
    img = gradient_bg(W, H)
    d = ImageDraw.Draw(img)
    # leggera griglia decorativa
    for x in range(0, W, 46):
        d.line([(x, 0), (x, H)], fill=(80, 200, 255, 12))
    for y in range(0, H, 46):
        d.line([(0, y), (W, y)], fill=(80, 200, 255, 12))
    # scudo a sinistra
    shield(d, 250, H/2, 230, 258, CYAN, 12)
    # testo
    f_big = load_font(82, bold=True)
    f_sub = load_font(30, bold=False)
    d.text((430, 235), "PEZZALIAPP", font=f_big, fill=TXT)
    d.text((430, 320), "CYBER HUB", font=f_big, fill=CYAN)
    d.text((432, 430), "Mappe live · formazione · analisi delle minacce", font=f_sub, fill=DIM)
    img.convert("RGB").save(path, quality=90)
    print("scritto", path)

if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    make_icon(192, os.path.join(here, "icon-192.png"))
    make_icon(512, os.path.join(here, "icon-512.png"))
    make_icon(512, os.path.join(here, "icon-maskable-512.png"), maskable=True)
    make_icon(180, os.path.join(here, "apple-touch-icon.png"))
    make_og(os.path.join(root, "og-image.png"))
    print("Fatto.")
