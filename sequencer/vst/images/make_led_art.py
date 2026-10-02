#!/usr/bin/env python3
"""Renders the step LEDs (led_off.png, led_on.png: small red rectangles) and the running-light rings (run_0..8.png: a row of
8 positions with a red outline at step N, none for 0). Needs only Pillow:
docker run --rm -v "$PWD":/w -w /w mpc-vst-html-art python3 images/make_led_art.py"""
from PIL import Image, ImageDraw, ImageFilter

SS = 4   # supersample


def rect(size, w, h, fill, glow=None, hi=True):
    """A small rectangular LED (bezel, lens, highlight), centred on a size x size canvas."""
    im = Image.new("RGBA", (size * SS, size * SS), (0, 0, 0, 0))
    c = size * SS // 2
    if glow:
        g = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).rounded_rectangle([c - (w // 2 + 5) * SS, c - (h // 2 + 5) * SS, c + (w // 2 + 5) * SS, c + (h // 2 + 5) * SS], radius=5 * SS, fill=glow)
        im = Image.alpha_composite(im, g.filter(ImageFilter.GaussianBlur(5 * SS)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([c - (w // 2 + 2) * SS, c - (h // 2 + 2) * SS, c + (w // 2 + 2) * SS, c + (h // 2 + 2) * SS], radius=4 * SS, fill=(8, 8, 9, 255))   # bezel
    d.rounded_rectangle([c - w // 2 * SS, c - h // 2 * SS, c + w // 2 * SS, c + h // 2 * SS], radius=3 * SS, fill=fill)
    if hi:   # glass highlight along the top edge
        d.rounded_rectangle([c - w // 2 * SS + 3 * SS, c - h // 2 * SS + 2 * SS, c + w // 2 * SS - 3 * SS, c - h // 2 * SS + 5 * SS], radius=SS, fill=(255, 255, 255, 70))
    return im.resize((size, size), Image.LANCZOS)


S = 48
rect(S, 34, 20, (70, 14, 16, 255)).save("images/led_off.png")
rect(S, 34, 20, (255, 70, 60, 255), glow=(255, 60, 50, 170)).save("images/led_on.png")

W, H, STEP, X0 = 760, 60, 95, 40       # ring centre of step i: X0 + i*STEP, vertically centred
for n in range(9):
    im = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    if n:
        cx, cy = (X0 + (n - 1) * STEP) * SS, H * SS // 2
        box = [cx - 26 * SS, cy - 18 * SS, cx + 26 * SS, cy + 18 * SS]
        g = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).rounded_rectangle([b + (-4 if i < 2 else 4) * SS for i, b in enumerate(box)], radius=9 * SS, fill=(255, 70, 60, 150))
        im = Image.alpha_composite(im, g.filter(ImageFilter.GaussianBlur(6 * SS)))
        ImageDraw.Draw(im).rounded_rectangle(box, radius=7 * SS, outline=(255, 120, 105, 255), width=3 * SS)
    im.resize((W, H), Image.LANCZOS).save("images/run_%d.png" % n)
print("led + run art written")
