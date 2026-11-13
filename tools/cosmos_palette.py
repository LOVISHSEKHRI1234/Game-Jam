"""Pixel-art palette remap used to generate the Cosmos theme.

Works on RGBA numpy arrays (H, W, 4). Hue classes (OpenCV H is 0-180):
  green  -> 'ground' (dark indigo) or 'flora' (glowing teal)
  brown  -> moon dust (pale blue-grey)
  blue   -> slate / asteroid rock
  red    -> magenta glow
"""
import cv2
import numpy as np


def remap(rgba: np.ndarray, green_mode: str = "ground", seed: int = 0,
          stars: float = 0.0) -> np.ndarray:
    out = rgba.copy()
    rgb = np.ascontiguousarray(rgba[..., :3])
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    nh, ns, nv = h.copy(), s.copy(), v.copy()

    green = (h >= 33) & (h <= 95) & (s > 35)
    brown = (h >= 5) & (h < 33) & (s > 45)
    blue = (h > 95) & (h <= 135) & (s > 20)
    red = ((h < 5) | (h > 160)) & (s > 90) & (v > 90)

    if green_mode == "ground":
        nh[green] = 128 + (h[green] - 60) * 0.25      # indigo / violet
        ns[green] = np.clip(s[green] * 0.9, 0, 255)
        nv[green] = v[green] * 0.55
    else:  # flora: glowing teal crystals
        nh[green] = 88 + (h[green] - 60) * 0.25
        ns[green] = np.clip(s[green] * 1.15, 0, 255)
        nv[green] = np.clip(v[green] * 1.1, 0, 255)

    nh[brown] = 124                                    # lavender moon dust
    ns[brown] = s[brown] * 0.18 + 18
    nv[brown] = np.clip(v[brown] * 0.72 + 12, 0, 255)
    # regolith speckle so large dirt areas aren't flat
    rng_d = np.random.default_rng(seed + 1)
    noise = rng_d.random(h.shape)
    nv[brown & (noise < 0.05)] -= 22
    nv[brown & (noise > 0.97)] += 20

    nh[blue] = 122 + (h[blue] - 110) * 0.3            # slate, slightly violet
    ns[blue] = np.clip(s[blue] * 0.8, 0, 255)
    nv[blue] = v[blue] * 0.85

    nh[red] = 152                                      # magenta glow
    ns[red] = 200
    nv[red] = 255

    hsv2 = np.stack([nh, ns, nv], -1).clip(0, 255).astype(np.uint8)
    out[..., :3] = cv2.cvtColor(hsv2, cv2.COLOR_HSV2RGB)

    if stars > 0:
        rng = np.random.default_rng(seed)
        cand = green & (rgba[..., 3] > 0)
        pick = cand & (rng.random(cand.shape) < stars)
        colors = np.array([[255, 255, 255], [190, 220, 255], [255, 210, 250]], np.uint8)
        idx = rng.integers(0, len(colors), pick.sum())
        out[..., :3][pick] = colors[idx]
    return out
