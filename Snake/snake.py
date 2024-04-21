import random
from dataclasses import dataclass, field
from typing import Callable

import pygame


# immutable Dataclass as a representation of postion and direction information
@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(
        self,
        o: "Position",
    ) -> "Position":
        return Position(self.x + o.x, self.y + o.y)

    def apply_transform(self, f: Callable[[int], int] = lambda x: x):
        return Position(f(self.x), f(self.y))

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Position):
            return NotImplemented
        return (self.x - o.x, self.y - o.y) == (0, 0)

    def drawing_coords(self, size: int) -> tuple[int, int, int, int]:
        return self.x * size, self.y * size, size, size

    def dot_product(self, o: "Position") -> int:
        return self.x * o.x + self.y * o.y

    @staticmethod
    def random_pos(mx: int, my: int) -> "Position":
        return Position(random.randint(0, mx - 1), random.randint(0, my - 1))


@dataclass()
class Snake:
    body: list[Position] = field(
        default_factory=lambda: [Position(3, 2), Position(4, 2), Position(5, 2)]
    )
    direction: Position = Position(-1, 0)


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
snake = Snake()
fruit: Position = Position(5, 5)
current_direction = Position(-1, 0)
end = False


# draw the fruit
def draw_fruit():
    # infill
    pygame.draw.rect(screen, FRUIT_COLOR, (fruit.drawing_coords(SQAURE_SIZE)))

    pygame.draw.rect(
        screen,
        BACKGROUND_COLOR,
        (fruit.drawing_coords(SQAURE_SIZE)),
        2,
    )


def draw_bordered_rect(pos: Position, color: pygame.Color) -> None:
    pygame.draw.rect(screen, color, pos.drawing_coords(SQAURE_SIZE))
    # border head
    pygame.draw.rect(
        screen,
        BACKGROUND_COLOR,
        pos.drawing_coords(SQAURE_SIZE),
        2,
    )


# draw the snake
def draw_snake():
    # draw head
    draw_bordered_rect(snake.body[0], SNAKE_HEAD_COLOR)
    for segment in snake.body[1:]:
        # infill body
        draw_bordered_rect(segment, SNAKE_BODY_COLOR)


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
def check_collision(fruit: Position):
    if any(map(lambda seg: seg == fruit, snake.body)):
        return True
    return False


# check if the snake collides with itself
def check_self_collision():
    for segment in snake.body[1:]:
        if snake.body[0] == segment:
            return True
    return False


# randomize the fruit position
def randomize_fruit():
    """#! This Code is flawed due to the issue that all fields could be occupied!
    A faster and more reliable way to find a empty position is to choose a random start
    and checking the closest positions systematically. This ensures, that a
    result will always be found deterministically in at most Square_Size^2 steps!
    While the current Implementation might never find a free spot.
    """
    while True:
        fpos = Position.random_pos(SQAURE_SIZE, SQAURE_SIZE)
        if not check_collision(fpos):
            print(fpos)
            return fpos


# move the snake
def move_snake() -> Position:
    tail = snake.body[-1]
    snake.body.pop()
    new_head = (snake.body[0] + snake.direction).apply_transform(
        lambda x: mod(x, SQAURE_SIZE)
    )
    snake.body.insert(0, new_head)
    return tail


# modulo for negative numbers
def mod(n: int, m: int) -> int:
    return ((n % m) + m) % m


DIRECTIONS = {
    "Up": Position(0, -1),
    "Down": Position(0, 1),
    "Left": Position(-1, 0),
    "Right": Position(1, 0),
}
DIRECTION_CHANGE = {
    pygame.K_UP: DIRECTIONS["Up"],
    pygame.K_w: DIRECTIONS["Up"],
    pygame.K_DOWN: DIRECTIONS["Down"],
    pygame.K_s: DIRECTIONS["Down"],
    pygame.K_LEFT: DIRECTIONS["Left"],
    pygame.K_a: DIRECTIONS["Left"],
    pygame.K_RIGHT: DIRECTIONS["Right"],
    pygame.K_d: DIRECTIONS["Right"],
}
# main game loop
while not end:
    screen.fill(BACKGROUND_COLOR)
    draw_fruit()
    draw_snake()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            end = True
        if event.type == pygame.KEYDOWN and event.key in DIRECTION_CHANGE:
            new_dir = DIRECTION_CHANGE[event.key]
            if new_dir.dot_product(snake.direction) == 0:
                snake.direction = new_dir
    tail = move_snake()

    if check_collision(fruit):
        snake.body.append(tail)
        fruit = randomize_fruit()

    if check_self_collision():
        end = True

    pygame.display.update()
    pygame.time.delay(GAME_SPEED)

draw_end(len(snake.body) - 3)
