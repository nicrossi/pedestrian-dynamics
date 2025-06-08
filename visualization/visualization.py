import pygame
import time
import math
import sys
import csv
'''
L: length
W: width
delta t
x, y, vx, vy for each particle
'''

def parse_particle_data(file_path):
    L = 16
    W = 3.6
    
    data = {
        "L": L,
        "W": W,
        "R_MAX": 0.35,
        "timesteps": {}
    }

    with open(file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row

        for row in reader:
            t, particle_id, x, y, xv, xy,r,g = row
            t = float(t)
            x, y, xv, xy,r = map(float, (x, y, xv, xy,r))

            if t not in data["timesteps"]:
                data["timesteps"][t] = {}

            data["timesteps"][t][particle_id] = {
                "x": x,
                "y": y,
                "vx": xv,
                "vy": xy,
                "r":r
            }
    return data

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 500
PADDING_X = 100
PADDING_Y = 100
BG_COLOR = (245, 245, 245)
PARTICLE_COLOR = (30, 30, 30)
ARROW_COLOR = (0, 100, 255)
TUNNEL_COLOR = (180, 180, 180)
C_L = (0x7f, 0xc9, 0x7f)
C_R = (0xfd, 0xc0, 0x86)

def draw_arrow(screen, x, y, vx, vy, scale=20):
    end_x = x + vx * scale
    end_y = y + vy * scale
    pygame.draw.line(screen, ARROW_COLOR, (x, y), (end_x, end_y), 2)

    angle = math.atan2(end_y - y, end_x - x)
    size = 6
    left = (end_x - size * math.cos(angle - math.pi / 6),
            end_y - size * math.sin(angle - math.pi / 6))
    right = (end_x - size * math.cos(angle + math.pi / 6),
             end_y - size * math.sin(angle + math.pi / 6))

    pygame.draw.polygon(screen, ARROW_COLOR, [(end_x, end_y), left, right])


def visualize_simulation(data, speed=1.0):
    L, W, R_MAX = data["L"], data["W"], data["R_MAX"]
    tunnel_px_width = WINDOW_WIDTH - 2 * PADDING_X
    tunnel_px_height = WINDOW_HEIGHT - 2 * PADDING_Y

    scale_x = tunnel_px_width / L
    r_px = int(R_MAX * tunnel_px_width / L)
    scale_y = (tunnel_px_height - 2 * r_px) / (W - 2 * R_MAX)

    pygame.display.init()
    pygame.font.init()
    font = pygame.font.SysFont(None,22)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pedestrian Dynamics Simulation")
    clock = pygame.time.Clock()

    timesteps = list(data["timesteps"].items())
    if len(timesteps) > 1:
        delta_t = timesteps[1][0] - timesteps[0][0]
    else:
        delta_t = 0.1/(2*1.5) #hardcodeado r_min/(2*max(v_d,v_e))

    next_time = time.perf_counter()
    step = delta_t / speed

    running = True
    timestep_index = 0

    color_by_id = {}
    def pick_color(pid, vx0):
        if pid in color_by_id:
            return color_by_id[pid]
        color_by_id[pid] = C_L if vx0 > 0 else C_R
        return color_by_id[pid]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if timestep_index >= len(timesteps):
            break

        screen.fill(BG_COLOR)

        pygame.draw.rect(screen,
                         TUNNEL_COLOR,
                         (PADDING_X, PADDING_Y + r_px, tunnel_px_width, tunnel_px_height - 2 * r_px),
                         2)

        y_min_px = PADDING_Y + round(r_px)
        y_max_px = PADDING_Y + round(r_px + (W - 2*R_MAX) * scale_y)

        _, particles = timesteps[timestep_index]
        for pid, p in particles.items():
            x = round(PADDING_X + p["x"] * scale_x)
            y = round(PADDING_Y + r_px + (W - p["r"] - p["y"]) * scale_y)
            y = max(
                    y_min_px + round(p["r"] * scale_x),
                    min(y_max_px - round(p["r"] * scale_x), y)
            )
            if not (0.0 <= p["x"] <= data["L"]):
                continue
            color = pick_color(pid, p["vx"])
            pygame.draw.circle(screen, color, (x, y),  max(2, int(p["r"] * scale_x)))

        screen.blit(font.render(f"t = {timesteps[timestep_index][0]:.2f} s", True, TUNNEL_COLOR), (10,10))
        pygame.display.flip()
        next_time += step
        timestep_index += 1

    pygame.quit()





if __name__ == "__main__":

    if (len(sys.argv) < 2):
        print("Usage: python visualization.py <particle_data_file> [speed=1.0]")
        sys.exit(1)

    data=parse_particle_data(sys.argv[1])
    speed = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    if speed <= 0:
        sys.exit("speed must be > 0")

    visualize_simulation(data, speed)