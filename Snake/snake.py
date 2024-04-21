import pygame
import random

pygame.init()

# Set up game constants
WINDOW_SIZE_WIDTH = 400
WINDOW_SIZE_HEIGHT = 400
SQAURE_SIZE = 20
BACKGROUND_COLOR = pygame.Color(211, 211, 211)
FRUIT_COLOR = pygame.Color(83, 135, 0)
SNAKE_HEAD_COLOR = pygame.Color(0, 0, 0)
SNAKE_BODY_COLOR = pygame.Color(0, 83, 142)
GAME_SPEED = 100

# Set up the display
screen = pygame.display.set_mode((WINDOW_SIZE_WIDTH, WINDOW_SIZE_HEIGHT))
pygame.display.set_caption("Snake")

# Set up the starting positions
snake = [{"x": 3, "y": 2}, {"x": 4, "y": 2}, {"x": 5, "y": 2}]
fruit = {"x": 5, "y": 5}
current_direction = {"x": -1, "y": 0}
end = False


# draw the fruit
def draw_fruit():
    # infill
    pygame.draw.rect(
        screen,
        FRUIT_COLOR,
        (fruit["x"] * SQAURE_SIZE, fruit["y"] * SQAURE_SIZE, SQAURE_SIZE, SQAURE_SIZE),
    )
    # border
    pygame.draw.rect(
        screen,
        BACKGROUND_COLOR,
        (fruit["x"] * SQAURE_SIZE, fruit["y"] * SQAURE_SIZE, SQAURE_SIZE, SQAURE_SIZE),
        2,
    )


# draw the snake
def draw_snake():
    # infill head
    pygame.draw.rect(
        screen,
        SNAKE_HEAD_COLOR,
        (
            snake[0]["x"] * SQAURE_SIZE,
            snake[0]["y"] * SQAURE_SIZE,
            SQAURE_SIZE,
            SQAURE_SIZE,
        ),
    )
    # border head
    pygame.draw.rect(
        screen,
        BACKGROUND_COLOR,
        (
            snake[0]["x"] * SQAURE_SIZE,
            snake[0]["y"] * SQAURE_SIZE,
            SQAURE_SIZE,
            SQAURE_SIZE,
        ),
        2,
    )
    for segment in snake[1:]:
        # infill body
        pygame.draw.rect(
            screen,
            SNAKE_BODY_COLOR,
            (
                segment["x"] * SQAURE_SIZE,
                segment["y"] * SQAURE_SIZE,
                SQAURE_SIZE,
                SQAURE_SIZE,
            ),
        )
        # border body
        pygame.draw.rect(
            screen,
            (211, 211, 211),
            (
                segment["x"] * SQAURE_SIZE,
                segment["y"] * SQAURE_SIZE,
                SQAURE_SIZE,
                SQAURE_SIZE,
            ),
            2,
        )


# draw end screen
def draw_end(points: int):
    font = pygame.font.Font(None, 36)
    game_over = font.render("Game Over", True, (255, 255, 255))
    text_rect = game_over.get_rect(center=(200, 200))
    screen.blit(game_over, text_rect)
    font = pygame.font.Font(None, 24)
    points_text = font.render("Points: " + str(points), True, (255, 255, 255))
    points_rect = points_text.get_rect(center=(200, 250))
    screen.blit(points_text, points_rect)
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()


# check if the snake collides with the fruit
def check_collision():
    if snake[0]["x"] == fruit["x"] and snake[0]["y"] == fruit["y"]:
        return True
    return False


# check if the snake collides with itself
def check_self_collision():
    for segment in snake[1:]:
        if segment["x"] == snake[0]["x"] and segment["y"] == snake[0]["y"]:
            return True
    return False


# randomize the fruit position
def randomize_fruit():
    fruit["x"] = random.randint(0, SQAURE_SIZE - 1)
    fruit["y"] = random.randint(0, SQAURE_SIZE - 1)

    if check_collision():
        randomize_fruit()


# move the snake
def move_snake() -> dict[str, int]:
    tail = snake[-1]
    snake.pop()
    new_head = {
        "x": mod(snake[0]["x"] + current_direction["x"], SQAURE_SIZE),
        "y": mod(snake[0]["y"] + current_direction["y"], SQAURE_SIZE),
    }
    snake.insert(0, new_head)
    return tail


# modulo for negative numbers
def mod(n: int, m: int) -> int:
    return ((n % m) + m) % m


# main game loop
while not end:
    screen.fill(BACKGROUND_COLOR)
    draw_fruit()
    draw_snake()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            end = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and current_direction["y"] == 0:
                current_direction = {"x": 0, "y": -1}
            if event.key == pygame.K_DOWN and current_direction["y"] == 0:
                current_direction = {"x": 0, "y": 1}
            if event.key == pygame.K_LEFT and current_direction["x"] == 0:
                current_direction = {"x": -1, "y": 0}
            if event.key == pygame.K_RIGHT and current_direction["x"] == 0:
                current_direction = {"x": 1, "y": 0}

    tail = move_snake()

    if check_collision():
        snake.append(tail)
        randomize_fruit()

    if check_self_collision():
        end = True

    pygame.display.update()
    pygame.time.delay(GAME_SPEED)

draw_end(len(snake) - 3)
