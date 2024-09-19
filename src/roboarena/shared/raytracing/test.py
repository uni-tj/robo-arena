import math
import time

import numpy as np
import pygame

from roboarena.shared.utils.perlin_nose import perlin_noise


def ray_march(player_pos, map_blocks, angle, max_distance, screen):
    ray_dir = (math.cos(angle), math.sin(angle))
    pygame.draw.line(
        screen,
        (255, 255, 0),
        player_pos,
        (
            player_pos[0] + ray_dir[0] * max_distance,
            player_pos[1] + ray_dir[1] * max_distance,
        ),
    )
    step = 0.1  # Adjust for precision vs. performance
    distance = 0

    while distance < max_distance:
        check_pos = (
            player_pos[0] + ray_dir[0] * distance,
            player_pos[1] + ray_dir[1] * distance,
        )

        # Find the two closest block corners
        block_x = int(check_pos[0])
        block_y = int(check_pos[1])

        if (block_x, block_y) in map_blocks:
            # Calculate exact intersection point
            return calculate_intersection(player_pos, check_pos, block_x, block_y)

        distance += step

    return None  # No intersection found within max_distance


def calculate_intersection(start, end, block_x, block_y):
    # Implement line-rectangle intersection here
    # This is a simplified placeholder
    return (block_x + 0.5, block_y + 0.5)


def cast_rays(player_pos, map_blocks, num_rays, fov, screen):
    t0 = time.time()
    intersections = []
    angle_step = fov / num_rays
    start_angle = -fov / 2

    for i in range(num_rays):
        angle = start_angle + i * angle_step
        intersection = ray_march(
            player_pos, map_blocks, angle, max_distance=200, screen=screen
        )
        if intersection:
            intersections.append(intersection)
    print(f"took {time.time()- t0 }")

    return intersections


# Main game loop
def main():
    pygame.init()
    size = 400
    screen = pygame.Surface((size, size))
    clock = pygame.time.Clock()

    player_pos = [size // 2, size // 2]
    noise = perlin_noise(size, size, gridsize=35, num_octaves=5, center=(300, 400))
    poss = set(map(tuple, np.transpose((noise > 0.67).nonzero())))
    map_blocks = poss

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
            player_pos, map_blocks, num_rays=100, fov=math.pi * 2, screen=screen
        )
        for intersection in intersections:
            pygame.draw.line(screen, (255, 255, 255), player_pos, intersection)

        # Draw player
        pygame.draw.circle(screen, (255, 0, 0), [int(p) for p in player_pos], 5)

        clock.tick(60)

        ascreen = pygame.display.set_mode((size * 4, size * 4))
        (pygame.transform.smoothscale_by(screen, 4, ascreen))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
