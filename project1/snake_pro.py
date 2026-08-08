import pygame
import math
import random
import sys

# Инициализация
pygame.init()

# Экран
WIDTH, HEIGHT = 640, 480
dis = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Змейка PRO — Ultimate Edition")
clock = pygame.time.Clock()
FPS = 12  # ✅ Снизили скорость для комфортной игры

# Цвета и стили
COLORS = {
    "bg": (15, 18, 28),
    "grid": (20, 25, 40),
    "snake_head": (100, 200, 120),
    "snake_body": (70, 180, 90),
    "snake_scales": (50, 140, 70),
    "apple_red": (220, 60, 60),
    "apple_shine": (255, 180, 180),
    "apple_stem": (101, 67, 33),
    "leaf": (60, 170, 80),
    "score_board": (30, 35, 50),
    "score_text": (255, 215, 0),
    "text_bg": (20, 25, 40),
    "text_shadow": (0, 0, 0, 80)
}

# Шрифты
font_hud = pygame.font.SysFont("segoeui", 28, bold=True)
font_msg = pygame.font.SysFont("segoeui", 42, bold=True)
font_small = pygame.font.SysFont("segoeui", 20)

# Настройки игры
BLOCK_SIZE = 20  # ✅ Оптимальный размер клетки
PARTICLE_LIFE = 20

# === Частицы (эффекты при поедании) ===
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = (random.random() - 0.5) * 6
        self.vy = (random.random() - 0.5) * 6
        self.life = PARTICLE_LIFE
        self.color = (random.randint(150, 255), random.randint(100, 200), random.randint(200, 255))
        self.size = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size *= 0.92

    def draw(self, surface):
        alpha = max(0, min(255, self.life * 12))
        color = (*self.color[:3], alpha)
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (self.size, self.size), self.size)
        surface.blit(surf, (self.x - self.size, self.y - self.size))

# === Утилиты ===
def draw_round_rect(surface, color, rect, radius=8, alpha=255):
    rect = pygame.Rect(rect)
    if alpha < 255:
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        draw_round_rect(s, (*color[:3], alpha), (0, 0, rect.width, rect.height), radius)
        surface.blit(s, (rect.x, rect.y))
        return

    pygame.draw.circle(surface, color, (rect.left + radius, rect.top + radius), radius)
    pygame.draw.circle(surface, color, (rect.right - radius, rect.top + radius), radius)
    pygame.draw.circle(surface, color, (rect.left + radius, rect.bottom - radius), radius)
    pygame.draw.circle(surface, color, (rect.right - radius, rect.bottom - radius), radius)
    pygame.draw.rect(surface, color, (rect.left + radius, rect.top, rect.width - 2*radius, rect.height))
    pygame.draw.rect(surface, color, (rect.left, rect.top + radius, rect.width, rect.height - 2*radius))

def draw_text_centered(text, font, color, center, offset_y=0):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=center)
    rect.y += offset_y
    dis.blit(surf, rect)

def draw_text_styled(text, font, color, topleft, shadow_color=(0, 0, 0)):
    shadow = font.render(text, True, shadow_color)
    dis.blit(shadow, (topleft[0] + 2, topleft[1] + 2))
    main = font.render(text, True, color)
    dis.blit(main, topleft)

# === Отрисовка элементов ===
def draw_grid():
    for y in range(0, HEIGHT - 40, BLOCK_SIZE):
        color = tuple(int(COLORS["grid"][i] + (y/HEIGHT)*10) for i in range(3))
        for x in range(0, WIDTH, BLOCK_SIZE):
            pygame.draw.rect(dis, color, (x, y, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_apple(surface, x, y, pulse=0):
    cx = x + BLOCK_SIZE // 2
    cy = y + BLOCK_SIZE // 2
    size = int(BLOCK_SIZE // 2 + pulse * 0.5)  # ✅ ИСПРАВЛЕНО: int()

    pygame.draw.line(surface, COLORS["apple_stem"], (cx, y + 4), (cx, y - 6), 3)

    leaf_points = [
        (cx + 2, y - 6),
        (cx + 10, y - 12),
        (cx - 4, y - 8)
    ]
    pygame.draw.polygon(surface, COLORS["leaf"], leaf_points)

    for i in range(size):
        alpha = 200 - i * 5
        radius = size - i
        if radius <= 0: 
            break
        color = (
            int(COLORS["apple_red"][0] * (1 - i/size)),
            int(COLORS["apple_red"][1] * (1 - i/size)),
            int(COLORS["apple_red"][2] * (1 - i/size))
        )
        pygame.draw.circle(surface, color, (cx, cy), radius)

    shine1 = (cx - size//3, cy - size//4)
    shine2 = (cx + size//4, cy + size//6)
    pygame.draw.circle(surface, COLORS["apple_shine"], shine1, size//6)
    pygame.draw.ellipse(surface, COLORS["apple_shine"], (*shine2, size//4, size//5))

def draw_snake_body(surface, x, y, pulse, direction, index):
    inset = 2
    rect = (x + inset, y + inset, BLOCK_SIZE - 2*inset, BLOCK_SIZE - 2*inset)

    ratio = min(1.0, index / 5)
    color_body = (
        max(30, int(COLORS["snake_body"][0] * (1 - ratio))),
        max(20, int(COLORS["snake_body"][1] * (1 - ratio))),
        max(20, int(COLORS["snake_body"][2] * (1 - ratio)))
    )

    if pulse > 0:
        shrink = pulse * 0.15
        rect = (x + shrink, y + shrink, BLOCK_SIZE - 2*shrink, BLOCK_SIZE - 2*shrink)

    shadow_rect = (rect[0] + 2, rect[1] + 2, rect[2], rect[3])
    pygame.draw.rect(dis, (0, 0, 0, 60), shadow_rect)

    draw_round_rect(dis, color_body, rect, 8)

    for i in range(1, 4):
        line_y = rect[1] + rect[3] * i // 4
        pygame.draw.line(dis, COLORS["snake_scales"], (rect[0], line_y), (rect[0] + rect[2], line_y), 2)

def draw_head(surface, x, y, pulse, direction):
    head_rect = (x, y, BLOCK_SIZE, BLOCK_SIZE)
    if pulse > 0:
        shrink = pulse * 0.15
        head_rect = (x + shrink, y + shrink, BLOCK_SIZE - 2*shrink, BLOCK_SIZE - 2*shrink)

    draw_round_rect(dis, COLORS["snake_head"], head_rect, 10)

    eye_offset = BLOCK_SIZE // 4
    cx = x + BLOCK_SIZE // 2
    cy = y + BLOCK_SIZE // 2

    eye_pos = {
        "UP":    [(cx - eye_offset, cy - eye_offset), (cx + eye_offset - 4, cy - eye_offset)],
        "DOWN":  [(cx - eye_offset, cy + eye_offset - 4), (cx + eye_offset - 4, cy + eye_offset - 4)],
        "LEFT":  [(cx - eye_offset, cy - eye_offset), (cx - eye_offset, cy + eye_offset - 4)],
        "RIGHT": [(cx + eye_offset - 4, cy - eye_offset), (cx + eye_offset - 4, cy + eye_offset - 4)]
    }

    if direction in eye_pos:
        left, right = eye_pos[direction]
        for p in [left, right]:
            pygame.draw.circle(dis, (255, 255, 255), p, 5)
        for p in [left, right]:
            pygame.draw.circle(dis, (0, 0, 0), p, 2)

# === Игра ===
def game_loop():
    game_over = False
    game_close = False
    score = 0

    x1 = WIDTH // BLOCK_SIZE // 2 * BLOCK_SIZE
    y1 = (HEIGHT - 40) // BLOCK_SIZE // 2 * BLOCK_SIZE
    x1_change = BLOCK_SIZE
    y1_change = 0
    direction = "RIGHT"
    snake_list = []
    length = 1

    foodx = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
    foody = round(random.randrange(0, HEIGHT - 40 - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE

    pulse = 0
    particles = []

    while not game_over:
        while game_close:
            panel = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(panel, (0, 0, 0, 150), (0, 0, WIDTH, HEIGHT))
            dis.blit(panel, (0, 0))

            draw_text_centered("Вы проиграли!", font_msg, (255, 80, 80), (WIDTH//2, HEIGHT//2 - 80))
            draw_text_centered(f"Ваш счёт: {score}", font_hud, (255, 215, 0), (WIDTH//2, HEIGHT//2 - 20))
            draw_text_centered("Нажмите C — игра заново, Q — выход", font_small, (230,230,255), (WIDTH//2, HEIGHT//2 + 50))

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

            pygame.display.update()
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and direction != "RIGHT":
                    x1_change = -BLOCK_SIZE
                    y1_change = 0
                    direction = "LEFT"
                elif event.key == pygame.K_RIGHT and direction != "LEFT":
                    x1_change = BLOCK_SIZE
                    y1_change = 0
                    direction = "RIGHT"
                elif event.key == pygame.K_UP and direction != "DOWN":
                    y1_change = -BLOCK_SIZE
                    x1_change = 0
                    direction = "UP"
                elif event.key == pygame.K_DOWN and direction != "UP":
                    y1_change = BLOCK_SIZE
                    x1_change = 0
                    direction = "DOWN"

        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT - 40 or y1 < 0:
            game_close = True
        x1 += x1_change
        y1 += y1_change

        pulse = max(0, pulse - 0.5)

        particles = [p for p in particles if p.life > 0]
        for p in particles:
            p.update()

        dis.fill(COLORS["bg"])
        draw_grid()

        apple_pulse = math.sin(pygame.time.get_ticks() / 150) * 2
        draw_apple(dis, foodx, foody, apple_pulse)

        snake_head = [x1, y1]
        snake_list.append(snake_head)
        if len(snake_list) > length:
            del snake_list[0]

        for seg in snake_list[:-1]:
            if seg == snake_head:
                game_close = True

        for i, (x, y) in enumerate(snake_list):
            draw_snake_body(dis, x, y, pulse, direction, i)

        draw_head(dis, snake_list[-1][0], snake_list[-1][1], pulse, direction)

        score_panel = pygame.Surface((WIDTH, 40))
        score_panel.fill(COLORS["score_board"])
        pygame.draw.line(score_panel, (50, 55, 70), (0, 0), (WIDTH, 0), 2)
        draw_text_styled(f"Счёт: {score}", font_hud, COLORS["score_text"], (10, 5), shadow_color=(0,0,0))
        dis.blit(score_panel, (0, HEIGHT - 40))

        for p in particles:
            p.draw(dis)

        pygame.display.update()
        clock.tick(FPS)

        if x1 == foodx and y1 == foody:
            score += 1
            length += 1
            foodx = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            foody = round(random.randrange(0, HEIGHT - 40 - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE

            for _ in range(12):
                particles.append(Particle(foodx + BLOCK_SIZE//2, foody + BLOCK_SIZE//2))
            pulse = 5
            apple_pulse = 5

if __name__ == "__main__":
    try:
        game_loop()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit()