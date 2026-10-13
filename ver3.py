import pygame
import random
import sys
import pyodbc


DB_SERVER = 'WIN-PP91IA6UC6F\LOCALDB#7C87ABF7'
DB_NAME = 'SnakeGameDB'


def save_to_sql(player_name, score):

    try:
        conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={DB_SERVER};'
            f'DATABASE={DB_NAME};'
            f'Trusted_Connection=yes;'
        )
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO GameResults (PlayerName, Score) VALUES (?, ?)",
            (player_name, score)
        )
        conn.commit()
        conn.close()
        print(f"✓ Результат сохранен: {player_name} - {score} очков")
        return True
    except Exception as e:
        print(f"✗ Ошибка сохранения в БД: {e}")
        return False



pygame.init()

WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
FPS = 10

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (200, 0, 0)
GRAY = (100, 100, 100)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Змейка с сохранением в MS-SQL")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 36)



class Snake:
    def __init__(self):
        self.body = [[100, 100], [80, 100], [60, 100]]
        self.direction = "RIGHT"
        self.change_to = self.direction

    def change_direction(self, new_dir):
        opposites = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
        if opposites[new_dir] != self.direction:
            self.change_to = new_dir

    def move(self):
        self.direction = self.change_to
        head = self.body[0].copy()
        if self.direction == "UP":
            head[1] -= CELL_SIZE
        elif self.direction == "DOWN":
            head[1] += CELL_SIZE
        elif self.direction == "LEFT":
            head[0] -= CELL_SIZE
        elif self.direction == "RIGHT":
            head[0] += CELL_SIZE
        self.body.insert(0, head)

    def shrink(self):
        self.body.pop()

    def check_collision(self):
        head = self.body[0]
        if head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT:
            return True
        if head in self.body[1:]:
            return True
        return False

    def draw(self):
        for i, segment in enumerate(self.body):
            color = GREEN if i == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, pygame.Rect(segment[0], segment[1], CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, BLACK, pygame.Rect(segment[0], segment[1], CELL_SIZE, CELL_SIZE), 1)



class Food:
    def __init__(self):
        self.position = self.random_position()

    def random_position(self):
        x = random.randrange(0, WIDTH, CELL_SIZE)
        y = random.randrange(0, HEIGHT, CELL_SIZE)
        return [x, y]

    def draw(self):
        pygame.draw.rect(screen, RED, pygame.Rect(self.position[0], self.position[1], CELL_SIZE, CELL_SIZE))



def get_player_name():

    name = ""
    input_active = True

    while input_active:
        screen.fill(BLACK)
        text = big_font.render("Введите ваше имя:", True, WHITE)
        name_text = font.render(name, True, GREEN)
        hint = font.render("Enter - начать игру", True, GRAY)

        screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2 - 60))
        screen.blit(name_text, (WIDTH // 2 - 50, HEIGHT // 2))
        screen.blit(hint, (WIDTH // 2 - 100, HEIGHT // 2 + 40))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if name.strip():
                        input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isalpha() or event.unicode.isdigit():
                    name += event.unicode

    return name.strip()



def game_loop(player_name):
    snake = Snake()
    food = Food()
    score = 0
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        return True  # Перезапуск
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                else:
                    if event.key == pygame.K_UP:
                        snake.change_direction("UP")
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction("DOWN")
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction("LEFT")
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction("RIGHT")

        if game_over:
            screen.fill(BLACK)
            text = big_font.render("GAME OVER", True, RED)
            score_text = font.render(f"Счёт: {score}", True, WHITE)
            hint = font.render("R — заново, ESC — выход", True, WHITE)

            screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 - 60))
            screen.blit(score_text, (WIDTH // 2 - 50, HEIGHT // 2))
            screen.blit(hint, (WIDTH // 2 - 130, HEIGHT // 2 + 40))
            pygame.display.flip()


            save_to_sql(player_name, score)
            continue

        snake.move()

        if snake.body[0] == food.position:
            score += 10
            food = Food()
            while food.position in snake.body:
                food = Food()
        else:
            snake.shrink()

        if snake.check_collision():
            game_over = True


        screen.fill(BLACK)
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(screen, (30, 30, 30), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, (30, 30, 30), (0, y), (WIDTH, y))

        food.draw()
        snake.draw()

        score_text = font.render(f"Игрок: {player_name} | Счёт: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)



if __name__ == "__main__":
    while True:
        player_name = get_player_name()
        restart = game_loop(player_name)
        if not restart:
            break

            
