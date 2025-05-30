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
        "timesteps": {}
    }

    with open(file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row

        for row in reader:
            t, particle_id, x, y, xv, xy,r = row
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


def visualize_simulation(data):
    tunnel_px_width = WINDOW_WIDTH - 2 * PADDING_X
    tunnel_px_height = WINDOW_HEIGHT - 2 * PADDING_Y

    scale_x = tunnel_px_width / data['L']
    scale_y = tunnel_px_height / data['W']

    pygame.display.init()
    pygame.font.init()

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pedestrian Dynamics Simulation")
    clock = pygame.time.Clock()

    timesteps = list(data["timesteps"].items())
    delta_t = 0.0001

    running = True
    timestep_index = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if timestep_index >= len(timesteps):
            break

        screen.fill(BG_COLOR)

        pygame.draw.rect(screen, TUNNEL_COLOR, (PADDING_X, PADDING_Y, tunnel_px_width, tunnel_px_height), 2)

        _, particles = timesteps[timestep_index]
        for p in particles.values():
            x = int(PADDING_X + p["x"] * scale_x)
            y = int(PADDING_Y + (data["W"] - p["y"]) * scale_y)
            pygame.draw.circle(screen, PARTICLE_COLOR, (x, y), p["r"])
            draw_arrow(screen, x, y, p["vx"], -p["vy"])

        pygame.display.flip()
        clock.tick(1 / delta_t)
        timestep_index += 1

    pygame.quit()





if __name__ == "__main__":
    data=parse_particle_data(sys.argv[1])
    visualize_simulation(data)