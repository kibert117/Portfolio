import pygame
import time
import random

# Инициализация Pygame
pygame.init()

# Цвета
WHITE = (255, 255, 255)
YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)

# Параметры экрана
dis_width = 600
dis_height = 400
dis = pygame.display.set_mode((dis_width, dis_height))
pygame.display.set_caption('Змейка')

clock = pygame.time.Clock()

# Шрифт и размер шрифта
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)

def your_score(score):
    value = score_font.render("Счёт: " + str(score), True, YELLOW)
    dis.blit(value, [0, 0])

def our_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(dis, GREEN, [x[0], x[1], snake_block, snake_block])

def message(msg, color):
    mesg = font_style.render(msg, True, color)
    # Центрирование текста
    text_rect = mesg.get_rect(center=(dis_width // 2, dis_height // 2))
    dis.blit(mesg, text_rect)

def gameLoop():
    game_over = False
    game_close = False

    # Начальная позиция змейки
    x1 = dis_width // 2
    y1 = dis_height // 2

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1

    # Еда
    foodx = round(random.randrange(0, dis_width - 10) / 10.0) * 10.0
    foody = round(random.randrange(0, dis_height - 10) / 10.0) * 10.0

    while not game_over:

        while game_close == True:
            dis.fill(BLACK)
            message("Ты проиграл! Q-Выход или C-Новая игра", RED)
            your_score(Length_of_snake - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change = -10
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change = 10
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change == 0:
                    y1_change = -10
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    y1_change = 10
                    x1_change = 0

        if x1 >= dis_width or x1 < 0 or y1 >= dis_height or y1 < 0:
            game_close = True
        x1 += x1_change
        y1 += y1_change
        dis.fill(BLACK)
        pygame.draw.rect(dis, BLUE, [foodx, foody, 10, 10])
        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        our_snake(10, snake_List)
        your_score(Length_of_snake - 1)

        pygame.display.update()

        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, dis_width - 10) / 10.0) * 10.0
            foody = round(random.randrange(0, dis_height - 10) / 10.0) * 10.0
            Length_of_snake += 1

        clock.tick(15)

    pygame.quit()
    quit()

gameLoop()
