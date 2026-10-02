#!/usr/bin/env python3
"""Renders the step LEDs (led_off.png, led_on.png) and the running-light rings (run_0..8.png: a row of
8 positions with a ring at step N, none for 0). Needs only Pillow:
docker run --rm -v "$PWD":/w -w /w mpc-vst-html-art python3 images/make_led_art.py"""
from PIL import Image, ImageDraw, ImageFilter

SS = 4   # supersample


def disc(size, r, fill, glow=None, glow_r=0, hi=True):
    im = Image.new("RGBA", (size * SS, size * SS), (0, 0, 0, 0))
    c = size * SS // 2
    if glow:
        g = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([c - glow_r * SS, c - glow_r * SS, c + glow_r * SS, c + glow_r * SS], fill=glow)
        im = Image.alpha_composite(im, g.filter(ImageFilter.GaussianBlur(5 * SS)))
    d = ImageDraw.Draw(im)
    d.ellipse([c - (r + 2) * SS, c - (r + 2) * SS, c + (r + 2) * SS, c + (r + 2) * SS], fill=(8, 8, 9, 255))   # bezel
    d.ellipse([c - r * SS, c - r * SS, c + r * SS, c + r * SS], fill=fill)
    if hi:   # glass highlight
        d.ellipse([c - r * SS * 0.55, c - r * SS * 0.75, c + r * SS * 0.1, c - r * SS * 0.2], fill=(255, 255, 255, 70))
    return im.resize((size, size), Image.LANCZOS)


S = 48
disc(S, 15, (70, 14, 16, 255)).save("images/led_off.png")
disc(S, 15, (255, 70, 60, 255), glow=(255, 60, 50, 170), glow_r=19).save("images/led_on.png")

W, H, STEP, X0 = 760, 60, 95, 40       # ring centre of step i: X0 + i*STEP, vertically centred
for n in range(9):
    im = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    if n:
        cx, cy = (X0 + (n - 1) * STEP) * SS, H * SS // 2
        g = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([cx - 29 * SS, cy - 29 * SS, cx + 29 * SS, cy + 29 * SS], fill=(90, 255, 140, 150))
        im = Image.alpha_composite(im, g.filter(ImageFilter.GaussianBlur(6 * SS)))
        d = ImageDraw.Draw(im)
        d.ellipse([cx - 27 * SS, cy - 27 * SS, cx + 27 * SS, cy + 27 * SS], outline=(140, 255, 175, 255), width=3 * SS)
    im.resize((W, H), Image.LANCZOS).save("images/run_%d.png" % n)
print("led + run art written")
