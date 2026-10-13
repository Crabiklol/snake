import pygame
import random
import sys
import pyodbc
import threading


DB_SERVER = r'(localdb)\MSSQLLocalDB'
DB_NAME = 'SnakeGameDBD'


def save_to_sql(player_name, score):

    try:
        conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={DB_SERVER};'
            f'DATABASE={DB_NAME};'
            f'Trusted_Connection=yes;',
            timeout=3
        )
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO GameResults (PlayerName, Score) VALUES (?, ?)",
            (player_name, score)
        )
        conn.commit()
        conn.close()
        print(f"✓ Сохранено в БД: {player_name} — {score}")
    except Exception as e:
        print(f"✗ Ошибка БД: {e}")



pygame.init()

WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
FPS = 10

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (200, 0, 0)
GRAY = (100, 100, 100)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Змейка + MS-SQL")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 36)


def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, (30, 30, 30), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, (30, 30, 30), (0, y), (WIDTH, y))


def spawn_food(snake_body):

    for _ in range(100):  # максимум 100 попыток
        x = random.randrange(0, WIDTH, CELL_SIZE)
        y = random.randrange(0, HEIGHT, CELL_SIZE)
        if [x, y] not in snake_body:
            return [x, y]
    # Если не нашли свободную клетку — возвращаем любую
    return [random.randrange(0, WIDTH, CELL_SIZE),
            random.randrange(0, HEIGHT, CELL_SIZE)]


def game_loop(player_name):
    snake_body = [[100, 100], [80, 100], [60, 100]]
    direction = "RIGHT"
    new_direction = direction
    food = spawn_food(snake_body)
    score = 0
    game_over = False
    saved = False

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        return True
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                else:
                    opposites = {"UP": "DOWN", "DOWN": "UP",
                                 "LEFT": "RIGHT", "RIGHT": "LEFT"}
                    pressed = None
                    if event.key == pygame.K_UP: pressed = "UP"
                    elif event.key == pygame.K_DOWN: pressed = "DOWN"
                    elif event.key == pygame.K_LEFT: pressed = "LEFT"
                    elif event.key == pygame.K_RIGHT: pressed = "RIGHT"

                    if pressed and opposites.get(pressed) != direction:
                        new_direction = pressed


        if not game_over:
            direction = new_direction
            head = snake_body[0].copy()

            if direction == "UP": head[1] -= CELL_SIZE
            elif direction == "DOWN": head[1] += CELL_SIZE
            elif direction == "LEFT": head[0] -= CELL_SIZE
            elif direction == "RIGHT": head[0] += CELL_SIZE

            snake_body.insert(0, head)


            if head == food:
                score += 10
                food = spawn_food(snake_body)
            else:
                snake_body.pop()

            # Столкновение?
            if (head[0] < 0 or head[0] >= WIDTH or
                head[1] < 0 or head[1] >= HEIGHT or
                head in snake_body[1:]):
                game_over = True


        screen.fill(BLACK)
        draw_grid()

        if not game_over:
            # Еда
            pygame.draw.rect(screen, RED,
                             pygame.Rect(food[0], food[1], CELL_SIZE, CELL_SIZE))

            for i, seg in enumerate(snake_body):
                color = GREEN if i == 0 else DARK_GREEN
                pygame.draw.rect(screen, color,
                                 pygame.Rect(seg[0], seg[1], CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, BLACK,
                                 pygame.Rect(seg[0], seg[1], CELL_SIZE, CELL_SIZE), 1)
            # Счёт
            score_text = font.render(f"Игрок: {player_name} | Счёт: {score}",
                                     True, WHITE)
            screen.blit(score_text, (10, 10))
        else:
            # Экран Game Over
            text = big_font.render("GAME OVER", True, RED)
            score_text = font.render(f"Счёт: {score}", True, WHITE)
            hint = font.render("R — заново, ESC — выход", True, WHITE)

            screen.blit(text, (WIDTH // 2 - 110, HEIGHT // 2 - 60))
            screen.blit(score_text, (WIDTH // 2 - 50, HEIGHT // 2))
            screen.blit(hint, (WIDTH // 2 - 130, HEIGHT // 2 + 40))


            if not saved:
                threading.Thread(target=save_to_sql,
                                 args=(player_name, score),
                                 daemon=True).start()
                saved = True

        pygame.display.flip()
        clock.tick(FPS)


def get_player_name():
    name = ""
    while True:
        screen.fill(BLACK)
        text = big_font.render("Введите имя:", True, WHITE)
        name_text = font.render(name + "_", True, GREEN)
        hint = font.render("Enter — начать", True, GRAY)

        screen.blit(text, (WIDTH // 2 - 120, HEIGHT // 2 - 60))
        screen.blit(name_text, (WIDTH // 2 - 50, HEIGHT // 2))
        screen.blit(hint, (WIDTH // 2 - 90, HEIGHT // 2 + 40))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isalnum() and len(name) < 15:
                    name += event.unicode


if __name__ == "__main__":
    while True:
        player_name = get_player_name()
        if not game_loop(player_name):
            break

pygame.quit()
