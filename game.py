import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Platformer")

clock = pygame.time.Clock()

# Load images
player_img = pygame.image.load("assets/player.png").convert_alpha()
background_img = pygame.image.load("assets/background.png").convert()
platform_img = pygame.image.load("assets/platform.png").convert_alpha()

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 500
        self.vel_y = 0
        self.jumping = False

    def update(self):
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if keys[pygame.K_LEFT]:
            dx = -5
        if keys[pygame.K_RIGHT]:
            dx = 5

        # Gravity
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Jump
        if keys[pygame.K_SPACE] and not self.jumping:
            self.vel_y = -15
            self.jumping = True

        # Collision with platforms
        for platform in platform_group:
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                dy = 0
                self.jumping = False

        # Update position
        self.rect.x += dx
        self.rect.y += dy

        # Boundaries
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.jumping = False

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = platform_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Sprite groups
player = Player()
player_group = pygame.sprite.Group()
player_group.add(player)

platform_group = pygame.sprite.Group()
platform_group.add(Platform(0, SCREEN_HEIGHT - 40))
platform_group.add(Platform(200, 450))
platform_group.add(Platform(400, 300))
platform_group.add(Platform(600, 200))

# Game loop
running = True
while running:
    clock.tick(FPS)

    screen.blit(background_img, (0, 0))

    player_group.update()
    player_group.draw(screen)
    platform_group.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

pygame.quit()
sys.exit()
