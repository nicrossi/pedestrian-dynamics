"""Improved visualisation for the AA‑CPM corridor simulation.

• Keeps true aspect ratio by using a single global scaling factor.
• Draws radii and arrows in proportion to physical size & speed.
• Automatically centres the corridor inside the window.
• Supports pausing with <space> and stepping with →/←.

Usage: python visualization.py <csv> [speed = 1.0]
The CSV is the one produced by CsvFrameWriter (columns: t,id,x,y,vx,vy,r).
"""
from __future__ import annotations

import csv
import math
import sys
import time
from pathlib import Path
from typing import Dict, Tuple
import pandas as pd
import pygame

# ── colour palette ────────────────────────────────────────────────────────────
BG_COLOR = (245, 245, 245)
TUNNEL_COLOR = (120, 120, 120)
ARROW_COLOR = (0, 102, 255)
C_L = (0x7f, 0xc9, 0x7f, 128)
C_L_MIN = (0x66, 0xc2, 0xa5)
C_R = (0xfd, 0xc0, 0x86, 128)
C_R_MIN = (0xfc, 0x8d, 0x62)
HC_R = (0xa6, 0x61, 0x1a)
HC_L = (0x01, 0x85, 0x71)
LABEL_COLOR = (40, 40, 40)

WINDOW_W, WINDOW_H = 1000, 500
PADDING = 40  # px frame around the corridor


def parse_csv(path: Path, chunk_size: int = 50_000) -> Dict:
    data: Dict = {"timesteps": {}}
    line_no = 1
    try:
        for chunk in pd.read_csv(
                path,
                chunksize=chunk_size,
                header=0,
                dtype={"id": str},
                names=["t", "id", "x", "y", "vx", "vy", "r", "goalSign"],
        ):
            for row in chunk.itertuples(index=False):
                line_no += 1
                try:
                    t = float(row.t)
                    pid = row.id
                    x, y = float(row.x), float(row.y)
                    vx, vy = float(row.vx), float(row.vy)
                    r = float(row.r)
                    gs = int(row.goalSign)
                except Exception as exc:
                    print(f"[CSV] malformed line {line_no}: {row} — {exc}", file=sys.stderr)
                    raise StopIteration

                frame = data["timesteps"].setdefault(t, {})
                frame[pid] = {"x": x, "y": y, "vx": vx, "vy": vy, "r": r, "gs": gs}
                data.setdefault("R_MAX", 0.35)
    except StopIteration:
        pass  # parsing stopped at first bad row

    if not data["timesteps"]:
        sys.exit("CSV contained no valid rows — exiting.")
    return data


def draw_arrow(surf, x, y, vx, vy, scale_px):
    """Draw velocity arrow; length = |v| * scale_px (1m/s = scale_px px)."""
    v_mag = math.hypot(vx, vy)
    if v_mag < 1e-3:
        return
    vx_n, vy_n = vx / v_mag, vy / v_mag
    length = v_mag * scale_px
    end_x = x + vx_n * length
    end_y = y - vy_n * length  # y axis inverted in screen coordinates
    pygame.draw.line(surf, ARROW_COLOR, (x, y), (end_x, end_y), 2)

    # arrow head
    head_size = 6
    angle = math.atan2(-(end_y - y), end_x - x)
    left = (end_x - head_size * math.cos(angle - math.pi / 6),
            end_y + head_size * math.sin(angle - math.pi / 6))
    right = (end_x - head_size * math.cos(angle + math.pi / 6),
             end_y + head_size * math.sin(angle + math.pi / 6))
    pygame.draw.polygon(surf, ARROW_COLOR, [(end_x, end_y), left, right])


def visualise(csv_path: Path, playback_speed: float = 1.0, dir_vector: bool = False):
    data = parse_csv(csv_path)
    times = sorted(data["timesteps"].keys())
    if len(times) < 2:
        raise ValueError("CSV must contain at least two timesteps")

    # corridor geometry
    xs = [p["x"] for frame in data["timesteps"].values() for p in frame.values()]
    ys = [p["y"] for frame in data["timesteps"].values() for p in frame.values()]
    L = 16
    W = 3.6
    R_MAX = 0.35

    # global uniform scale: 1m = SCALE px
    available_w = WINDOW_W - 2 * PADDING
    available_h = WINDOW_H - 2 * PADDING
    SCALE = min(available_w / L, available_h / W)

    x_off = (WINDOW_W - L * SCALE) / 2
    y_off = (WINDOW_H - W * SCALE) / 2

    def to_px(x_m: float, y_m: float) -> Tuple[int, int]:
        px = int(x_off + x_m * SCALE)
        py = int(y_off + (W - y_m) * SCALE)  # flip y to screen coords
        return px, py

    # arrow scaling: 1m/s ≡ ARROW_SCALE px
    ARROW_SCALE = SCALE * 0.7

    # ── pygame setup ──
    pygame.display.init()
    pygame.font.init()
    font = pygame.font.SysFont(None, 20)
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("AA‑CPM corridor visualisation")
    # transparent layer for RGBA discs
    layer_L = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
    layer_R = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)

    dt_sim = times[1] - times[0]
    dt_real = dt_sim / playback_speed

    i = 0
    paused = False
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_RIGHT:
                    i = min(i + 1, len(times) - 1)
                elif event.key == pygame.K_LEFT:
                    i = max(i - 1, 0)

        if not paused:
            screen.fill(BG_COLOR)

            # draw corridor outline
            x0, y0 = to_px(0, 0)
            x1, y1 = to_px(L, W)
            pygame.draw.rect(screen, TUNNEL_COLOR, (x0, y1, x1 - x0, y0 - y1), 2)
            layer_L.fill((0, 0, 0, 0))
            layer_R.fill((0, 0, 0, 0))
            t = times[i]
            frame = data["timesteps"][t]
            for pid, p in frame.items():
                x_px, y_px = to_px(p["x"], p["y"])
                r_px = max(2, int(p["r"] * SCALE))
                r_min_px = max(1, int(0.1 * SCALE))
                color = C_L if p["gs"] > 0 else C_R
                highlight_color = HC_L if color == C_L else HC_R
                min_color = C_L_MIN if color == C_L else C_R_MIN
                vx_sign = 1 if p["vx"] > 0 else -1
                layer = layer_L if vx_sign > 0 else layer_R
                pygame.draw.circle(layer, color, (x_px, y_px), r_px)
                pygame.draw.circle(layer, min_color, (x_px, y_px), r_min_px)
                # if vx_sign != p["gs"]:
                #     pygame.draw.circle(layer, highlight_color, (x_px, y_px), r_px, width=2)
                if dir_vector:
                    draw_arrow(screen, x_px, y_px, p["vx"], p["vy"], ARROW_SCALE)

            screen.blit(layer_L, (0, 0))
            screen.blit(layer_R, (0, 0))
            # timestamp label
            label = font.render(f"t = {t:.2f}s", True, LABEL_COLOR)
            screen.blit(label, (10, 10))

            pygame.display.flip()
            clock.tick(1 / dt_real)

            if i < len(times) - 1:
                i += 1
        else:
            # paused – just limit FPS
            clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python visualization.py <particle_data.csv> [speed=1.0] [dir_vector=False]")
        sys.exit(1)
    path_csv = Path(sys.argv[1]).expanduser()
    if not path_csv.exists():
        sys.exit(f"File not found: {path_csv}")
    speed = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    if speed <= 0:
        sys.exit("speed must be > 0")
    dir_vector = sys.argv[3].lower() == "true" if len(sys.argv) >= 4 else False

    visualise(path_csv, speed, dir_vector)
