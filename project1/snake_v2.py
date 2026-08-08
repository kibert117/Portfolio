import pygame
import math
import random

# Инициализация
pygame.init()

# Параметры экрана
WIDTH, HEIGHT = 600, 460
dis = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Змейка — улучшенная версия")

clock = pygame.time.Clock()
FPS = 15

# Цвета (градиенты и оттенки)
DARK_BG = (20, 25, 40)
GRID_COLOR = (30, 35, 55)
SNAKE_HEAD = (60, 200, 100)
SNAKE_BODY = (40, 180, 80)
SNAKE_TAIL = (20, 160, 60)
APPLE_COLOR = (255, 70, 70)
APPLE_HIGHLIGHT = (255, 150, 150)
TEXT_COLOR = (230, 230, 255)
SCORE_COLOR = (255, 215, 0)

# Шрифты
font_score = pygame.font.SysFont("calibri", 32, bold=True)
font_game_over = pygame.font.SysFont("impact", 48, bold=True)
font_restart = pygame.font.SysFont("calibri", 24)

# Настройка размеров
BLOCK_SIZE = 20
SNAKE_SPEED = 20  # пикселей за кадр (для плавности — в данном случае 1 блок за шаг)

# Эффекты
def draw_round_rect(surface, color, rect, radius=6):
    """Рисует прямоугольник со скруглёнными углами."""
    if radius <= 0:
        pygame.draw.rect(surface, color, rect)
        return
    rect = pygame.Rect(rect)
    pygame.draw.circle(surface, color, (rect.left + radius, rect.top + radius), radius)
    pygame.draw.circle(surface, color, (rect.right - radius, rect.top + radius), radius)
    pygame.draw.circle(surface, color, (rect.left + radius, rect.bottom - radius), radius)
    pygame.draw.circle(surface, color, (rect.right - radius, rect.bottom - radius), radius)
    pygame.draw.rect(surface, color, (rect.left + radius, rect.top, rect.width - 2*radius, rect.height))
    pygame.draw.rect(surface, color, (rect.left, rect.top + radius, rect.width, rect.height - 2*radius))

def draw_apple(surface, x, y, size):
    """Рисует красивое яблоко с бликом."""
    # Основа яблока
    apple_rect = pygame.Rect(x + 2, y + 2, size - 4, size - 4)
    draw_round_rect(surface, APPLE_COLOR, apple_rect, radius=8)

    # Блик (блик сверху слева)
    highlight_rect = pygame.Rect(x + 5, y + 5, size // 3, size // 4)
    pygame.draw.ellipse(surface, APPLE_HIGHLIGHT, highlight_rect)

    # Черенок
    stem_rect = pygame.Rect(x + size//2 - 2, y - 4, 4, 8)
    pygame.draw.rect(surface, (139, 69, 19), stem_rect)

    # Листик
    leaf_points = [
        (x + size//2, y - 4),
        (x + size//2 + 6, y - 8),
        (x + size//2 - 4, y - 7)
    ]
    pygame.draw.polygon(surface, (50, 205, 50), leaf_points)

def draw_snake_body_part(surface, x, y, is_head=False):
    """Рисует сегмент змейки."""
    rect = (x + 1, y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2)

    if is_head:
        # Голова — чуть больше, с глазами
        draw_round_rect(surface, SNAKE_HEAD, rect, radius=8)

        # Глаза
        eye_size = 3
        left_eye = (x + BLOCK_SIZE//4, y + BLOCK_SIZE//3)
        right_eye = (x + 3*BLOCK_SIZE//4 - 2*eye_size, y + BLOCK_SIZE//3)
        pygame.draw.circle(surface, (255, 255, 255), left_eye, eye_size + 1)
        pygame.draw.circle(surface, (0, 0, 0), left_eye, eye_size)
        pygame.draw.circle(surface, (255, 255, 255), right_eye, eye_size + 1)
        pygame.draw.circle(surface, (0, 0, 0), right_eye, eye_size)

    else:
        # Тело — с градиентом от головы к хвосту (здесь — базовый цвет)
        draw_round_rect(surface, SNAKE_BODY, rect, radius=6)
        # Тень для объёма
        shadow_rect = (x + 2, y + BLOCK_SIZE - 4, BLOCK_SIZE - 4, 2)
        pygame.draw.rect(surface, (0, 0, 0, 60), shadow_rect)

def draw_grid():
    """Фон — тонкая сетка."""
    for x in range(0, WIDTH, BLOCK_SIZE):
        pygame.draw.line(dis, GRID_COLOR, (x, 0), (x, HEIGHT - 40), 1)
    for y in range(0, HEIGHT - 40, BLOCK_SIZE):
        pygame.draw.line(dis, GRID_COLOR, (0, y), (WIDTH, y), 1)

def draw_text(text, font, color, center_x, center_y, offset_y=0):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(center_x, center_y + offset_y))
    dis.blit(surf, rect)

# Игровой цикл
def game_loop():
    game_over = False
    game_close = False

    # Начальная позиция
    x1 = WIDTH // 2 // BLOCK_SIZE * BLOCK_SIZE
    y1 = (HEIGHT - 40) // 2 // BLOCK_SIZE * BLOCK_SIZE

    x1_change = 0
    y1_change = 0

    snake_list = []
    length = 1

    # Еда (координаты кратны BLOCK_SIZE)
    foodx = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
    foody = round(random.randrange(0, HEIGHT - 40 - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE

    # Анимация яблока
    apple_pulse = 0

    while not game_over:
        while game_close:
            dis.fill(DARK_BG)
            draw_text("Вы проиграли!", font_game_over, (255, 50, 50), WIDTH // 2, HEIGHT // 2 - 60)
            draw_text(f"Счёт: {length - 1}", font_score, SCORE_COLOR, WIDTH // 2, HEIGHT // 2 - 10)
            draw_text("Нажмите C — играть снова, Q — выйти", font_restart, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 + 40)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change = -BLOCK_SIZE
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change = BLOCK_SIZE
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change == 0:
                    y1_change = -BLOCK_SIZE
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    y1_change = BLOCK_SIZE
                    x1_change = 0

        # Движение
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT - 40 or y1 < 0:
            game_close = True
        x1 += x1_change
        y1 += y1_change

        # Отрисовка фона и сетки
        dis.fill(DARK_BG)
        draw_grid()

        # Рисуем яблоко (с пульсацией)
        pulse = math.sin(apple_pulse) * 3
        draw_apple(dis, foodx + pulse//2, foody + pulse//2, BLOCK_SIZE)
        apple_pulse += 0.2

        # Логика змейки
        snake_head = [x1, y1]
        snake_list.append(snake_head)
        if len(snake_list) > length:
            del snake_list[0]

        # Проверка на столкновение с хвостом
        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_close = True

        # Рисуем змейку (с головой)
        for i, (x, y) in enumerate(snake_list):
            is_head = (i == len(snake_list) - 1)
            draw_snake_body_part(dis, x, y, is_head)

        # Счёт
        score_text = font_score.render(f"Счёт: {length - 1}", True, SCORE_COLOR)
        dis.blit(score_text, (10, HEIGHT - 30))

        pygame.display.update()

        # Еда
        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            foody = round(random.randrange(0, HEIGHT - 40 - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            length += 1

        clock.tick(FPS)

    pygame.quit()

# Запуск
if __name__ == "__main__":
    game_loop()