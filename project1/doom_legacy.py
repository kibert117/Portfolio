import pygame
import math
import random

# Инициализация
pygame.init()

# Параметры экрана
WIDTH, HEIGHT = 800, 600
dis = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Doom Legacy - Maze Adventure")

clock = pygame.time.Clock()
FPS = 60

# Цвета в стиле старого Doom
dark_wall = (30, 30, 40)  # Темные стены
light_wall = (60, 60, 80)  # Светлые стены
player_color = (255, 255, 255)  # Белый игрок
player_head = (255, 200, 100)  # Желтоватый
health_glow = (255, 0, 0)  # Красный для состояния здоровья
floor_color = (40, 40, 50)  # Темный пол
corridor_color = (70, 70, 90)  # Цвет коридоров
exit_color = (100, 255, 100)  # Зеленый для выхода
keys_color = (255, 255, 0)  # Желтые ключи
health_potion_color = (255, 100, 100)  # Красный для зелья

# Шрифты
font_score = pygame.font.SysFont("bahnschrift", 24, bold=True)
font_game_over = pygame.font.SysFont("impact", 48, bold=True)
font_status = pygame.font.SysFont("calibri", 18)

# Настройка размера блока
BLOCK_SIZE = 20

# Эффекты

def draw_doom_wall(surface, x, y, width, height, dark=True):
    """Рисует стену в стиле Doom - с эффектом текстуры"""
    color = dark_wall if dark else light_wall
    
    # Основной прямоугольник
    pygame.draw.rect(surface, color, (x, y, width, height))
    
    # Добавляем эффект муара/текстуры стен для ретро-внешнего вида
    if dark:
        # Рисуем мелкие квадратики для текстуры
        for i in range(0, width, 2):
            for j in range(0, height, 2):
                if (i + j) % 4 == 0:
                    pygame.draw.rect(surface, light_wall, (x + i, y + j, 2, 2))
    else:
        # Рисуем более светлую текстуру
        for i in range(0, width, 3):
            for j in range(0, height, 3):
                if random.random() > 0.7:
                    pygame.draw.rect(surface, light_wall, (x + i, y + j, 3, 3))

def draw_doom_player(surface, x, y, size, health_percentage=1.0):
    """Рисует игрока в стиле Doom с эффектом свечения при низком здоровье"""
    # Рисуем свечение, если здоровье низкое
    glow_intensity = int(255 * (1 - health_percentage)) if health_percentage < 1.0 else 0
    if glow_intensity > 0:
        pygame.draw.circle(surface, (glow_intensity, 0, 0), (x + size // 2, y + size // 2), 
                          size // 2 + 2)
    
    # Рисуем игрока (как змейку, но в стиле Doom)
    pygame.draw.rect(surface, player_head, (x + 2, y + 2, size - 4, size - 4))
    
    # Эффект глаз (как у змеи)
    eye_size = 3
    left_eye = (x + size // 3, y + size // 3)
    right_eye = (x + 2 * size // 3 - eye_size, y + size // 3)
    pygame.draw.circle(surface, (0, 0, 0), left_eye, eye_size)
    pygame.draw.circle(surface, (255, 255, 255), left_eye, eye_size // 2)
    pygame.draw.circle(surface, (0, 0, 0), right_eye, eye_size)
    pygame.draw.circle(surface, (255, 255, 255), right_eye, eye_size // 2)
    
    # Рисуем хвост (хвост игрока)
    for i in range(1, size // 4):
        tail_x = x - i * 3
        if tail_x >= 0:
            pygame.draw.rect(surface, (200, 200, 200), (tail_x, y + 2, size - 4, size - 4))

def draw_inventory(surface, x, y, items):
    """Рисует инвентарь в стиле Doom (нижняя панель статуса)"""
    # Рисуем темную панель статуса
    pygame.draw.rect(surface, (0, 0, 0), (0, HEIGHT - 60, WIDTH, 60))
    pygame.draw.rect(surface, (100, 100, 100), (0, HEIGHT - 60, WIDTH, 60), 2)
    
    # Рисуем символы предметов
    item_spacing = 40
    for i, item in enumerate(items):
        item_x = 20 + i * item_spacing
        if item == "sword":
            # Рисуем меч
            pygame.draw.polygon(surface, (200, 200, 200), 
                              [(item_x, HEIGHT - 45), (item_x + 20, HEIGHT - 35), (item_x + 10, HEIGHT - 25)])
        elif item == "key":
            # Рисуем ключи
            pygame.draw.rect(surface, keys_color, (item_x, HEIGHT - 45, 15, 20))
            pygame.draw.polygon(surface, keys_color, 
                              [(item_x + 7, HEIGHT - 45), (item_x + 7, HEIGHT - 25), (item_x + 3, HEIGHT - 30)])
        elif item == "health":
            # Рисуем зелье здоровья
            pygame.draw.ellipse(surface, health_potion_color, (item_x, HEIGHT - 45, 15, 18))
            pygame.draw.ellipse(surface, (255, 255, 255), (item_x + 4, HEIGHT - 42, 7, 10))
    
    # Отображаем количество
    count_text = font_status.render(f" Items: {len(items)}", True, (255, 255, 255))
    surface.blit(count_text, (20, HEIGHT - 30))

def draw_DOOM_style_text(surface, text, font, color, x, y):
    """Рисует текст в стиле Doom - с более粗鄭 эффектом"""
    text_surf = font.render(text, True, color)
    surface.blit(text_surf, (x, y))
    
    # Добавляем тень для эффекта
    shadow_surf = font.render(text, True, (0, 0, 0))
    surface.blit(shadow_surf, (x + 2, y + 2))

# Игровой цикл
def game_loop():
    game_over = False
    game_close = False
    
    # Начальная позиция
    x1 = WIDTH // 2 // BLOCK_SIZE * BLOCK_SIZE
    y1 = (HEIGHT - 60) // 2 // BLOCK_SIZE * BLOCK_SIZE
    
    x1_change = 0
    y1_change = 0
    
    snake_list = []
    length = 1
    
    # Получаем загадочные предметы в стиле Doom
    items = ["key", "health"] if random.random() > 0.5 else ["key"]
    
    # Координаты еды/уровня (меч/Exit)
    if "sword" in items:
        weapon_x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
        weapon_y = round(random.randrange(0, HEIGHT - 60 - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
    elif "key" in items:
        key_x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
        key_y = round(random.randrange(0, HEIGHT - 60 - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
    else:
        weapon_x = weapon_y = key_x = key_y = -1
    
    # Случайное размещение стен
    walls = []
    for _ in range(30):
        wall_type = "vertical" if random.random() > 0.5 else "horizontal"
        if wall_type == "vertical":
            wx = random.randrange(40, WIDTH - 40, BLOCK_SIZE * 2)
            wy = random.randrange(40, HEIGHT - 60 - 40, BLOCK_SIZE)
            walls.append(("vertical", wx, wy))
        else:
            wx = random.randrange(40, WIDTH - 40, BLOCK_SIZE)
            wy = random.randrange(40, HEIGHT - 60 - 40, BLOCK_SIZE * 2)
            walls.append(("horizontal", wx, wy))
    
    # Цикл игры
    while not game_over:
        while game_close:
            dis.fill((0, 0, 0))
            draw_DOOM_style_text(dis, "Игра окончена!", font_game_over, (255, 50, 50), 
                              WIDTH // 2 - 200, HEIGHT // 2 - 50)
            draw_DOOM_style_text(dis, f"Счёт: {length - 1}", font_score, (255, 215, 0), 
                              WIDTH // 2 - 100, HEIGHT // 2 + 30)
            draw_DOOM_style_text(dis, "Нажмите C — играть снова, Q — выйти", font_status, (200, 200, 200), 
                              WIDTH // 2 - 250, HEIGHT // 2 + 80)
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
        x1 += x1_change
        y1 += y1_change
        
        # Проверки столкновений
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT - 60 or y1 < 0:
            game_close = True
        
        # Проверка столкновения со стенами
        for wall_type, wx, wy in walls:
            if wall_type == "vertical":
                if wx <= x1 <= wx + BLOCK_SIZE and (y1 >= wy and y1 <= wy + 100):
                    # Отскок от стены
                    x1_change = 0
            else:
                if wy <= y1 <= wy + BLOCK_SIZE and (x1 >= wx and x1 <= wx + 100):
                    y1_change = 0
        
        dis.fill(floor_color)
        
        # Рисуем коридоры (лавировка полов)
        for row in range(0, HEIGHT - 60, BLOCK_SIZE * 2):
            pygame.draw.rect(dis, corridor_color, (0, row, WIDTH, BLOCK_SIZE * 2))
        
        # Рисуем стены
        for wall_type, wx, wy in walls:
            if wall_type == "vertical":
                draw_doom_wall(dis, wx, wy, BLOCK_SIZE, 100)
            else:
                draw_doom_wall(dis, wx, wy, 100, BLOCK_SIZE, dark=(wx + wy) % 3 == 0)
        
        # Рисуем предметы
        if "sword" in items:
            pygame.draw.polygon(dis, (200, 200, 200), 
                              [(weapon_x, weapon_y), (weapon_x + BLOCK_SIZE, weapon_y + BLOCK_SIZE), 
                               (weapon_x + BLOCK_SIZE, weapon_y - BLOCK_SIZE), (weapon_x, weapon_y + BLOCK_SIZE)])
        elif "key" in items:
            pygame.draw.rect(dis, keys_color, (key_x, key_y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.polygon(dis, keys_color, 
                              [(key_x + BLOCK_SIZE//2, key_y), 
                               (key_x + BLOCK_SIZE//2, key_y + BLOCK_SIZE), 
                               (key_x + BLOCK_SIZE//2 - BLOCK_SIZE//4, key_y + BLOCK_SIZE//2)])
        elif "health" in items:
            pygame.draw.rect(dis, health_potion_color, (weapon_x, weapon_y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(dis, (255, 255, 255), (weapon_x + 2, weapon_y + 2, BLOCK_SIZE - 4, BLOCK_SIZE - 4))
        
        # Логика змейки
        snake_head = [x1, y1]
        snake_list.append(snake_head)
        
        if len(snake_list) > length:
            del snake_list[0]
        
        # Проверяем, съели ли предмет
        collect_item = False
        if "sword" in items and x1 == weapon_x and y1 == weapon_y:
            items.append("sword")
            collect_item = True
        elif "key" in items and x1 == key_x and y1 == key_y:
            items.append("key")
            collect_item = True
        elif "health" in items and x1 == weapon_x and y1 == weapon_y:
            items.append("health")
            collect_item = True
        
        if collect_item:
            items.remove(items[-1])  # Убираем иконку предмета из списка
        
        # Рисуем змейку (игрока)
        draw_doom_player(dis, x1, y1, BLOCK_SIZE)
        
        # Рисуем хвост (хвост змейки)
        for i in range(1, length):
            tail_x = snake_list[-i-1][0] if -i-1 < len(snake_list) else x1 - i * BLOCK_SIZE
            tail_y = snake_list[-i-1][1] if -i-1 < len(snake_list) else y1
            pygame.draw.rect(dis, (200, 200, 200), (tail_x, tail_y, BLOCK_SIZE, BLOCK_SIZE))
        
        # Проверка на столкновение с хвостом
        for x in snake_list[:-1]:
            if x == snake_head:
                game_close = True
        
        # Отображаемый счёт
        score_text = font_score.render(f"Счёт: {length - 1}", True, (255, 215, 0))
        dis.blit(score_text, (10, HEIGHT - 40))
        
        # Отображаем инвентарь
        draw_inventory(dis, 0, HEIGHT - 60, items)
        
        pygame.display.update()
        
        # Увеличиваем длину, если съели предмет
        if collect_item:
            length += 1
        
        clock.tick(FPS)
    
    pygame.quit()
    # Не используем quit() для безопасности

if __name__ == "__main__":
    game_loop()
