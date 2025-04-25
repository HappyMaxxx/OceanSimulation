import math
import random
from typing import TYPE_CHECKING

import pygame

from core.settings import (
    ALGAE_GROW,
    CURRENT_MOVEMENT_FACTOR,
    DEAD_ALGAE_LIFETIME,
    HEIGHT,
    MAX_ALGAE,
    WIDTH,
)

if TYPE_CHECKING:
    from core.simulation import Simulation

class Algae:
    def __init__(self, x, base_y, simulation: "Simulation"):
        self.root_x = x
        self.base_y = base_y
        self.simulation = simulation
        self.segments = [(x, base_y)]
        self.lowest_y = base_y 
        self.energy_value = 10
        self.growth_timer = round(random.uniform(*ALGAE_GROW))
        self.max_height = random.randint(int(HEIGHT * 0.3), int(HEIGHT * 0.5))
        self.branch_chance = 0.1
        self.is_alive = True

    def grow(self):  
        if not self.is_alive or self.simulation.day_phase == "Night":
            return

        if self.growth_timer > 0:
            self.growth_timer -= 3
            return

        top_y = min(seg[1] for seg in self.segments)
        if self.base_y - top_y >= self.max_height:
            return

        season = self.simulation.seasons[self.simulation.current_season_index]
        growth_modifier = {"Spring": 1.1, "Summer": 1.2, "Autumn": 0.9, "Winter": 0.7}[season]

        top_segment = min(self.segments, key=lambda s: s[1])
        new_x = top_segment[0] + random.uniform(-2, 2)
        new_y = top_segment[1] - random.uniform(4, 7) * growth_modifier
        
        self.segments.append((new_x, new_y))
        self.simulation.add_segment_to_grid(new_x, new_y, self)
        self.energy_value += random.randint(1, 3)
        if new_y < self.lowest_y:
            self.lowest_y = new_y 
        
        if random.random() < self.branch_chance:
            branch_x = top_segment[0] + random.uniform(-5, 5)
            branch_y = top_segment[1] - random.uniform(2, 5) * growth_modifier
            self.segments.append((branch_x, branch_y))
            self.simulation.add_segment_to_grid(branch_x, branch_y, self)
            self.energy_value += random.randint(1, 2)
            if branch_y < self.lowest_y:
                self.lowest_y = branch_y  

        self.growth_timer = round(random.uniform(*ALGAE_GROW))
    
    def check_root(self):
        return any(seg[1] >= self.base_y - 4 for seg in self.segments[:5])

    def update(self, algae_list, dead_algae_parts):
        if not self.check_root() and self.is_alive:
            self.is_alive = False
            for seg_x, seg_y in self.segments[:]:
                if seg_y < self.base_y - 4:
                    if random.random() < 0.4:
                        dead_algae_parts.append(DeadAlgaePart(seg_x, seg_y, self.simulation))
                self.simulation.remove_segment_from_grid(seg_x, seg_y, self)
            self.segments.clear()
            self.lowest_y = float('inf')

        if self.is_alive:
            if random.random() < 0.6:
                self.grow()
            if len(algae_list) < MAX_ALGAE and random.random() < 0.01:
                new_x = self.root_x + random.randint(-20, 20)
                if 0 <= new_x <= WIDTH:
                    new_algae = Algae(new_x, self.base_y, self.simulation)
                    algae_list.append(new_algae)
                    self.simulation.add_segment_to_grid(new_x, self.base_y, new_algae)

    def draw(self, screen):
        if not self.segments:
            return
        
        color = (0, 150, 0) if self.is_alive else (0, 125, 0)
        step = max(1, len(self.segments) // 10) 
        points = [(int(x), int(y)) for i, (x, y) in enumerate(self.segments) if i % step == 0]
        
        if len(points) >= 2:
            pygame.draw.lines(screen, color, False, points, 2)
        elif len(points) == 1:
            pygame.draw.circle(screen, color, points[0], 2)


class DeadAlgaePart:
    def __init__(self, x, y, simulation):
        self.x = x
        self.y = y
        self.simulation = simulation
        self.energy_value = random.randint(2, 5) 
        self.float_speed = random.uniform(0.2, 0.5)  
        self.lifetime = round(random.uniform(*DEAD_ALGAE_LIFETIME))

    def update(self):
        strength, direction = self.simulation.current_grid.get_current_at(self.x, self.y)
        current_x = strength * math.cos(direction)
        current_y = strength * math.sin(direction)
        
        self.x += current_x * CURRENT_MOVEMENT_FACTOR
        self.y += current_y * CURRENT_MOVEMENT_FACTOR - (self.float_speed * 1.2 - 0.02)
        self.y -= self.float_speed 
        self.lifetime -= 2

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 125, 0), (int(self.x), int(self.y)), 2)