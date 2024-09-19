import math
import time
from collections import defaultdict

import numpy as np
import pygame

from roboarena.shared.utils.perlin_nose import perlin_noise


def ray_march(player_pos, map_blocks, angle, max_distance, block_size=50):
    ray_dir = (math.cos(angle), math.sin(angle))
    current_pos = list(player_pos)
    total_distance = 0

    # Calculate steps and initial distances
    step_x = 1 if ray_dir[0] > 0 else -1
    step_y = 1 if ray_dir[1] > 0 else -1

    cell_x, cell_y = int(current_pos[0] / block_size), int(current_pos[1] / block_size)

    # Calculate distance to next x or y cell boundary
    if ray_dir[0] != 0:
        delta_x = block_size / abs(ray_dir[0])
        next_x = (cell_x + step_x) * block_size if step_x > 0 else cell_x * block_size
        t_max_x = (next_x - current_pos[0]) / ray_dir[0]
    else:
        delta_x = float("inf")
        t_max_x = float("inf")

    if ray_dir[1] != 0:
        delta_y = block_size / abs(ray_dir[1])
        next_y = (cell_y + step_y) * block_size if step_y > 0 else cell_y * block_size
        t_max_y = (next_y - current_pos[1]) / ray_dir[1]
    else:
        delta_y = float("inf")
        t_max_y = float("inf")

    while total_distance < max_distance:
        # Check if current cell contains a block
        if (cell_x, cell_y) in map_blocks:
            return current_pos

        # Move to next cell
        if t_max_x < t_max_y:
            t_max_x += delta_x
            cell_x += step_x
            total_distance = t_max_x
        else:
            t_max_y += delta_y
            cell_y += step_y
            total_distance = t_max_y

        current_pos[0] = player_pos[0] + ray_dir[0] * total_distance
        current_pos[1] = player_pos[1] + ray_dir[1] * total_distance

    # No intersection found within max_distance
    return current_pos


def cast_rays(player_pos, map_blocks, num_rays, fov, max_distance):
    intersections = []
    angle_step = fov / num_rays
    start_angle = -fov / 2

    for i in range(num_rays):
        angle = start_angle + i * angle_step
        intersection = ray_march(player_pos, map_blocks, angle, max_distance)
        intersections.append(intersection)

    return intersections


# Main game loop
def main():
    pygame.init()
    size = 600
    screen = pygame.Surface((size, size))
    clock = pygame.time.Clock()

    player_pos = [size // 2, size // 2]
    noise = perlin_noise(size, size, gridsize=35, num_octaves=5, center=(300, 400))
    poss = set(map(tuple, np.transpose((noise > 0.67).nonzero())))
    map_blocks = poss
    # distance_field = prepare_distance_field(map_blocks)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        # Draw blocks
        for block in map_blocks:
            pygame.draw.rect(screen, (100, 100, 100), (block[0], block[1], 1, 1))

        # Cast rays and draw light
        intersections = cast_rays(
            player_pos, map_blocks, num_rays=36, fov=math.pi * 2, max_distance=100
        )
        for intersection in intersections:
            pygame.draw.circle(screen, (255, 255, 0), intersection, 2)
            pygame.draw.line(screen, (255, 0, 0), player_pos, intersection)

        # Draw player
        pygame.draw.circle(screen, (255, 0, 0), [int(p) for p in player_pos], 5)

        clock.tick(60)
        f = 1.5
        ascreen = pygame.display.set_mode((size * f, size * f))
        (pygame.transform.smoothscale_by(screen, f, ascreen))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
