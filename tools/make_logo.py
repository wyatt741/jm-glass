#!/usr/bin/env python3
"""Knock the opaque white background out of the J&M wordmark, and build a
reversed variant for dark surfaces.

The source (assets/src/jmglass-main-horz-logo_1.png, 1567x187, RGB) has no
alpha at all. A global "white -> transparent" would be wrong: the mark itself
contains white, the mullion cross on the red half and the diagonal hatching on
the grey half, and a global rule punches holes straight through the logo. So
the background is found by flood-filling inward from the border and only that
connected region is cleared.

The reversed variant maps the near-black wordmark to the light ink colour while
leaving the red pane untouched, because the accent is the one element that must
read the same on both themes.

    python3 tools/make_logo.py
"""
from collections import deque
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "src" / "jmglass-main-horz-logo_1.png"
OUT_DIR = ROOT / "assets"

WHITE_MIN = 236          # a pixel this bright on every channel counts as paper
LIGHT_INK = (242, 242, 242)   # matches --ink on the dark theme


def background_mask(rgb):
    """Pixels reachable from the border through near-white only."""
    w, h = rgb.size
    px = rgb.load()
    seen = bytearray(w * h)

    def paper(x, y):
        r, g, b = px[x, y][:3]
        return r >= WHITE_MIN and g >= WHITE_MIN and b >= WHITE_MIN

    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if not seen[y * w + x] and paper(x, y):
                seen[y * w + x] = 1
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if not seen[y * w + x] and paper(x, y):
                seen[y * w + x] = 1
                q.append((x, y))

    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx] and paper(nx, ny):
                seen[ny * w + nx] = 1
                q.append((nx, ny))
    return seen


def is_red(r, g, b):
    """The brand red, kept as-is in the reversed variant."""
    return r > 110 and r - g > 45 and r - b > 45


def main():
    rgb = Image.open(SRC).convert("RGB")
    w, h = rgb.size
    seen = background_mask(rgb)

    out = rgb.convert("RGBA")
    px = out.load()
    cleared = 0
    for y in range(h):
        row = y * w
        for x in range(w):
            if seen[row + x]:
                px[x, y] = (255, 255, 255, 0)
                cleared += 1
    out.save(OUT_DIR / "logo.png")

    rev = out.copy()
    rpx = rev.load()
    recoloured = 0
    for y in range(h):
        row = y * w
        for x in range(w):
            if seen[row + x]:
                continue
            r, g, b, a = rpx[x, y]
            if a == 0 or is_red(r, g, b):
                continue
            # map the dark wordmark up to light ink, leave mid greys alone-ish
            lum = (r * 299 + g * 587 + b * 114) // 1000
            if lum < 200:
                t = 1 - (lum / 200)
                rpx[x, y] = tuple(
                    int(c + (li - c) * t) for c, li in zip((r, g, b), LIGHT_INK)
                ) + (a,)
                recoloured += 1
    rev.save(OUT_DIR / "logo-reversed.png")

    print(f"source {w}x{h} RGB (no alpha)")
    print(f"logo.png          background cleared: {cleared} px "
          f"({cleared * 100 // (w * h)}% of frame)")
    print(f"logo-reversed.png ink recoloured:     {recoloured} px")


if __name__ == "__main__":
    main()
