import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = 0.8
JUMP_STRENGTH = -15
PLAYER_SPEED = 5
ENEMY_SPEED = 2

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BLACK = (0, 0, 0)

class SoundManager:
    def __init__(self):
        self.sounds = {}
        try:
            self.create_jump_sound()
            self.create_coin_sound()
            self.create_death_sound()
        except Exception:
            print("Sound initialization failed; continuing without sound.")

    def create_jump_sound(self):
        duration = 0.1
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = []
        for i in range(frames):
            wave = 4096 * math.sin(2 * math.pi * (440 + i*2) * i / sample_rate)
            arr.append([int(wave)]*2)
        sound = pygame.sndarray.make_sound(pygame.sndarray.array(arr, dtype='int16'))
        self.sounds['jump'] = sound

    def create_coin_sound(self):
        duration = 0.2
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = []
        for i in range(frames):
            wave = 2048 * math.sin(2 * math.pi * (800 + i*3) * i / sample_rate)
            arr.append([int(wave)]*2)
        sound = pygame.sndarray.make_sound(pygame.sndarray.array(arr, dtype='int16'))
        self.sounds['coin'] = sound

    def create_death_sound(self):
        duration = 0.5
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = []
        for i in range(frames):
            wave = 3072 * math.sin(2 * math.pi * (200 - i*0.5) * i / sample_rate)
            arr.append([int(wave)]*2)
        sound = pygame.sndarray.make_sound(pygame.sndarray.array(arr, dtype='int16'))
        self.sounds['death'] = sound

    def play(self, sound_name):
        snd = self.sounds.get(sound_name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = random.uniform(-3, 3)
        self.vel_y = random.uniform(-5, -2)
        self.life = 30
        self.max_life = 30
        self.size = random.randint(2, 4)

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.2
        self.life -= 1
        return self.life > 0

    def draw(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.size)

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.collected = False
        self.bob_offset = 0
        self.bob_speed = 0.1

    def update(self):
        if not self.collected:
            self.bob_offset += self.bob_speed
            self.rect.y = self.y + math.sin(self.bob_offset) * 3

    def draw(self, screen):
        if not self.collected:
            center = (self.rect.centerx, self.rect.centery)
            pygame.draw.circle(screen, YELLOW, center, 10)
            pygame.draw.circle(screen, ORANGE, center, 8)
            pygame.draw.circle(screen, YELLOW, center, 5)

class Enemy:
    def __init__(self, x, y, left, right):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 24
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.vel_x = ENEMY_SPEED
        self.left = left
        self.right = right
        self.direction = 1

    def update(self):
        self.x += self.vel_x * self.direction
        if self.x <= self.left or self.x >= self.right - self.width:
            self.direction *= -1
        self.rect.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, PURPLE, self.rect)
        eye_y = int(self.y + 6)
        pygame.draw.circle(screen, WHITE, (int(self.x + 6), eye_y), 2)
        pygame.draw.circle(screen, WHITE, (int(self.x + 18), eye_y), 2)
        pygame.draw.circle(screen, BLACK, (int(self.x + 6), eye_y), 1)
        pygame.draw.circle(screen, BLACK, (int(self.x + 18), eye_y), 1)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 48
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.alive = True

    def update(self, platforms, enemies):
        if not self.alive:
            return None
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.on_ground = False
            self.vel_y = JUMP_STRENGTH
            return "jump"

        self.vel_y += GRAVITY
        self.x += self.vel_x
        self.y += self.vel_y
        self.rect.x, self.rect.y = self.x, self.y

        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_y > 0 and self.rect.bottom <= plat.rect.top + 10:
                    self.y = plat.rect.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0 and self.rect.top >= plat.rect.bottom - 10:
                    self.y = plat.rect.bottom
                    self.vel_y = 0
                else:
                    if self.vel_x > 0:
                        self.x = plat.rect.left - self.width
                    elif self.vel_x < 0:
                        self.x = plat.rect.right

        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
        if self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.vel_y = 0
            self.on_ground = True

        self.rect.x, self.rect.y = self.x, self.y

        for e in enemies:
            if self.rect.colliderect(e.rect):
                self.alive = False
                return "death"

        return None

    def draw(self, screen):
        if self.alive:
            pygame.draw.rect(screen, RED, self.rect)
            pygame.draw.circle(screen, WHITE, (int(self.x + 8), int(self.y + 12)), 3)
            pygame.draw.circle(screen, WHITE, (int(self.x + 24), int(self.y + 12)), 3)
        else:
            pygame.draw.rect(screen, (100, 0, 0), self.rect)
            pygame.draw.line(screen, WHITE, (int(self.x + 5), int(self.y + 9)), (int(self.x + 11), int(self.y + 15)), 2)
            pygame.draw.line(screen, WHITE, (int(self.x + 11), int(self.y + 9)), (int(self.x + 5), int(self.y + 15)), 2)
            pygame.draw.line(screen, WHITE, (int(self.x + 21), int(self.y + 9)), (int(self.x + 27), int(self.y + 15)), 2)
            pygame.draw.line(screen, WHITE, (int(self.x + 27), int(self.y + 9)), (int(self.x + 21), int(self.y + 15)), 2)

class Platform:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.rect)
        pygame.draw.rect(screen, BROWN, self.rect, 3)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Enhanced Platformer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.sound = SoundManager()
        self.reset_game()

    def reset_game(self):
        self.player = Player(100, SCREEN_HEIGHT - 100)
        self.platforms = [
            Platform(200, SCREEN_HEIGHT - 150, 150, 20),
            Platform(400, SCREEN_HEIGHT - 250, 150, 20),
            Platform(600, SCREEN_HEIGHT - 180, 100, 20),
            Platform(300, SCREEN_HEIGHT - 350, 200, 20),
            Platform(550, SCREEN_HEIGHT - 400, 120, 20),
            Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50),
        ]
        self.coins = [
            Coin(250, SCREEN_HEIGHT - 180),
            Coin(450, SCREEN_HEIGHT - 280),
            Coin(630, SCREEN_HEIGHT - 210),
            Coin(380, SCREEN_HEIGHT - 380),
            Coin(580, SCREEN_HEIGHT - 430),
            Coin(150, SCREEN_HEIGHT - 100),
            Coin(700, SCREEN_HEIGHT - 100),
        ]
        self.enemies = [
            Enemy(220, SCREEN_HEIGHT - 174, 200, 350),
            Enemy(420, SCREEN_HEIGHT - 274, 400, 550),
            Enemy(320, SCREEN_HEIGHT - 374, 300, 500),
        ]
        self.score = 0
        self.particles = []
        self.game_over = False

    def handle_coin_collection(self):
        for c in self.coins:
            if not c.collected and self.player.rect.colliderect(c.rect):
                c.collected = True
                self.score += 10
                self.sound.play('coin')
                for _ in range(8):
                    self.particles.append(Particle(c.rect.centerx, c.rect.centery))

    def update_particles(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw_ui(self):
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 50))
        if not self.game_over:
            inst = self.font.render("Move: ←/→ or WASD • Jump: ↑/W/Space", True, WHITE)
            self.screen.blit(inst, (10, 10))
        else:
            go = self.big_font.render("GAME OVER", True, WHITE)
            rt = self.font.render("Press R to Restart or ESC to Quit", True, WHITE)
            rect_go = go.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            rect_rt = rt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0,0))
            self.screen.blit(go, rect_go)
            self.screen.blit(rt, rect_rt)

    def run(self):
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        running = False
                    elif ev.key == pygame.K_r and self.game_over:
                        self.reset_game()

            if not self.game_over:
                se = self.player.update(self.platforms, self.enemies)
                if se:
                    self.sound.play(se)
                    if se == "death":
                        self.game_over = True

                for e in self.enemies:
                    e.update()
                for c in self.coins:
                    c.update()
                self.handle_coin_collection()
                self.update_particles()

            # Drawing
            self.screen.fill(BLUE)
            for p in self.platforms:
                p.draw(self.screen)
            for c in self.coins:
                c.draw(self.screen)
            for e in self.enemies:
                e.draw(self.screen)
            for pt in self.particles:
                pt.draw(self.screen)
            self.player.draw(self.screen)
            self.draw_ui()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()
