#!/usr/bin/env python3
"""Renders panel_bg.png: black brushed-metal panel with narrow walnut end cheeks (Moog Labyrinth look).
Needs only Pillow: docker run --rm -v "$PWD":/w -w /w mpc-vst-html-art python3 images/make_panel_bg.py"""
import random
from PIL import Image, ImageChops, ImageFilter, ImageOps

W, H, CHEEK = 1280, 628, 22
random.seed(7)


def streaks(w, h, sx, sy, sigma=70):
    """Noise stretched sx (across) / sy (down): brushed grain."""
    n = Image.effect_noise((max(1, w // sx), max(1, h // sy)), sigma)
    return n.resize((w, h), Image.BICUBIC)


# ---- brushed black metal: horizontal streaks at three scales + fine grain ----
g = streaks(W, H, 40, 1, 80)
g = ImageChops.add(ImageChops.multiply(g, Image.new("L", (W, H), 150)), ImageChops.multiply(streaks(W, H, 12, 1, 80), Image.new("L", (W, H), 105)), scale=1.0)
g = Image.blend(g, Image.effect_noise((W, H), 40), 0.18)
g = ImageOps.autocontrast(g, cutoff=1)
panel = ImageOps.colorize(g, black=(9, 9, 11), white=(38, 39, 42))
# soft anodised sheen: a little lighter toward the top and the middle, darker at the edges
sheen = Image.linear_gradient("L").resize((W, H))                       # black top -> white bottom
sheen = ImageOps.invert(sheen).point(lambda v: v // 7)
vign = Image.linear_gradient("L").rotate(90).resize((W, H))
vign = ImageChops.multiply(vign, ImageOps.mirror(vign)).point(lambda v: v // 9)
panel = ImageChops.add(panel, Image.merge("RGB", [ImageChops.add(sheen, vign)] * 3))

# ---- walnut cheeks: vertical grain, darker figure lines, bevel ----
def cheek(flip):
    w = CHEEK
    base = streaks(w, H, 1, 60, 90)
    fig = streaks(w, H, 3, 14, 70)
    base = ImageOps.autocontrast(Image.blend(base, fig, 0.45), cutoff=1)
    wood = ImageOps.colorize(base, black=(52, 26, 14), white=(132, 78, 46), mid=(92, 52, 30))
    # bevel: bright rim on the outer edge, shadow toward the panel
    ramp = Image.linear_gradient("L").rotate(90).resize((w, H))          # white left -> black right
    shade = ramp.point(lambda v: int(40 * (v / 255.0) ** 2) - 0)
    dark = ImageOps.invert(ramp).point(lambda v: int(70 * (v / 255.0) ** 4))
    wood = ImageChops.add(wood, Image.merge("RGB", [shade] * 3))
    wood = ImageChops.subtract(wood, Image.merge("RGB", [dark] * 3))
    return ImageOps.mirror(wood) if flip else wood


out = panel.copy()
out.paste(cheek(False), (0, 0))
out.paste(cheek(True), (W - CHEEK, 0))
# shadow the cheeks cast on the panel, and a thin dark seam
sh = Image.new("L", (W, H), 0)
for x in range(10):
    v = int(120 * (1 - x / 10.0) ** 2)
    for xx in (CHEEK + x, W - CHEEK - 1 - x):
        sh.paste(v, (xx, 0, xx + 1, H))
out = ImageChops.subtract(out, Image.merge("RGB", [sh] * 3))
out.save("images/panel_bg.png")
print("images/panel_bg.png", out.size)
