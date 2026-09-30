import pygame
import random
import sys

# ИНИЦИАЛИЗАЦИЯ
pygame.init()

# Размеры окна
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20  # размер одной клетки

# Цвета (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
DARK_GREEN = (0, 150, 0)

# Скорость игры (FPS)
FPS = 10

# Создаем окно
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Змейка (Snake)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 36)


# КЛАСС ЗМЕЙКИ 
class Snake:
    def __init__(self):
        # Начальная позиция змейки (список сегментов)
        self.body = [
            [100, 100],
            [80, 100],
            [60, 100]
        ]
        self.direction = "RIGHT"  # начальное направление
        self.change_to = self.direction

    def change_direction(self, new_dir):
        """Меняем направление, но нельзя развернуться на 180°"""
        opposites = {
            "UP": "DOWN", "DOWN": "UP",
            "LEFT": "RIGHT", "RIGHT": "LEFT"
        }
        if opposites[new_dir] != self.direction:
            self.change_to = new_dir

    def move(self):
        """Двигаем змейку"""
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

        self.body.insert(0, head)  # добавляем новую голову

    def eat(self):
        """Если съела еду — не удаляем хвост (растёт)"""
        pass  # хвост удаляется только если НЕ съела

    def shrink(self):
        """Удаляем хвост (обычное движение)"""
        self.body.pop()

    def check_collision(self):
        """Проверка столкновения со стенами или с собой"""
        head = self.body[0]
        # Стены
        if head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT:
            return True
        # Сама себя
        if head in self.body[1:]:
            return True
        return False

    def draw(self):
        """Рисуем змейку"""
        for i, segment in enumerate(self.body):
            color = GREEN if i == 0 else DARK_GREEN  # голова ярче
            pygame.draw.rect(
                screen, color,
                pygame.Rect(segment[0], segment[1], CELL_SIZE, CELL_SIZE)
            )
            pygame.draw.rect(
                screen, BLACK,
                pygame.Rect(segment[0], segment[1], CELL_SIZE, CELL_SIZE), 1
            )


# КЛАСС ЕДЫ 
class Food:
    def __init__(self):
        self.position = self.random_position()

    def random_position(self):
        """Случайная позиция, кратная CELL_SIZE"""
        x = random.randrange(0, WIDTH, CELL_SIZE)
        y = random.randrange(0, HEIGHT, CELL_SIZE)
        return [x, y]

    def draw(self):
        """Рисуем еду (красный квадрат)"""
        pygame.draw.rect(
            screen, RED,
            pygame.Rect(self.position[0], self.position[1],
                        CELL_SIZE, CELL_SIZE)
        )


# ОСНОВНАЯ ФУНКЦИЯ ИГРЫ 
def game_loop():
    snake = Snake()
    food = Food()
    score = 0
    game_over = False

    while True:
        #  Обработка событий 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Управление стрелками
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        return  # перезапуск
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
            # Экран Game Over
            screen.fill(BLACK)
            text = big_font.render("GAME OVER", True, RED)
            score_text = font.render(f"Счёт: {score}", True, WHITE)
            hint = font.render("R — заново, ESC — выход", True, WHITE)

            screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 - 60))
            screen.blit(score_text, (WIDTH // 2 - 50, HEIGHT // 2))
            screen.blit(hint, (WIDTH // 2 - 130, HEIGHT // 2 + 40))
            pygame.display.flip()
            continue

        # Логика игры 
        snake.move()

        # Проверка: съела ли еду?
        if snake.body[0] == food.position:
            score += 10
            food = Food()  # новая еда
            # Проверка, чтобы еда не появилась на змейке
            while food.position in snake.body:
                food = Food()
        else:
            snake.shrink()  # удаляем хвост

        # Проверка столкновения
        if snake.check_collision():
            game_over = True

        # Отрисовка 
        screen.fill(BLACK)

        # Рисуем сетку (опционально, для красоты)
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(screen, (30, 30, 30), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, (30, 30, 30), (0, y), (WIDTH, y))

        food.draw()
        snake.draw()

        # Счёт в углу
        score_text = font.render(f"Счёт: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)


# ЗАПУСК 
if __name__ == "__main__":
    while True:
        game_loop()
