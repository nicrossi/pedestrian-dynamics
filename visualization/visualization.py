import pygame
import time
import math

# Store data as 
'''
L: length
W: width
delta t
x, y, vx, vy for each particle
'''

def parse_particle_data(lines):
    L = float(lines[0].strip())   
    W = float(lines[1].strip())   
    
    data = {
        "L": L,
        "W": W,
        "timesteps": {}
    }

    i = 2
    while i < len(lines):
        if lines[i].strip().isdigit():
            timestep = int(lines[i].strip())
            i += 1
            particles = {}
            particle_count = 1
            while i < len(lines) and len(lines[i].strip().split()) == 4:
                x, y, vx, vy = map(float, lines[i].strip().split())
                particles[f"p_{particle_count}"] = {
                    "x": x, "y": y, "vx": vx, "vy": vy
                }
                i += 1
                particle_count += 1
            data["timesteps"][f"{timestep}"] = particles
        else:
            i += 1  
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
    delta_t = data["delta_t"]

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
            pygame.draw.circle(screen, PARTICLE_COLOR, (x, y), 6)
            draw_arrow(screen, x, y, p["vx"], -p["vy"])

        pygame.display.flip()
        clock.tick(1 / delta_t)
        time.sleep(0.5) # TODO: decrease or delete when used for real data
        timestep_index += 1

    pygame.quit()


def main():
    # TODO: just for development, remove when used for real data
    mock_data = {
        'L': 16.0,
        'W': 3.6,
        'delta_t': 0.1,
        'timesteps': {
            '1': {
                'particle_1': {'x': 1, 'y': 0.5, 'vx': 1.2, 'vy': 0.3},
                'particle_2': {'x': 3, 'y': 1.0, 'vx': 1.1, 'vy': -0.2},
                'particle_3': {'x': 2, 'y': 2.0, 'vx': 1.4, 'vy': 0.0}
            },
            '2': {
                'particle_1': {'x': 1.2, 'y': 0.53, 'vx': 1.2, 'vy': 0.3},
                'particle_2': {'x': 3.2, 'y': 0.96, 'vx': 1.1, 'vy': -0.2},
                'particle_3': {'x': 2.4, 'y': 2.0, 'vx': 1.4, 'vy': 0.0}
            },
            '3': {
                'particle_1': {'x': 1.4, 'y': 0.56, 'vx': 1.2, 'vy': 0.3},
                'particle_2': {'x': 3.4, 'y': 0.92, 'vx': 1.1, 'vy': -0.2},
                'particle_3': {'x': 2.8, 'y': 2.0, 'vx': 1.4, 'vy': 0.0}
            },
            '4': {
                'particle_1': {'x': 1.6, 'y': 0.59, 'vx': 1.2, 'vy': 0.3},
                'particle_2': {'x': 3.6, 'y': 0.88, 'vx': 1.1, 'vy': -0.2},
                'particle_3': {'x': 3.2, 'y': 2.0, 'vx': 1.4, 'vy': 0.0},
                'particle_4': {'x': 0.0, 'y': 3.5, 'vx': 2.0, 'vy': -1.0}
            }
        }
    }

    visualize_simulation(mock_data)


if __name__ == "__main__":
    main()