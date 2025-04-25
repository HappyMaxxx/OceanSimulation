import math
import random

import pygame

from core.settings import CRUSTACEAN_LIFETIME, HEIGHT, PLANKTON_LIFETIME, WIDTH


class Crustacean:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy_value = random.randint(25, 40)
        self.speed = random.uniform(0.5, 1.0)
        self.direction = random.uniform(0, 2 * math.pi)
        self.lifetime = round(random.uniform(*CRUSTACEAN_LIFETIME))

    def update(self):
        if self.y < HEIGHT // 3:
            self.y += self.speed / 2
            random_x = random.uniform(-self.speed, self.speed)
            self.x += random_x
            
        else:
            self.x += math.cos(self.direction) * self.speed
            self.y += math.sin(self.direction) * self.speed

        self.lifetime -= 2

        if self.x < 0 or self.x > WIDTH:
            self.direction = math.pi - self.direction

        if self.y < HEIGHT // 3:
            self.direction = math.atan2(math.sin(self.direction) * -1, math.cos(self.direction))
        elif self.y > HEIGHT - 10:
            self.direction = math.atan2(math.sin(self.direction) * -1, math.cos(self.direction))

    def draw(self, screen):
        pygame.draw.circle(screen, (150, 75, 0), (int(self.x), int(self.y)), 4)  


class Plankton:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy_value = random.randint(3, 7)  
        self.lifetime = round(random.uniform(*PLANKTON_LIFETIME))

    def update(self):
        self.lifetime -= 3

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 200, 200), (int(self.x), int(self.y)), 2)
