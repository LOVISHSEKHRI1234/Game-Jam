"""Generate the Cosmos theme from the original art.

Copies assets/sprites -> assets/themes/cosmos/sprites, then recolors the
tilesets, objects and menu background into a space palette. The original
assets are never modified, so the theme can be regenerated or switched off
(THEME in config/settings.py).

Usage:
    .venv/bin/python tools/make_cosmos_theme.py
"""
import os
import shutil
import sys
import zlib

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cosmos_palette import remap  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets')
DST = os.path.join(ROOT, 'assets', 'themes', 'cosmos')

# (path relative to sprites/, green mode, star density per green pixel)
RECOLOR = [
    ('tilesets/plains.png', 'ground', 0.006),
    ('tilesets/decor_16x16.png', 'ground', 0.008),
    ('tilesets/decor_8x8.png', 'ground', 0.008),
    ('tilesets/objects.png', 'flora', 0.0),
    ('objects/objects.png', 'flora', 0.0),
    ('tilesets/fences.png', 'flora', 0.0),
    ('tilesets/walls/walls.png', 'ground', 0.0),
    ('tilesets/walls/wooden_door.png', 'ground', 0.0),
    ('tilesets/walls/wooden_door_b.png', 'ground', 0.0),
    ('tilesets/floors/wooden.png', 'ground', 0.0),
    ('tilesets/floors/flooring.png', 'ground', 0.0),
] + [(f'objects/rock_in_water_0{i}.png', 'ground', 0.0) for i in range(1, 7)] + [
    ('objects/rock_in_water_01-sheet.png', 'ground', 0.0),
]

# Logo colours drawn onto the menu background; kept untouched.
LOGO_COLORS = [(246, 228, 170), (226, 166, 86), (40, 24, 16), (20, 12, 8)]


def load_rgba(path):
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if im.ndim == 2:
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGRA)
    elif im.shape[2] == 3:
        im = cv2.cvtColor(im, cv2.COLOR_BGR2BGRA)
    return cv2.cvtColor(im, cv2.COLOR_BGRA2RGBA)


def save_rgba(path, rgba):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cv2.imwrite(path, cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA))


def make_grass_tile(src, dst):
    """The base ground tile repeats everywhere, so give it just two faint stars."""
    out = remap(load_rgba(src), 'ground')
    out[3, 11, :3] = (200, 205, 255)
    out[12, 4, :3] = (150, 160, 230)
    save_rgba(dst, out)


def make_menu_background(src, dst):
    a = load_rgba(src)
    logo = np.zeros(a.shape[:2], bool)
    for c in LOGO_COLORS:
        logo |= np.all(a[..., :3] == c, axis=-1)
    out = remap(a, 'ground', seed=7, stars=0.004)
    out[logo] = a[logo]
    # a few brighter 2x2 stars for depth
    rng = np.random.default_rng(11)
    hsv = cv2.cvtColor(np.ascontiguousarray(out[..., :3]), cv2.COLOR_RGB2HSV)
    dark = (hsv[..., 2] < 90) & ~logo
    ys, xs = np.nonzero(dark[:-1, :-1])
    for i in rng.choice(len(ys), size=min(140, len(ys)), replace=False):
        y, x = ys[i], xs[i]
        out[y:y + 2, x:x + 2, :3] = (235, 240, 255)
    save_rgba(dst, out)


def main():
    dst_sprites = os.path.join(DST, 'sprites')
    if os.path.isdir(dst_sprites):
        shutil.rmtree(dst_sprites)
    shutil.copytree(os.path.join(SRC, 'sprites'), dst_sprites)

    for rel, mode, stars in RECOLOR:
        src = os.path.join(SRC, 'sprites', rel)
        if not os.path.exists(src):
            print(f'skip (missing): {rel}')
            continue
        save_rgba(os.path.join(dst_sprites, rel),
                  remap(load_rgba(src), mode, seed=zlib.crc32(rel.encode()), stars=stars))
        print(f'recolored: {rel}')

    make_grass_tile(os.path.join(SRC, 'sprites', 'tilesets', 'grass.png'),
                    os.path.join(dst_sprites, 'tilesets', 'grass.png'))
    make_menu_background(os.path.join(SRC, 'home_page.png'),
                         os.path.join(DST, 'home_page.png'))
    print('done ->', os.path.relpath(DST, ROOT))


if __name__ == '__main__':
    main()
