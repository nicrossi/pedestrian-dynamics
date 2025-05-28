#!/usr/bin/env python
import sys, csv, itertools, time, pygame

FPS, SCALE, PAD = 60, 50, 40
R_MAX = 0.35
C_L, C_R = (0x7f, 0xc9, 0x7f), (0xfd, 0xc0, 0x86)
C_BG, C_W = (20, 20, 25), (180, 180, 185)


def frames(path):
    with open(path, newline="") as f:
        rdr = csv.reader(f);
        head = next(rdr)
        col = {h: i for i, h in enumerate(head)}
        t0, buf = None, []
        for row in rdr:
            t = float(row[col["time"]])
            if t0 is None: t0 = t
            if t != t0:
                yield t0, buf;
                buf = [];
                t0 = t
            buf.append((
                int(row[col["id"]]),
                float(row[col["x"]]),
                float(row[col["y"]]),
                float(row[col["radius"]]),
                float(row[col["vx"]])
            ))
        if buf: yield t0, buf


def play(csv_file, speed):
    fs = frames(csv_file)
    t0, a0 = next(fs);
    t1, _ = next(fs);
    dt = t1 - t0
    L, W = 16.0, 3.6

    r_px = int(R_MAX * SCALE)
    scr_w = int(L * SCALE) + 2 * PAD
    scr_h = int(W * SCALE) + 2 * PAD
    pygame.init()
    screen = pygame.display.set_mode((scr_w, scr_h))
    pygame.display.set_caption("Pedestrian Dynamics")
    font = pygame.font.SysFont(None, 22)
    clock = pygame.time.Clock()

    inner = pygame.Rect(PAD, PAD + r_px, L * SCALE, int((W - 2 * R_MAX) * SCALE))
    to_px = lambda x, y: (PAD + int(x * SCALE),
                          PAD + r_px + int((W - R_MAX - y) * SCALE))

    color_by_id = {}
    def pick_color(pid, vx0):
        if pid in color_by_id: return color_by_id[pid]
        color_by_id[pid] = C_L if vx0 > 0 else C_R
        return color_by_id[pid]

    stream = itertools.chain([(t0, a0), (t1, _)], fs)
    nxt = time.perf_counter();
    step = dt / speed

    for t, agents in stream:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); return

        screen.fill(C_BG)
        pygame.draw.rect(screen, C_W, inner, width=2)

        old_clip = screen.get_clip();
        screen.set_clip(inner)
        for pid, x, y, r, vx in agents:
            pygame.draw.circle(
                screen,
                pick_color(pid, vx),
                to_px(x, y),
                max(2, int(r * SCALE))
            )
        screen.set_clip(old_clip)

        screen.blit(font.render(f"t = {t:.2f} s", True, C_W), (10, 10))
        pygame.display.flip()

        nxt += step
        time.sleep(max(0, nxt - time.perf_counter()))
        # clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python visualization.py [input file csv] [speed]")
        sys.exit(1)
    play(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 1.0)
