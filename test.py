from itertools import count

import pygame
import sys
import random
import math

# Инициализация Pygame
pygame.init()
pygame.mixer.init()  # Инициализация микшера для звуков

# Загрузка музыки и звуков
pygame.mixer.music.load("background_music.mp3")

attack_sound = pygame.mixer.Sound("attack_sound.wav")
attack_sound.set_volume(0.5)  # Установите громкость на 50%
magic_cast_sound = pygame.mixer.Sound("magic_cast_sound.wav")
magic_cast_sound.set_volume(0.5)
magic_hit_sound = pygame.mixer.Sound("magic_hit_sound.wav")
magic_hit_sound.set_volume(0.5)

# Воспроизведение фоновой музыки
pygame.mixer.music.play(-1)  # Зацикливаем музыку

# Настройки экрана
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Мега RPG")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)dw
BLUE = (0, 0, 255)

# Шрифт
font = pygame.font.Font(None, 36)

class Projectile:
    def __init__(self, start_x, start_y, target_x, target_y, speed=5):
        self.x = start_x
        self.y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        try:
            self.image = pygame.image.load("projectile.png")
            self.image = pygame.transform.scale(self.image, (20, 20))
        except pygame.error as e:
            print(f"Ошибка загрузки изображения снаряда: {e}")
            self.image = pygame.Surface((20, 20))
            self.image.fill(BLUE)

        # Вычисляем направление движения
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        self.dx = (dx / distance) * speed if distance > 0 else 0
        self.dy = (dy / distance) * speed if distance > 0 else 0

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def check_collision(self, target):
        # Используем размеры текущего кадра анимации цели
        target_frame = target.idle_frames[target.current_frame]
        target_width = target_frame.get_width()
        target_height = target_frame.get_height()

        return (abs(self.x - target.x) < (target_width / 2 + self.image.get_width() / 2) and
                abs(self.y - target.y) < (target_height / 2 + self.image.get_height() / 2))
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.action()
                return True
        return False
def show_level_up_menu(hero):
    # Цвета
    WINDOW_COLOR = (50, 50, 50)
    BUTTON_COLOR = (100, 100, 100)
    BUTTON_HOVER_COLOR = (150, 150, 150)

    # Размеры окна
    window_width = 400
    window_height = 500
    window_x = (SCREEN_WIDTH - window_width) // 2
    window_y = (SCREEN_HEIGHT - window_height) // 2

    # Создаем кнопки для улучшения характеристик
    buttons = [
        Button(window_x + 50, window_y + 100, 300, 50, "Физическая атака +5",
               BUTTON_COLOR, BUTTON_HOVER_COLOR, lambda: hero.__setattr__("physical_attack", hero.physical_attack + 5)),
        Button(window_x + 50, window_y + 170, 300, 50, "Регенерация маны +2",
               BUTTON_COLOR, BUTTON_HOVER_COLOR, lambda: hero.__setattr__("mana_regen", hero.mana_regen + 2)),
        Button(window_x + 50, window_y + 240, 300, 50, "Манапул +20",
               BUTTON_COLOR, BUTTON_HOVER_COLOR, lambda: hero.__setattr__("max_mana", hero.max_mana + 20) or hero.__setattr__("mana", hero.mana + 20)),
        Button(window_x + 50, window_y + 310, 300, 50, "Магическая атака +5",
               BUTTON_COLOR, BUTTON_HOVER_COLOR, lambda: hero.__setattr__("magic_power", hero.magic_power + 5)),
        Button(window_x + 50, window_y + 380, 300, 50, "Защита +3",
               BUTTON_COLOR, BUTTON_HOVER_COLOR, lambda: hero.__setattr__("defense", hero.defense + 3)),
    ]

    # Флаг для отображения окна
    level_up_menu_active = True


    while level_up_menu_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Проверяем нажатия на кнопки
            for button in buttons:
                if button.check_click(event):
                    level_up_menu_active = False  # Закрываем окно после выбора

        # Отрисовка окна
        pygame.draw.rect(screen, WINDOW_COLOR, (window_x, window_y, window_width, window_height))
        font = pygame.font.Font(None, 48)
        title = font.render("Выберите улучшение", True, WHITE)
        screen.blit(title, (window_x + 50, window_y + 20))

        # Отрисовка кнопок
        for button in buttons:
            button.draw(screen)

        pygame.display.flip()
class Character:
    def __init__(self, x, y, idle_frames, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.attack_range = 4
        self.magic_power = 20  # Магическая атака
        self.physical_attack = 10  # Физическая атака
        self.mana = 100  # Текущий манапул
        self.max_mana = 100  # Максимальный манапул
        self.mana_regen = 10  # Регенерация маны
        self.defense = 5  # Защита
        self.projectiles = []
        self.mana = 100
        self.lvl = 1
        self.exp = 0
        self.next_lvl = 100

        # Анимация ожидания
        self.idle_frames = []  # Список кадров анимации
        self.current_frame = 0  # Текущий кадр анимации
        self.frame_timer = 0  # Таймер для отслеживания времени между кадрами
        self.animation_speed = 0.1  # Скорость смены кадров (в секундах)
        self.load_idle_animation(idle_frames)

    def load_idle_animation(self, idle_frames):
        """
        Загружает кадры анимации ожидания.
        idle_frames — список путей к файлам или спрайт-лист.
        """
        try:
            # Если используется список отдельных файлов
            if isinstance(idle_frames, list):
                for frame_path in idle_frames:
                    frame = pygame.image.load(frame_path)
                    frame = pygame.transform.scale(frame, (40, 40))
                    self.idle_frames.append(frame)
            # Если используется спрайт-лист
            elif isinstance(idle_frames, str):
                sheet = pygame.image.load(idle_frames).convert_alpha()
                frame_width = sheet.get_width() // 4  # Предположим, что в листе 4 кадра
                frame_height = sheet.get_height()
                for i in range(4):  # Загружаем 4 кадра
                    frame = sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
                    frame = pygame.transform.scale(frame, (40, 40))
                    self.idle_frames.append(frame)
        except pygame.error as e:
            print(f"Ошибка загрузки анимации: {e}")
            # Если загрузка не удалась, создаем заглушку
            frame = pygame.Surface((40, 40))
            frame.fill(RED)
            self.idle_frames.append(frame)

    def update_animation(self, dt):
        """
        Обновляет текущий кадр анимации.
        dt — время, прошедшее с последнего кадра (в секундах).
        """
        self.frame_timer += dt
        if self.frame_timer >= self.animation_speed:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.idle_frames)

    def draw(self, screen):
        """
        Отрисовывает текущий кадр анимации.
        """
        screen.blit(self.idle_frames[self.current_frame], (self.x, self.y))
        self.draw_health(screen)
        self.draw_mana(screen)
        for projectile in self.projectiles:
            projectile.draw(screen)

    def draw_health(self, screen):
        health_text = font.render(f"HP: {self.health}", True, RED)
        screen.blit(health_text, (self.x, self.y - 40))

    def draw_mana(self, screen):
        mana_text = font.render(f"MP: {self.mana}", True, BLUE)
        screen.blit(mana_text, (self.x, self.y - 20))

    def move(self, dx, dy):
        # Используем размеры текущего кадра анимации
        current_frame = self.idle_frames[self.current_frame]
        frame_width = current_frame.get_width()
        frame_height = current_frame.get_height()

        # Проверяем границы экрана
        if 0 <= self.x + dx <= SCREEN_WIDTH - frame_width:
            self.x += dx
        if 0 <= self.y + dy <= SCREEN_HEIGHT - frame_height:
            self.y += dy

    def attack(self, target):
        if self.distance(target) <= self.attack_range * 40:
            target.health -= self.physical_attack
            attack_sound.play()  # Воспроизведение звука атаки
            print(f"Атака! У {target} осталось {target.health} HP.")
        else:
            print(f"Цель слишком далеко для атаки! Расстояние: {self.distance(target)}")

    def heal(self):
        self.health += self.magic_power

    def cast_magic(self, target):
        if self.mana > 0:
            if self.distance(target) <= (self.attack_range + 5) * 40:
                projectile = Projectile(self.x, self.y, target.x, target.y)
                self.projectiles.append(projectile)
                self.mana -= 20
                magic_cast_sound.play()  # Воспроизведение звука кастинга магии
                print(f"Запущен магический снаряд!")
            else:
                print(f"Цель слишком далеко для магии! Расстояние: {self.distance(target)}")
        else:
            print('Нам нужна мана! БОЛЬШЕ МАНЫ!')
    def regen_mana(self):
        if self.mana < self.max_mana:
            self.mana += self.mana_regen


    def update_projectiles(self, target):
        for projectile in self.projectiles[:]:
            projectile.move()
            if projectile.check_collision(target):
                target.health -= self.magic_power
                magic_hit_sound.play()  # Воспроизведение звука попадания магии
                print(f"Магия попала! У {target} осталось {target.health} HP.")
                self.projectiles.remove(projectile)

    def distance(self, target):
        return math.sqrt((self.x - target.x) ** 2 + (self.y - target.y) ** 2)  # Исправлено на ** 2

    def lvl_up(self, exp):
        self.exp += exp
        if self.exp >= self.next_lvl:
            self.exp -= self.next_lvl
            self.lvl += 1
            self.next_lvl = int(self.next_lvl * 1.5)  # Увеличиваем опыт для следующего уровня
            return True  # Возвращаем True, чтобы показать, что уровень повышен
        return False


class Enemy(Character):
    def __init__(self, x, y, image_path, health=100):
        super().__init__(x, y, image_path, health)
        self.attack_range = 2

    def random_move(self):
        dx = random.choice([-1, 0, 1]) * 40
        dy = random.choice([-1, 0, 1]) * 40
        self.move(dx, dy)

    def attack(self, target):
        if self.distance(target) <= self.attack_range * 40:
            target.health -= 15
            print(f"Враг атакует! У {target} осталось {target.health} HP.")
        else:
            print(f"Цель слишком далеко для атаки врага! Расстояние: {self.distance(target)}")


def main():
    clock = pygame.time.Clock()
    try:
        background = pygame.transform.scale(pygame.image.load("background.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print(f"Ошибка загрузки фона: {e}")
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background.fill(BLACK)

    # Список кадров анимации ожидания для героя
    hero_idle_frames = [f'hero_frame/{i}.jpeg' for i in range(1, 17)]
    # Список кадров анимации ожидания для врага
    enemy_idle_frames = [f'enemy_frame/{i}.jpeg' for i in range(1, 49)]
    enemy_idle_frames2 = [f'enemy2_frame/{i}.jpeg' for i in range(1, 5)]


    hero = Character(400, 300, hero_idle_frames, health=200)
    enemy = Enemy(200, 200, enemy_idle_frames, health=10)

    log = []
    turn = "player"
    counter = 0

    while True:
        dt = clock.tick(60) / 1000  # Время в секундах

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if turn == "player" and event.type == pygame.KEYDOWN:
                hero.regen_mana()
                if event.key == pygame.K_UP:
                    hero.move(0, -40)
                    log.append("Герой движется вверх")
                    turn = "enemy"
                elif event.key == pygame.K_DOWN:
                    hero.move(0, 40)
                    log.append("Герой движется вниз")
                    turn = "enemy"
                elif event.key == pygame.K_LEFT:
                    hero.move(-40, 0)
                    log.append("Герой движется влево")
                    turn = "enemy"
                elif event.key == pygame.K_RIGHT:
                    hero.move(40, 0)
                    log.append("Герой движется вправо")
                    turn = "enemy"
                elif event.key == pygame.K_a:
                    hero.attack(enemy)
                    log.append("Герой атакует врага")
                    turn = "enemy"
                elif event.key == pygame.K_m:
                    hero.cast_magic(enemy)
                    log.append("Герой использует магию")
                    turn = "enemy"
                elif event.key == pygame.K_h:
                    hero.heal()
                    log.append("Герой использует лечение")
                    turn = "enemy"

        # Обновление анимаций
        hero.update_animation(dt)
        enemy.update_animation(dt)

        # Обновление снарядов
        hero.update_projectiles(enemy)
        enemy.update_projectiles(hero)

        # Отрисовка фона
        screen.blit(background, (0, 0))

        # Отрисовка персонажей
        hero.draw(screen)
        enemy.draw(screen)

        # Отрисовка логов
        for i, message in enumerate(log[-5:]):
            log_text = font.render(message, True, WHITE)
            screen.blit(log_text, (10, 10 + i * 30))

        # Проверка на победу или поражение
        if hero.health <= 0:
            log.append("Герой погиб! Игра окончена.")
            pygame.display.flip()
            pygame.time.delay(2000)
            pygame.quit()
            sys.exit()
        elif enemy.health <= 0:
            if counter == 0:
                log.append("Враг побежден! Вы выиграли!")
                background = pygame.transform.scale(pygame.image.load("back.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
                if hero.lvl_up(200):  # Проверяем, повысился ли уровень
                    log.append(f"Герой достиг уровня {hero.lvl}!")
                    show_level_up_menu(hero)  # Отображаем окно прокачки
                enemy = Enemy(200, 200, enemy_idle_frames, health=10)
            elif counter == 1:
                log.append("Враг побежден! Вы выиграли!")
                if hero.lvl_up(300):  # Проверяем, повысился ли уровень
                    log.append(f"Герой достиг уровня {hero.lvl}!")
                    show_level_up_menu(hero)  # Отображаем окно прокачки
                background = pygame.transform.scale(pygame.image.load("back.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
                enemy = Enemy(200, 200, enemy_idle_frames2, health=10)
            else:
                log.append("Враг побежден! Вы выиграли!")
                if hero.lvl_up(150 * counter):  # Проверяем, повысился ли уровень
                    log.append(f"Герой достиг уровня {hero.lvl}!")
                    show_level_up_menu(hero)  # Отображаем окно прокачки
                background = pygame.transform.scale(pygame.image.load("back.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
                enemy = Enemy(200, 200, enemy_idle_frames2, health=10)
            counter += 1

        if turn == "enemy":
            enemy.random_move()
            enemy.attack(hero)
            log.append("Враг атакует героя")
            pygame.time.delay(100)
            turn = "player"

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
