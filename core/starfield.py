"""Parallax starfield drawn behind the tilemap (visible past the map edges)."""
import math
import random

import pygame

SPACE_COLOR = (8, 6, 22)
_TILE = 512
_layers = None


def _build_layers():
    rng = random.Random(42)
    layers = []
    # (star count, colours, size, parallax factor)
    for count, colors, size, factor in [
        (140, [(90, 90, 140), (70, 80, 130)], 1, 0.15),
        (60, [(200, 210, 255), (255, 220, 250)], 2, 0.3),
        (12, [(255, 255, 255)], 3, 0.5),
    ]:
        surf = pygame.Surface((_TILE, _TILE), pygame.SRCALPHA)
        for _ in range(count):
            x, y = rng.randrange(_TILE), rng.randrange(_TILE)
            pygame.draw.rect(surf, rng.choice(colors), (x, y, size, size))
        layers.append((surf, factor))
    return layers


def draw_starfield(screen: pygame.Surface, cam_x: float = 0.0, cam_y: float = 0.0):
    """Fill the screen with deep space and tiled parallax star layers."""
    global _layers
    if _layers is None:
        _layers = _build_layers()
    screen.fill(SPACE_COLOR)
    w, h = screen.get_size()
    for surf, factor in _layers:
        ox = -int(cam_x * factor) % _TILE
        oy = -int(cam_y * factor) % _TILE
        for ty in range(-1, math.ceil(h / _TILE) + 1):
            for tx in range(-1, math.ceil(w / _TILE) + 1):
                screen.blit(surf, (tx * _TILE + ox, ty * _TILE + oy))
