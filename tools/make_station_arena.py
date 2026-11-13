"""Generate the Cosmos space-station arena.

Outputs:
  assets/themes/cosmos/sprites/tilesets/station.png   (procedural pixel-art tiles)
  data/survival_arena_cosmos.json                      (arena map using them)

The map is derived from data/survival_arena.json so walls, openings, pillars
and spawn points stay identical; only the art changes. Grass outside the walls
becomes open space (transparent, with invisible collision) so the starfield
shows through.

Usage:
    .venv/bin/python tools/make_station_arena.py
"""
import json
import os
import random

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
import pygame  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TILESET_OUT = os.path.join(ROOT, 'assets', 'themes', 'cosmos', 'sprites', 'tilesets', 'station.png')
MAP_IN = os.path.join(ROOT, 'data', 'survival_arena.json')
MAP_OUT = os.path.join(ROOT, 'data', 'survival_arena_cosmos.json')

T = 16
# Palette
STEEL = (46, 50, 72)
STEEL_B = (42, 45, 66)
STEEL_HI = (72, 78, 106)
STEEL_LO = (28, 30, 46)
RIVET = (96, 102, 136)
SLOT = (16, 18, 28)
CYAN = (80, 225, 255)
CYAN_DIM = (40, 120, 150)
WALL_FACE = (30, 32, 48)
WALL_TOP = (60, 64, 92)
MAG_D, MAG, MAG_L, MAG_OUT = (140, 40, 165), (225, 90, 235), (255, 190, 255), (34, 10, 44)


def px(s, x, y, c):
    s.set_at((x, y), c)


def plate(s, ox, oy, base=STEEL, rivets=True):
    pygame.draw.rect(s, base, (ox, oy, T, T))
    pygame.draw.line(s, STEEL_HI, (ox, oy), (ox + T - 1, oy))
    pygame.draw.line(s, STEEL_HI, (ox, oy), (ox, oy + T - 1))
    pygame.draw.line(s, STEEL_LO, (ox, oy + T - 1), (ox + T - 1, oy + T - 1))
    pygame.draw.line(s, STEEL_LO, (ox + T - 1, oy), (ox + T - 1, oy + T - 1))
    if rivets:
        for rx, ry in [(2, 2), (13, 2), (2, 13), (13, 13)]:
            px(s, ox + rx, oy + ry, RIVET)
            px(s, ox + rx + 1, oy + ry + 1, STEEL_LO)


def plate_b(s, ox, oy):
    plate(s, ox, oy, STEEL_B)
    # panel seam + scuffs
    pygame.draw.line(s, STEEL_LO, (ox + 1, oy + 8), (ox + 14, oy + 8))
    pygame.draw.line(s, STEEL_HI, (ox + 1, oy + 9), (ox + 14, oy + 9))
    for x, y in [(5, 4), (6, 5), (10, 11), (11, 12)]:
        px(s, ox + x, oy + y, (54, 58, 82))


def vent(s, ox, oy):
    plate(s, ox, oy, rivets=False)
    for i in range(4):
        y = oy + 3 + i * 3
        pygame.draw.line(s, SLOT, (ox + 3, y), (ox + 12, y))
        pygame.draw.line(s, CYAN_DIM, (ox + 5, y), (ox + 10, y))


def corridor(s, ox, oy):
    plate(s, ox, oy, rivets=False)
    pygame.draw.line(s, STEEL_LO, (ox + 3, oy), (ox + 3, oy + T - 1))
    pygame.draw.line(s, STEEL_LO, (ox + 12, oy), (ox + 12, oy + T - 1))
    for y in (3, 11):
        pygame.draw.rect(s, CYAN_DIM, (ox + 6, oy + y - 1, 4, 3))
        pygame.draw.rect(s, CYAN, (ox + 7, oy + y, 2, 1))


def wall(s, ox, oy):
    pygame.draw.rect(s, WALL_FACE, (ox, oy, T, T))
    pygame.draw.rect(s, WALL_TOP, (ox, oy, T, 6))
    pygame.draw.line(s, STEEL_HI, (ox, oy), (ox + T - 1, oy))
    pygame.draw.line(s, STEEL_LO, (ox, oy + 6), (ox + T - 1, oy + 6))
    pygame.draw.rect(s, CYAN_DIM, (ox, oy + 9, T, 3))
    pygame.draw.line(s, CYAN, (ox, oy + 10), (ox + T - 1, oy + 10))
    pygame.draw.line(s, (12, 12, 20), (ox, oy + T - 1), (ox + T - 1, oy + T - 1))
    px(s, ox + 2, oy + 3, RIVET)
    px(s, ox + 13, oy + 3, RIVET)


def trim(s, ox, oy, sides):
    """Floor plate with a glowing edge on the given sides ('t','b','l','r')."""
    plate(s, ox, oy)
    for side in sides:
        if side == 't':
            pygame.draw.rect(s, STEEL_LO, (ox, oy, T, 2)); pygame.draw.line(s, CYAN, (ox, oy + 2), (ox + T - 1, oy + 2))
        if side == 'b':
            pygame.draw.rect(s, STEEL_LO, (ox, oy + T - 2, T, 2)); pygame.draw.line(s, CYAN, (ox, oy + T - 3), (ox + T - 1, oy + T - 3))
        if side == 'l':
            pygame.draw.rect(s, STEEL_LO, (ox, oy, 2, T)); pygame.draw.line(s, CYAN, (ox + 2, oy), (ox + 2, oy + T - 1))
        if side == 'r':
            pygame.draw.rect(s, STEEL_LO, (ox + T - 2, oy, 2, T)); pygame.draw.line(s, CYAN, (ox + T - 3, oy), (ox + T - 3, oy + T - 1))


def crystal(s, ox, oy):
    # pedestal
    pygame.draw.rect(s, STEEL_LO, (ox + 3, oy + 12, 10, 4))
    pygame.draw.rect(s, WALL_TOP, (ox + 4, oy + 12, 8, 2))
    pygame.draw.line(s, CYAN, (ox + 5, oy + 14), (ox + 10, oy + 14))
    # crystal shards (outline, then fills)
    shards = [
        [(8, 0), (11, 5), (10, 12), (6, 12), (5, 5)],
        [(4, 4), (6, 8), (6, 12), (3, 12), (2, 8)],
        [(12, 5), (14, 9), (13, 12), (10, 12), (10, 9)],
    ]
    for pts in shards:
        pygame.draw.polygon(s, MAG_OUT, [(ox + x, oy + y) for x, y in pts], 0)
    for pts in shards:
        inner = [(ox + x + (0.5 if x < 8 else -0.5), oy + y + 0.7) for x, y in pts]
        pygame.draw.polygon(s, MAG, inner, 0)
    pygame.draw.line(s, MAG_L, (ox + 8, oy + 2), (ox + 7, oy + 10))
    pygame.draw.line(s, MAG_D, (ox + 9, oy + 4), (ox + 9, oy + 11))
    px(s, ox + 3, oy + 7, MAG_L)
    px(s, ox + 12, oy + 7, MAG_L)


def build_tileset():
    sheet = pygame.Surface((8 * T, 5 * T), pygame.SRCALPHA)
    plate(sheet, 0 * T, 0)           # (0,0) plate A
    plate_b(sheet, 1 * T, 0)         # (1,0) plate B
    vent(sheet, 2 * T, 0)            # (2,0) vent
    corridor(sheet, 3 * T, 0)        # (3,0) docking bridge
    # (4,0) void: left transparent (invisible collision)
    tmp = pygame.Surface((T, T), pygame.SRCALPHA)
    corridor(tmp, 0, 0)
    sheet.blit(pygame.transform.rotate(tmp, 90), (5 * T, 0))  # (5,0) horizontal bridge
    wall(sheet, 0, T)                # (0,1) bulkhead wall
    crystal(sheet, T, T)             # (1,1) energy crystal (ysort)
    sides = {(0, 0): 'tl', (1, 0): 't', (2, 0): 'tr',
             (0, 1): 'l', (1, 1): '', (2, 1): 'r',
             (0, 2): 'bl', (1, 2): 'b', (2, 2): 'br'}
    for (c, r), sd in sides.items():  # rows 2-4: trimmed border 3x3
        trim(sheet, c * T, (2 + r) * T, sd)
    os.makedirs(os.path.dirname(TILESET_OUT), exist_ok=True)
    pygame.image.save(sheet, TILESET_OUT)


def build_map():
    src = json.load(open(MAP_IN))
    w, h = src['width'], src['height']
    ground = [row.split() for row in src['layers']['ground']['grid']]
    objects = [row.split() for row in src['layers']['objects']['grid']]

    # Arena interior bounds = extent of the trimmed dirt rectangle
    xs = [x for y in range(h) for x in range(w) if ground[y][x] == 'Dtl']
    ys = [y for y in range(h) for x in range(w) if ground[y][x] == 'Dtl']
    x0, y0 = xs[0], ys[0]
    x1 = max(x for y in range(h) for x in range(w) if ground[y][x] == 'Dbr')
    y1 = max(y for y in range(h) for x in range(w) if ground[y][x] == 'Dbr')

    edge = {'Dtl': 'Ttl', 'Dt': 'Tt', 'Dtr': 'Ttr', 'Dl': 'Tl', 'Dr': 'Tr',
            'Dbl': 'Tbl', 'Db': 'Tb', 'Dbr': 'Tbr'}
    rng = random.Random(3)
    g_out, o_out = [], []
    for y in range(h):
        grow, orow = [], []
        for x in range(w):
            t = ground[y][x]
            inside = x0 <= x <= x1 and y0 <= y <= y1
            if t == 'G':
                grow.append('.')
                orow.append('V')              # open space: invisible collision
                continue
            out_dirs = {'Dt': (0, -1), 'Db': (0, 1), 'Dl': (-1, 0), 'Dr': (1, 0)}
            if t in out_dirs:
                dx, dy = out_dirs[t]
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and ground[ny][nx] == 'Dc':
                    grow.append('A')          # opening: no trim across the doorway
                    orow.append('.')
                    continue
            if t in edge:
                grow.append(edge[t])
            elif t == 'Dc' and not inside:
                grow.append('R' if x0 <= x <= x1 else 'H')  # docking bridge
            else:
                r = rng.random()
                grow.append('X' if r < 0.04 else ('B' if (x + y) % 2 else 'A'))
            orow.append('W' if objects[y][x] == 'W' else '.')
        g_out.append(' '.join(grow))
        o_out.append(' '.join(orow))

    ysort = [dict(t, tileset='station', col=1, row=1) for t in src['layers']['ysort']['tiles']]

    out = {
        'name': 'survival_arena_cosmos',
        'width': w, 'height': h, 'tile_size': src['tile_size'],
        'tile_defs': {
            'A': ['station', 0, 0], 'B': ['station', 1, 0], 'X': ['station', 2, 0],
            'R': ['station', 3, 0], 'H': ['station', 5, 0], 'V': ['station', 4, 0], 'W': ['station', 0, 1],
            'Ttl': ['station', 0, 2], 'Tt': ['station', 1, 2], 'Ttr': ['station', 2, 2],
            'Tl': ['station', 0, 3], 'Tr': ['station', 2, 3],
            'Tbl': ['station', 0, 4], 'Tb': ['station', 1, 4], 'Tbr': ['station', 2, 4],
        },
        'layers': {
            'ground': {'grid': g_out},
            'objects': {'grid': o_out},
            'ysort': {'tiles': ysort},
        },
        'spawn_points': src['spawn_points'],
    }
    with open(MAP_OUT, 'w') as f:
        json.dump(out, f, indent=2)


if __name__ == '__main__':
    pygame.init()
    build_tileset()
    build_map()
    print('wrote', os.path.relpath(TILESET_OUT, ROOT), 'and', os.path.relpath(MAP_OUT, ROOT))
