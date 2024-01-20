import pygame
import random
import sqlite3
import pygame.sprite
import sys

SIZE_CELLS = 30
COUNT_CELLS = 20
SNAKE_COLOR = (0, 102, 0)
MARGIN_TOP = 60
all_sprites = pygame.sprite.Group()


def get_result():
    con = sqlite3.connect('snake_score.db')
    cur = con.cursor()
    result = cur.execute(f"""
        SELECT score_max from score_table
    """).fetchall()
    con.commit()
    con.close()
    return result[0][0]


def update_result(score):
    con = sqlite3.connect('snake_score.db')
    cur = con.cursor()
    cur.execute(f"""
        UPDATE score_table
        SET score_max = {score}
        WHERE {score} > score_max
    """)
    con.commit()
    con.close()


def draw_cell(screen, color, row, column):
    pygame.draw.rect(screen, color, [column * SIZE_CELLS + SIZE_CELLS,
                                     row * SIZE_CELLS + SIZE_CELLS + MARGIN_TOP,
                                     SIZE_CELLS, SIZE_CELLS])


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(-3, 3)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))
    print('2')


def show_score(screen, score):
    value = pygame.font.SysFont("comicsansms", 35).render("Ваша длина: " + str(score), True, pygame.Color('white'))
    value_max = pygame.font.SysFont("comicsansms", 35).render("Ваш рекорд: " + str(get_result()), True,
                                                              pygame.Color('white'))
    screen.blit(value, [SIZE_CELLS, SIZE_CELLS - 10])
    screen.blit(value_max, [400, SIZE_CELLS - 10])


def start_screen(screen, size):
    intro_text = ["SNAKE GAME", "",
                  "Приветствую вас!",
                  "Желаю приятной игры",
                  "для начала нажмите на любую клавишу"]

    fon = pygame.transform.scale(pygame.image.load('img/fon1.jpg'), size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50

    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру


def loose_screen(screen, score):
    intro_text = ["ВЫ ПРОИГРАЛИ", "",
                  f"ваш счет: {score}",
                  'нажмите на любую клавишу для продолжения']

    record_text = "У вас новый рекорд!"
    screen.fill((147, 194, 214))
    font = pygame.font.Font(None, 30)
    text_coord = 200

    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
        print(get_result())

    if score > int(get_result()):
        string_rendered = font.render(record_text, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру


def terminate():
    pygame.quit()
    sys.exit()


class Board:
    # создание поля
    def __init__(self, count_cells, cell_size):
        self.cell_size = cell_size
        self.count_cells = count_cells
        self.cell_size = cell_size

    def render(self, scrn):
        for row in range(self.count_cells):
            for column in range(self.count_cells):
                if (row + column) % 2 == 0:
                    color = pygame.Color('grey')
                else:
                    color = pygame.Color('white')
                draw_cell(scrn, color, row, column)


class Player:
    def __init__(self, x, y):
        self.spawn_row = x
        self.spawn_column = y

    def show_spawn(self):
        return self.spawn_row, self.spawn_column

    def move(self, dx, dy):
        self.spawn_row += dy
        self.spawn_column += dx
        return self.spawn_row, self.spawn_column


class Apple:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [pygame.image.load('img/part.png')]
    for scale in (1, 2):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это векторs
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos[1] * SIZE_CELLS + SIZE_CELLS + (SIZE_CELLS / 2), pos[
            0] * SIZE_CELLS + SIZE_CELLS + MARGIN_TOP + (SIZE_CELLS / 2)

        # гравитация будет одинаковой (значение константы)
        self.gravity = 2

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(0, 0, 700, 700):
            self.kill()


def main():
    pygame.init()
    size = [SIZE_CELLS * COUNT_CELLS + SIZE_CELLS * 2, SIZE_CELLS * COUNT_CELLS + 2 * SIZE_CELLS + MARGIN_TOP]
    length = 1
    dx, dy = 0, 0
    dirs = {'W': True, 'S': True, 'A': True, 'D': True}

    pygame.display.set_caption('Snake game')
    screen = pygame.display.set_mode(size)
    board = Board(COUNT_CELLS, SIZE_CELLS)
    player = Player(random.randint(0, 19), random.randint(0, 19))
    snake = [player.show_spawn()]
    apple = Apple(random.randint(0, 19), random.randint(0, 19))
    clock = pygame.time.Clock()
    music = pygame.mixer.Sound('sounds/Beethoven.ogg')
    eat = pygame.mixer.Sound("sounds/bite.ogg")

    start_screen(screen, size)
    music.play()

    running = True
    while running:
        # отрисовка и изменение
        all_sprites.update()

        screen.fill((0, 0, 0))
        board.render(screen)

        draw_cell(screen, pygame.Color('red'), apple.x, apple.y)
        snake.append(player.move(dx, dy))
        snake = snake[-length:]

        show_score(screen, length)

        if 0 > snake[-1][0] or 19 < snake[-1][0] or 0 > snake[-1][1] or 19 < snake[-1][1] \
                or len(snake) != len(set(snake)):
            music.stop()
            loose_screen(screen, length)
            update_result(length)
            main()

        for elem in snake:
            draw_cell(screen, SNAKE_COLOR, elem[0], elem[1])

        if snake[-1] == (apple.x, apple.y):
            eat.play()
            create_particles((apple.x, apple.y))
            spawn_coord = random.randint(0, 19), random.randint(0, 19)
            while spawn_coord in snake:
                spawn_coord = random.randint(0, 19), random.randint(0, 19)
            apple = Apple(spawn_coord[0], spawn_coord[1])
            length += 1

        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(length // 4 + 9)

        # управление
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        key = pygame.key.get_pressed()
        if key[pygame.K_w]:
            if dirs['W']:
                dx, dy = 0, -1
                dirs = {'W': True, 'S': False, 'A': True, 'D': True}
        elif key[pygame.K_s]:
            if dirs['S']:
                dx, dy = 0, 1
                dirs = {'W': False, 'S': True, 'A': True, 'D': True}
        elif key[pygame.K_a]:
            if dirs['A']:
                dx, dy = -1, 0
                dirs = {'W': True, 'S': True, 'A': True, 'D': False}
        elif key[pygame.K_d]:
            if dirs['D']:
                dx, dy = 1, 0
                dirs = {'W': True, 'S': True, 'A': False, 'D': True}
    terminate()


if __name__ == "__main__":
    main()
