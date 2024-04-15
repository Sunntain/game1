import pygame

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)  # Добавляем желтый цвет для ключа
GRAVITY = 0.5
MAX_FALL_SPEED = 10
JUMP_POWER = -10.5
MOVE_SPEED = 5

# Создание окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Простой платформер")


# Класс для кнопок
class Button(pygame.sprite.Sprite):
    def __init__(self, text, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.font = pygame.font.Font(None, 36)
        self.text = text
        self.render_text()

    def render_text(self):
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=(self.rect.width / 2, self.rect.height / 2))
        self.image.fill(WHITE)
        self.image.blit(text_surf, text_rect)

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(pygame.mouse.get_pos()):
            return True
        return False


# Функция отображения главного меню
def main_menu():
    title_font = pygame.font.Font(None, 64)
    title_text = title_font.render("Главное меню", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

    start_button = Button("Начать игру", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50, GREEN)
    quit_button = Button("Выход", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 50, RED)

    menu_sprites = pygame.sprite.Group(start_button, quit_button)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if start_button.update(event):
                return True
            if quit_button.update(event):
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False

        screen.fill(BLACK)
        screen.blit(title_text, title_rect)
        menu_sprites.draw(screen)
        pygame.display.flip()


# Класс для игрового персонажа
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Создание изображения и прямоугольника для игрока
        self.image = pygame.Surface((50, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        # Позиционирование игрока в центре экрана по горизонтали и по вертикали
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        # Начальная скорость по вертикали
        self.y_velocity = 0
        # Флаг, указывающий, что игрок находится на земле
        self.on_ground = False
        # Флаг, указывающий, что игрок взял ключ
        self.has_key = False

    # Обновление игрока
    def update(self, platforms, spikes):
        # Обработка гравитации
        self.y_velocity += GRAVITY
        if self.y_velocity > MAX_FALL_SPEED:
            self.y_velocity = MAX_FALL_SPEED
        self.rect.y += self.y_velocity

        # Проверка столкновения игрока с платформами по вертикали
        self.check_collision_y(platforms)

        # Проверка столкновения игрока с шипами
        self.check_collision_spikes(spikes)

        # Проверка выхода за пределы экрана по горизонтали
        if self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH

        # Обработка прыжка и перемещения влево и вправо
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.on_ground:
            self.y_velocity = JUMP_POWER
            self.on_ground = False

        # Перемещение влево и вправо с обработкой столкновений
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= MOVE_SPEED
            self.handle_collision_x(platforms)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += MOVE_SPEED
            self.handle_collision_x(platforms)

    # Обработка столкновений игрока с платформами по вертикали
    def check_collision_y(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.y_velocity > 0:
                    self.rect.bottom = platform.rect.top
                    self.y_velocity = 0
                    self.on_ground = True
                elif self.y_velocity < 0:
                    self.rect.top = platform.rect.bottom
                    self.y_velocity = 0

        # Проверка, находится ли игрок на земле
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.y_velocity = 0
            self.on_ground = True

    # Обработка столкновений игрока с платформами по горизонтали
    def handle_collision_x(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.rect.right > platform.rect.left and self.rect.left < platform.rect.left:
                    self.rect.right = platform.rect.left
                elif self.rect.left < platform.rect.right and self.rect.right > platform.rect.right:
                    self.rect.left = platform.rect.right

    # Обработка столкновений игрока с шипами
    def check_collision_spikes(self, spikes):
        for spike in spikes:
            if self.rect.colliderect(spike.rect):
                self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)  # Телепортируем на стартовую позицию


# Класс для платформ
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        # Создание изображения и прямоугольника для платформы
        self.image = pygame.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        # Позиционирование платформы
        self.rect.x = x
        self.rect.y = y


# Класс для ключа
class Key(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        # Создание изображения и прямоугольника для ключа
        self.image = pygame.Surface((width, height))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        # Позиционирование ключа
        self.rect.x = x
        self.rect.y = y


# Класс для двери
class Door(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        # Создание изображения и прямоугольника для двери
        self.image = pygame.Surface((width, height))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        # Позиционирование двери
        self.rect.x = x
        self.rect.y = y
        # Флаг, указывающий, что дверь открыта
        self.opened = False

    def check_collision(self, player):
        # Проверка столкновения игрока с дверью
        if self.rect.colliderect(player.rect) and player.has_key:
            self.opened = True
            self.image.fill(RED)  # Изменяем цвет двери на красный при открытии
            return True
        return False


# Класс для шипов
class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        # Создание изображения и прямоугольника для шипов
        self.image = pygame.Surface((width, height))
        self.image.fill(RED)  # Изменено на красный цвет
        self.rect = self.image.get_rect()
        # Позиционирование шипов
        self.rect.x = x
        self.rect.y = y


# Функция для запуска игрового процесса
def start_game():
    # Создание игрока
    player = Player()

    # Создание списка платформ
    platforms = [
        Platform(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20),
        Platform(10, 500, 100, 20),
        Platform(160, 400, 100, 20),
        Platform(10, 300, 100, 20),
        Platform(130, 200, 100, 20),
        Platform(630, 110, 100, 20),
        Platform(675, 400, 100, 20),
        Platform(550, 300, 100, 20),
        Platform(610, 200, 100, 20)
    ]

    # Создание списка шипов
    spikes = [
        Spike(250, 470, 20, 20),
        Spike(450, 370, 20, 20),
        Spike(700, 270, 20, 20)
    ]

    # Создание ключа
    key = Key(175, 160, 30, 30)

    # Создание двери
    door = Door(655, 10, 50, 100)

    all_sprites = pygame.sprite.Group()
    all_sprites.add(player, key)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        # Обновление игры
        player.update(platforms, spikes)

        # Проверяем столкновение с ключом
        collided_sprites = pygame.sprite.spritecollide(player, all_sprites, False)
        if collided_sprites:
            for sprite in collided_sprites:
                if isinstance(sprite, Key):  # Проверяем, что столкнулись с ключом
                    player.has_key = True
                    all_sprites.remove(sprite)  # Удаляем ключ из группы спрайтов

        # Проверяем столкновение с дверью
        if door.check_collision(player):
            # Выводим сообщение о победе
            font = pygame.font.Font(None, 36)
            text = font.render("Победа!", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            background_rect = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            pygame.draw.rect(screen, RED, background_rect)  # Отрисовываем фон для надписи
            screen.blit(text, text_rect)
            pygame.display.flip()

            pygame.time.delay(2000)  # Задержка для отображения сообщения о победе
            return  # Возвращаемся в главное меню

        # Отрисовка экрана
        screen.fill(BLACK)
        for platform in platforms:
            pygame.draw.rect(screen, WHITE, platform.rect)
        for spike in spikes:
            pygame.draw.rect(screen, RED, spike.rect)
        pygame.draw.rect(screen, RED, player.rect)
        pygame.draw.rect(screen, BLUE, door.rect)
        if not door.opened:
            for sprite in all_sprites:
                screen.blit(sprite.image, sprite.rect)
        pygame.display.flip()

        # Задержка для 60 кадров в секунду
        pygame.time.Clock().tick(60)


# Основной цикл программы
while True:
    if not main_menu():
        break
    start_game()

# Завершение Pygame
pygame.quit()
