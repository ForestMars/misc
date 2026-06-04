
import pygame
import random

# Initialize pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 400, 600
FPS = 60
GRAVITY = 0.25
JUMP_STRENGTH = -7
PIPE_SPEED = 3
PIPE_FREQUENCY = 1800  # milliseconds between pipes
PIPE_GAP = 150

# Colors
SKY_BLUE = (113, 197, 207)
GREEN = (111, 248, 109)
WHITE = (255, 255, 255)

class Bird:
    def __init__(self):
        self.x = WIDTH // 4
        self.y = HEIGHT // 2
        self.velocity = 0
        self.size = 30

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def update(self):
        # Update bird position based on velocity and gravity
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Boundary checks (top/bottom)
        if self.y <= 0:
            self.y = 0
            self.velocity = 0
        elif self.y >= HEIGHT - 50:  # Floor collision
            self.y = HEIGHT - 50
            self.velocity = 0

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 0), (self.x + self.size//2, int(self.y)), self.size//2)
        # Draw a simple beak
        pygame.draw.polygon(screen, (255, 165, 0), 
                           [(self.x + self.size*3//4, int(self.y - self.size//4)),
                            (self.x + self.size*2, int(self.y)),
                            (self.x + self.size*3//4, int(self.y + self.size//4))])
        # Draw eyes
        pygame.draw.circle(screen, WHITE, (int(self.x + self.size*0.7), int(self.y - self.size//6)), 5)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + self.size*0.8), int(self.y - self.size//6)), 2)

class Pipe:
    def __init__(self):
        self.gap_y = random.randint(150, HEIGHT - 300)
        self.x = WIDTH
        self.width = 70
        self.passed = False

    def update(self):
        # Move pipe to the left
        self.x -= PIPE_SPEED
        
    def draw(self, screen):
        # Draw top pipe
        pygame.draw.rect(screen, GREEN, (self.x, 0, self.width, self.gap_y - PIPE_GAP//2))
        # Draw bottom pipe
        pygame.draw.rect(screen, GREEN, (self.x, self.gap_y + PIPE))
