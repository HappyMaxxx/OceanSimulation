import pygame
import random
import math
import tkinter as tk
from threading import Thread

from settings import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fish Evolution - Food Decay")
font = pygame.font.Font(None, 24)
clock = pygame.time.Clock()


class Algae:
    def __init__(self, x, base_y):
        self.root_x = x
        self.base_y = base_y
        self.segments = [(x, base_y)]
        self.energy_value = 7
        self.growth_timer = random.randint(50, 100)
        self.max_height = random.randint(int(HEIGHT * 0.3), int(HEIGHT * 0.5))
        self.branch_chance = 0.1
        self.is_alive = True

    def grow(self):
        if not self.is_alive:
            return
        
        if self.growth_timer > 0:
            self.growth_timer -= 1
            return
        
        top_y = min(seg[1] for seg in self.segments)
        if self.base_y - top_y >= self.max_height:
            return

        top_segment = min(self.segments, key=lambda s: s[1])
        new_x = top_segment[0] + random.uniform(-2, 2)
        new_y = top_segment[1] - random.uniform(2, 5)
        
        self.segments.append((new_x, new_y))
        self.energy_value += random.randint(1, 3)
        
        if random.random() < self.branch_chance:
            branch_x = top_segment[0] + random.uniform(-5, 5)
            branch_y = top_segment[1] - random.uniform(2, 5)
            self.segments.append((branch_x, branch_y))
            self.energy_value += random.randint(1, 2)

        self.growth_timer = random.randint(100, 150)

    def check_root(self):
        return any(seg[1] >= self.base_y - 4 for seg in self.segments)

    def update(self, algae_list, dead_algae_parts):
        if not self.check_root() and self.is_alive:
            self.is_alive = False

            for seg_x, seg_y in self.segments[:]:
                if seg_y < self.base_y - 5: 
                    dead_algae_parts.append(DeadAlgaePart(seg_x, seg_y))
            self.segments.clear() 

        if self.is_alive:
            self.grow()
            if len(algae_list) < MAX_ALGAE and random.random() < 0.01:
                new_x = self.root_x + random.randint(-20, 20)
                if 0 <= new_x <= WIDTH:
                    algae_list.append(Algae(new_x, self.base_y))

    def draw(self, screen):
        if not self.segments:
            return
        
        color = (0, 150, 0) if self.is_alive else (0, 125, 0)
        for i in range(len(self.segments) - 1):
            pygame.draw.line(screen, color, 
                            (int(self.segments[i][0]), int(self.segments[i][1])), 
                            (int(self.segments[i + 1][0]), int(self.segments[i + 1][1])), 2)


class DeadAlgaePart:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy_value = random.randint(2, 5) 
        self.float_speed = random.uniform(0.2, 0.5)  
        self.lifetime = random.randint(500, 800)  

    def update(self):
        self.y -= self.float_speed 
        self.lifetime -= 1

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 125, 0), (int(self.x), int(self.y)), 2)


class Crustacean:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy_value = random.randint(25, 40)
        self.speed = random.uniform(0.5, 1.0)
        self.direction = random.uniform(0, 2 * math.pi)
        self.lifetime = random.randint(300, 500) 

    def update(self):
        self.x += math.cos(self.direction) * self.speed
        self.y += math.sin(self.direction) * self.speed
        self.lifetime -= 1
        if self.x < 0 or self.x > WIDTH:
            self.direction = math.pi - self.direction 
        self.y = max(HEIGHT // 3, min(HEIGHT - 10, self.y))  

    def draw(self, screen):
        pygame.draw.circle(screen, (150, 75, 0), (int(self.x), int(self.y)), 4)  


class Plankton:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy_value = random.randint(3, 7)  
        self.lifetime = random.randint(150, 200)  

    def update(self):
        self.lifetime -= 1

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 200, 200), (int(self.x), int(self.y)), 2)


class Fish:
    def __init__(self, x, y, energy, genome=None):
        self.x = x
        self.y = y
        self.energy = min(energy, MAX_ENERGY)
        
        if genome is None:
            self.genome = {
                "speed": [random.uniform(0, 1), random.uniform(0, 1)],
                "size": [random.uniform(0, 1), random.uniform(0, 1)],
                "vision": [random.uniform(0, 1), random.uniform(0, 1)],
                "metabolism": [random.uniform(0, 1), random.uniform(0, 1)],
                "digestion": [random.uniform(0, 1), random.uniform(0, 1)],
                "reproduction": [random.uniform(0, 1), random.uniform(0, 1)],
                "defense": [random.uniform(0, 1), random.uniform(0, 1)],
                "color": [random.uniform(0, 1), random.uniform(0, 1)],
                "preferred_depth": [random.uniform(0, 1), random.uniform(0, 1)],
                "predator": [random.uniform(0, 1), random.uniform(0, 1)]
            }
        else:
            self.genome = genome
        
        self.is_predator = (sum(self.genome["predator"]) / 2) > 0.5
        
        self.is_male = random.choice([True, False])
        
        self.age = 0
        self.max_size = (sum(self.genome["size"]) / 2) * (10 if self.is_predator else 6) + (5 if self.is_predator else 3)
        
        if self.is_predator:
            self.speed = (sum(self.genome["speed"]) / 2) * 1.5 + 0.5
            self.size = 3
            self.vision = (sum(self.genome["vision"]) / 2) * 100 + 50
            self.mate_vision = (sum(self.genome["vision"]) / 2) * 150 + 75
            self.reproduction_rate = (sum(self.genome["reproduction"]) / 2) * 0.25
            self.energy_threshold = 40
        else:
            self.speed = (sum(self.genome["speed"]) / 2) * 2.5 + 1
            self.size = 2
            self.vision = (sum(self.genome["vision"]) / 2) * 60 + 30
            self.mate_vision = (sum(self.genome["vision"]) / 2) * 80 + 40
            self.reproduction_rate = (sum(self.genome["reproduction"]) / 2) * 0.45
            self.energy_threshold = 20
        
        self.metabolism = sum(self.genome["metabolism"]) / 2
        self.digestion = sum(self.genome["digestion"]) / 2
        self.defense = sum(self.genome["defense"]) / 2
        self.preferred_depth = (sum(self.genome["preferred_depth"]) / 2) * HEIGHT
        
        # Генетичні взаємодії
        # Висока швидкість зменшує захист
        self.defense *= (1 - sum(self.genome["speed"]) / 4)  # Швидкість зменшує захист до 25%
        # Великий розмір погіршує маневреність
        self.turn_speed = 0.1 if not self.is_predator else 0.08
        self.turn_speed *= (1 - sum(self.genome["size"]) / 4)  # Розмір зменшує маневреність до 25%
        
        # Енергетичний штраф за надмірний розвиток (якщо середнє значення гена > 0.8)
        self.energy_penalty = 0
        for trait in ["speed", "size", "vision", "metabolism"]:
            avg = sum(self.genome[trait]) / 2
            if avg > 0.8:
                self.energy_penalty += (avg - 0.8) * 0.5  # Штраф до витрат енергії
        
        # Епігенетика: адаптивний метаболізм
        self.base_metabolism = self.metabolism
        self.food_scarcity_timer = 0  
        
        # Статевий диморфізм: модифікація характеристик залежно від статі
        if self.is_male:
            # Самці яскравіші, але повільніші
            self.color_modifier = 1.5
            self.speed *= 0.9  # Зменшення швидкості на 10%
        else:
            # Самки краще маскуються
            self.color_modifier = 0.7
            self.defense *= 1.1  # Збільшення захисту на 10%
        
        self.speed *= (1 - self.size / 20)
        self.speed += self.metabolism * 0.5
        
        self.color = (
            max(0, min(255, int(self.genome["color"][0] * (100 if self.is_predator else 255) * self.color_modifier))),
            max(0, min(255, int((100 + self.size * 10) * (0.5 if self.is_predator else 1) * self.color_modifier))),
            max(0, min(255, int(self.genome["color"][1] * (100 if self.is_predator else 255) * self.color_modifier)))
        )
        
        self.direction = random.uniform(-math.pi/2, math.pi/2)
        self.ready_to_mate = False
        self.tail_angle = 0
        self.tail_speed = 0.2
        self.is_dead = False
        self.float_speed = 0.5

        base_lifespan = self.max_size * 4 
        variation = random.uniform(0.8, 1.2)  
        self.max_age = base_lifespan * variation * (1.2 if self.is_predator else 1.0)
        
        base_reproduction_age = self.max_size * 0.4
        repro_variation = random.uniform(0.7, 1.3)  
        self.min_reproduction_age = base_reproduction_age * repro_variation * (1.5 if self.is_predator else 1.0)

    def grow(self):
        if not self.is_dead and self.size < self.max_size:
            growth_rate = 0.01 * (self.energy / MAX_ENERGY) * (1 + self.metabolism)
            self.size = min(self.max_size, self.size + growth_rate)
            self.speed = ((sum(self.genome["speed"]) / 2) * (1.5 if self.is_predator else 2.5) + 
                         (0.5 if self.is_predator else 1)) * (1 - self.size / 20) + self.metabolism * 0.5
    
    def find_nearest_food(self, algae_list, plankton_list, crustacean_list, dead_algae_parts):
        if self.is_predator:
            if not crustacean_list:
                return None
            return min(crustacean_list, key=lambda c: math.hypot(c.x - self.x, c.y - self.y))
        else:
            closest = None
            min_dist = float('inf')
            
            # Водорослі
            for algae in algae_list:
                for seg_x, seg_y in algae.segments:
                    dist = math.hypot(seg_x - self.x, seg_y - self.y)
                    if dist < min_dist:
                        min_dist = dist
                        closest = (algae, (seg_x, seg_y))
            
            # Планктон
            for plankton in plankton_list:
                dist = math.hypot(plankton.x - self.x, plankton.y - self.y)
                if dist < min_dist:
                    min_dist = dist
                    closest = plankton
            
            # Мертві частини водоростей
            for dead_part in dead_algae_parts:
                dist = math.hypot(dead_part.x - self.x, dead_part.y - self.y)
                if dist < min_dist:
                    min_dist = dist
                    closest = dead_part
            
            return closest
    
    def find_nearest_prey(self, fish_list):
        if not fish_list:
            return None
        
        potential_prey = [f for f in fish_list if f != self and 
                      (f.is_dead or
                       (not f.is_predator) or 
                       (f.is_predator and f.size + EAT_SIZE < self.size))]
        
        if not potential_prey:
            return None
        return min(potential_prey, key=lambda f: math.hypot(f.x - self.x, f.y - self.y))
    
    def find_nearest_mate(self, fish_list):
        if not fish_list:
            return None
        potential_mates = [f for f in fish_list if f != self and f.ready_to_mate and f.is_predator == self.is_predator]
        if not potential_mates:
            return None
        return min(potential_mates, key=lambda f: math.hypot(f.x - self.x, f.y - self.y))
    
    def handle_collision(self, other_fish):
        if self.is_dead or other_fish.is_dead:
            return
        
        if self.is_predator != other_fish.is_predator:
            return

        distance = math.hypot(self.x - other_fish.x, self.y - other_fish.y)
        min_distance = self.size + other_fish.size 
        
        if distance < min_distance and distance > 0: 
            overlap = min_distance - distance
            direction_x = (self.x - other_fish.x) / distance
            direction_y = (self.y - other_fish.y) / distance
            
            self.x += direction_x * overlap * OVERLAP_THRESHOLD
            self.y += direction_y * overlap * OVERLAP_THRESHOLD
            other_fish.x -= direction_x * overlap * OVERLAP_THRESHOLD
            other_fish.y -= direction_y * overlap * OVERLAP_THRESHOLD
            
            self.direction = math.atan2(direction_y, direction_x)
            other_fish.direction = math.atan2(-direction_y, -direction_x)

    def move(self, algae_list=None, plankton_list=None, crustacean_list=None, dead_algae_parts=None, target_prey=None, target_mate=None, predators=None, fish_list=None):
        target_food = self.find_nearest_food(algae_list, plankton_list, crustacean_list, dead_algae_parts)

        if self.is_dead:
            self.y -= self.float_speed
            if self.y <= 0:
                return
            return

        self.age += APT
        self.grow()

        if self.age >= self.max_age and not self.is_dead:
            self.is_dead = True
            self.energy = max(self.energy, 10)

        current_strength = (HEIGHT - self.y) / HEIGHT * 0.5
        self.x += current_strength

        nearest_predator = None
        if predators:
            if self.is_predator:
                bigger_predators = [p for p in predators if p.size > self.size + EAT_SIZE and p != self]
                if bigger_predators:
                    nearest_predator = min(bigger_predators, key=lambda p: math.hypot(p.x - self.x, p.y - self.y))
            else:
                nearest_predator = min(predators, key=lambda p: math.hypot(p.x - self.x, p.y - self.y), default=None)
                
        # if self.is_predator:
        if self.energy < MAX_ENERGY * 0.2:
            target_depth = HEIGHT / 3 
        elif self.energy > MAX_ENERGY * 0.8:
            target_depth = (sum(self.genome["preferred_depth"]) / 2) * HEIGHT 
        else:
            target_depth = self.preferred_depth 
        self.preferred_depth += (target_depth - self.preferred_depth) * ADAPTATION_RATE

        # Пріоритети дій:
        # 1. Втеча від хижака
        # 2. Розмноження (якщо готові)
        # 3. Адаптація глибини (для хижаків з низькою енергією, якщо немає цілей)
        # 4. Полювання/пошук їжі
        # 5. Рух до preferred_depth (як базова поведінка)

        if nearest_predator and math.hypot(nearest_predator.x - self.x, nearest_predator.y - self.y) < self.vision * 1.5:
            # Втеча від хижака - найвищий пріоритет
            desired_angle = math.atan2(self.y - nearest_predator.y, self.x - nearest_predator.x)
            angle_diff = desired_angle - self.direction
            angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
            if abs(angle_diff) > self.turn_speed:
                self.direction += self.turn_speed if angle_diff > 0 else -self.turn_speed
            else:
                self.direction = desired_angle
            self.direction = self.direction % (2 * math.pi)
            self.x += math.cos(self.direction) * self.speed * 1.2
            self.y += math.sin(self.direction) * self.speed * 1.2
        elif (self.ready_to_mate and target_mate and 
            math.hypot(target_mate.x - self.x, target_mate.y - self.y) < self.mate_vision):
            # Розмноження - другий пріоритет
            desired_angle = math.atan2(target_mate.y - self.y, target_mate.x - self.x)
            angle_diff = desired_angle - self.direction
            angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
            if abs(angle_diff) > self.turn_speed:
                self.direction += self.turn_speed if angle_diff > 0 else -self.turn_speed
            else:
                self.direction = desired_angle
            self.direction = self.direction % (2 * math.pi)
            self.x += math.cos(self.direction) * self.speed
            self.y += math.sin(self.direction) * self.speed
        elif (self.is_predator and self.energy < MAX_ENERGY * 0.2 and not target_prey):
            # Третій пріоритет: рух до preferred_depth при низькій енергії
            desired_angle = math.atan2(self.preferred_depth - self.y, 10)
            angle_diff = desired_angle - self.direction
            angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
            if abs(angle_diff) > self.turn_speed / 2:
                self.direction += (self.turn_speed / 2) if angle_diff > 0 else -(self.turn_speed / 2)
            self.direction = max(-math.pi/2, min(math.pi/2, self.direction))
            self.x += math.cos(self.direction) * self.speed
            self.y += math.sin(self.direction) * self.speed
        elif self.is_predator and target_prey and math.hypot(target_prey.x - self.x, target_prey.y - self.y) < self.vision:
            # Полювання для хижаків - четвертий пріоритет
            desired_angle = math.atan2(target_prey.y - self.y, target_prey.x - self.x)
            angle_diff = desired_angle - self.direction
            angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
            if abs(angle_diff) > self.turn_speed:
                self.direction += self.turn_speed if angle_diff > 0 else -self.turn_speed
            else:
                self.direction = desired_angle
            self.direction = self.direction % (2 * math.pi)
            self.x += math.cos(self.direction) * self.speed
            self.y += math.sin(self.direction) * self.speed
        elif not self.is_predator and target_food and self.energy < MAX_ENERGY * 0.95:
            # Пошук їжі для не-хижаків - четвертий пріоритет

            # Обробка target_food залежно від його типу
            if isinstance(target_food, tuple):  # Водорості: (algae, (seg_x, seg_y))
                algae, (target_x, target_y) = target_food
            else:  # Планктон
                target_x, target_y = target_food.x, target_food.y
            
            if math.hypot(target_x - self.x, target_y - self.y) < self.vision:
                desired_angle = math.atan2(target_y - self.y, target_x - self.x)
                angle_diff = desired_angle - self.direction
                angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
                if abs(angle_diff) > self.turn_speed:
                    self.direction += self.turn_speed if angle_diff > 0 else -self.turn_speed
                else:
                    self.direction = desired_angle
                self.direction = self.direction % (2 * math.pi)
                self.x += math.cos(self.direction) * self.speed
                self.y += math.sin(self.direction) * self.speed
        else:
            desired_angle = math.atan2(self.preferred_depth - self.y, 10)
            angle_diff = desired_angle - self.direction
            angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
            if abs(angle_diff) > self.turn_speed / 2:
                self.direction += (self.turn_speed / 2) if angle_diff > 0 else -(self.turn_speed / 2)
            self.direction = max(-math.pi/2, min(math.pi/2, self.direction))
            self.x += math.cos(self.direction) * self.speed
            self.y += math.sin(self.direction) * self.speed

        if fish_list:
            for other_fish in fish_list:
                if other_fish != self:
                    self.handle_collision(other_fish)

        if self.x > WIDTH + self.size:
            self.x = -self.size
        elif self.x < -self.size:
            self.x = WIDTH + self.size
        self.y = max(self.size, min(HEIGHT - self.size, self.y))

        energy_cost = self.speed * self.size * 0.005 * self.metabolism * (1 - self.defense * 0.5)
        self.energy -= energy_cost
    
    def eat(self, algae_list, plankton_list, crustacean_list, dead_algae_parts, fish_list):
        if self.is_dead or self.energy >= MAX_ENERGY * 0.95:
            return
        
        if self.is_predator:
            for crust in crustacean_list[:]:
                distance = math.hypot(self.x - crust.x, self.y - crust.y)
                if distance < self.size + 5:
                    energy_gain = crust.energy_value * (0.5 + self.digestion * 0.5)
                    self.energy = min(MAX_ENERGY, self.energy + energy_gain)
                    crustacean_list.remove(crust)
            for prey in fish_list[:]:
                if prey != self:
                    distance = math.hypot(self.x - prey.x, self.y - prey.y)
                    if distance < self.size + prey.size:
                        if prey.is_dead:
                            energy_gain = prey.energy * (0.5 + self.digestion * 0.5) * 0.7
                            self.energy = min(MAX_ENERGY, self.energy + energy_gain)
                            fish_list.remove(prey)
                        elif not prey.is_predator:
                            energy_gain = prey.energy * (0.5 + self.digestion * 0.5)
                            self.energy = min(MAX_ENERGY, self.energy + energy_gain)
                            fish_list.remove(prey)
                        elif prey.is_predator and prey.size + EAT_SIZE < self.size:
                            energy_gain = prey.energy * (0.5 + self.digestion * 0.5)
                            self.energy = min(MAX_ENERGY, self.energy + energy_gain)
                            fish_list.remove(prey)
        else:
            # Водорослі
            for algae in algae_list[:]:
                for i, (seg_x, seg_y) in enumerate(algae.segments[:]):
                    distance = math.hypot(self.x - seg_x, self.y - seg_y)
                    if distance < self.size + 5:
                        energy_gain = 3 * (0.5 + self.digestion * 0.5)
                        self.energy = min(MAX_ENERGY, self.energy + energy_gain)
                        algae.segments.pop(i)
                        algae.energy_value = max(0, algae.energy_value - 3)
                        if not algae.segments:
                            algae_list.remove(algae)
                        break
            
            # Планктон
            for plankton in plankton_list[:]:
                distance = math.hypot(self.x - plankton.x, self.y - plankton.y)
                if distance < self.size + 5:
                    energy_gain = plankton.energy_value * (0.5 + self.digestion * 0.5)
                    self.energy = min(MAX_ENERGY, self.energy + energy_gain)
                    plankton_list.remove(plankton)
            
            # Мертві частини водоростей
            for dead_part in dead_algae_parts[:]:
                distance = math.hypot(self.x - dead_part.x, self.y - dead_part.y)
                if distance < self.size + 5:
                    energy_gain = dead_part.energy_value * (0.5 + self.digestion * 0.5)
                    self.energy = min(MAX_ENERGY, self.energy + energy_gain)
                    dead_algae_parts.remove(dead_part)
    
    def check_mating_readiness(self):
        if not self.is_dead:
            self.ready_to_mate = (self.energy > self.energy_threshold and 
                                  random.random() < self.reproduction_rate and 
                                  self.age >= self.min_reproduction_age)
    def mate(self, partner):
        if (not partner or not self.ready_to_mate or not partner.ready_to_mate or 
            self.is_predator != partner.is_predator or self.is_dead or partner.is_dead or 
            self.is_male == partner.is_male or 
            self.age < self.min_reproduction_age or partner.age < partner.min_reproduction_age):
            return None
        
        distance = math.hypot(self.x - partner.x, self.y - partner.y)
        if distance > (self.size + partner.size) * 2 or self.energy < 30 or partner.energy < 30:
            return None
        
        child_genome = {}
        for key in self.genome:
            self_allele = random.choice(self.genome[key])
            partner_allele = random.choice(partner.genome[key])
            if key == "size":
                if random.random() < MUTATION_RATE:
                    self_allele = max(0.3, min(1, self_allele + random.uniform(-0.05, 0.05)))
                if random.random() < MUTATION_RATE:
                    partner_allele = max(0.3, min(1, partner_allele + random.uniform(-0.05, 0.05)))
            else:
                if random.random() < MUTATION_RATE:
                    self_allele = max(0, min(1, self_allele + random.uniform(-0.15, 0.15)))
                if random.random() < MUTATION_RATE:
                    partner_allele = max(0, min(1, partner_allele + random.uniform(-0.15, 0.15)))
            child_genome[key] = [self_allele, partner_allele]
        
        self.energy -= 30
        partner.energy -= 30
        self.ready_to_mate = False
        partner.ready_to_mate = False
        
        return Fish(self.x, self.y, 30, child_genome)
    
    def draw(self, screen):
        if self.is_dead:
            pygame.draw.circle(screen, (100, 100, 100), (int(self.x), int(self.y)), int(self.size))
        else:
            if self.is_predator:
                pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), int(self.size) + 2, 1)

            if self.ready_to_mate:
                pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), int(self.size) + 3, 1)
            
            if self.is_male:
                pygame.draw.circle(screen, (0, 0, 255), (int(self.x), int(self.y)), int(self.size) + 1, 2)
            else:
                pygame.draw.circle(screen, (0, 255, 0), (int(self.x), int(self.y)), int(self.size) + 1, 2)

            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))
        self.tail_angle += self.tail_speed * self.speed if not self.is_dead else 0
        tail_offset = math.sin(self.tail_angle) * self.size * 0.3
        tail_x = self.x - math.cos(self.direction) * self.size * 1.5
        tail_y = self.y - math.sin(self.direction) * self.size * 0.5 + tail_offset
        pygame.draw.line(screen, (255, 255, 255), (int(self.x), int(self.y)), 
                        (int(tail_x), int(tail_y)), 2)


class FishDetailsWindow:
    def __init__(self, simulation: 'Simulation', fish: 'Fish') -> None:
        def open_window():
            self.simulation = simulation
            self.fish = fish
            self.simulation.paused = True
            self.window = tk.Tk()

            self.window.title("Fish Details")
            self.window.geometry("530x570")
            self.window.configure(bg='#242424')

            left_frame = tk.Frame(self.window, bg='#242424')
            left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

            tk.Label(left_frame, 
                    text=f"Energy: {int(self.fish.energy)}/{MAX_ENERGY}",
                    font=("Arial", 12), bg='#242424', fg='#5E9F61'
            ).pack(pady=5)

            tk.Label(left_frame, 
                    text=f"Age: {self.fish.age:.1f}/{self.fish.max_age:.1f}",
                    font=("Arial", 12), bg='#242424', fg='#5E9F61'
            ).pack(pady=5)

            tk.Label(left_frame, 
                    text=f"Min Reproduction Age: {self.fish.min_reproduction_age:.1f}",
                    font=("Arial", 12), bg='#242424', fg='#5E9F61'
            ).pack(pady=5)

            tk.Label(left_frame, 
                    text=f"Size: {self.fish.size:.1f}/{self.fish.max_size:.1f}",
                    font=("Arial", 12), bg='#242424', fg='#5E9F61'
            ).pack(pady=5)

            tk.Label(left_frame, 
                    text=f"Gender: {'Male' if self.fish.is_male else 'Female'}",
                    font=("Arial", 12), bg='#242424', fg='#5E9F61'
            ).pack(pady=5)

            tk.Label(left_frame, 
                    text=f"Type: {'Predator' if self.fish.is_predator else 'Prey'}",
                    font=("Arial", 12), bg='#242424', fg='#5E9F61'
            ).pack(pady=5)

            tk.Label(left_frame, 
                    text=f"Ready to mate: {'Yes' if self.fish.ready_to_mate else 'No'}",
                    font=("Arial", 12), bg='#242424', fg='#5E9F61'
            ).pack(pady=5)

            tk.Label(left_frame, 
                    text=f"Status: {'Dead' if self.fish.is_dead else 'Alive'}",
                    font=("Arial", 12), bg='#242424', fg='#5E9F61'
            ).pack(pady=5)

            right_frame = tk.Frame(self.window, bg='#242424')
            right_frame.pack(side=tk.LEFT, padx=0, pady=10, fill=tk.BOTH, expand=True)

            tk.Label(right_frame, 
                    text="Genome:", 
                    font=("Arial", 12, "bold"), 
                    bg='#242424', 
                    fg='#5E9F61'
            ).pack(pady=5)

            canvas = tk.Canvas(right_frame, 
                             width=300, 
                             height=520, 
                             bg='#333333',
                             highlightbackground='#424242', 
                             highlightthickness=2
            ) 
            canvas.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            self.draw_genome(canvas, self.fish.genome)

            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.mainloop()

        Thread(target=open_window).start()

    def draw_genome(self, canvas, genome):
        y_pos = 20
        for trait, values in genome.items():
            canvas.create_text(20, y_pos, 
                             text=f"{trait}:", 
                             anchor="w", 
                             fill="#5E9F61", 
                             font=("Arial", 10))
            
            avg_value = sum(values) / 2
            canvas.create_text(120, y_pos, 
                             text=f"{avg_value:.2f}", 
                             anchor="w", 
                             fill="#5E9F61", 
                             font=("Arial", 10))
            
            bar_width = int(avg_value * 100)
            canvas.create_rectangle(200, y_pos-5, 200 + bar_width, y_pos+5, 
                                  fill="#5E9F61", 
                                  outline="")
            
            y_pos += 30

    def close_window(self) -> None:
        self.window.destroy()

class EventHandler:
    def __init__(self, simulation: 'Simulation') -> None:
        self.simulation = simulation

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.simulation.running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for fish in self.simulation.fish_population:
                    distance = math.hypot(fish.x - mouse_x, fish.y - mouse_y)
                    if distance < fish.size + 5:
                        FishDetailsWindow(self.simulation, fish)
                        break

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.simulation.paused = not self.simulation.paused 


class Simulation:
    def __init__(self):
        self.fish_population = [Fish(random.randint(0, WIDTH), random.randint(0, HEIGHT), 50)
                                for _ in range(NUM_FISH)]
        self.algae_list = [Algae(random.randint(0, WIDTH), HEIGHT)
                           for _ in range(INITIAL_ALGAE)]
        self.crustacean_list = [Crustacean(random.randint(0, WIDTH), random.randint(int(HEIGHT / 3), HEIGHT))
                                for _ in range(INITIAL_CRUSTACEANS)]
        self.plankton_list = [Plankton(random.randint(0, WIDTH), random.randint(0, int(HEIGHT/1.5)))
                              for _ in range(INITIAL_PLANKTON)]
        self.dead_algae_parts = []
        self.running = True
        self.paused = False
        self.event_handler = EventHandler(self)

    @staticmethod
    def draw_background(screen):
        for y in range(HEIGHT):
            blue = max(0, int(255 - (y / HEIGHT) * 205))
            green = max(0, int(150 - (y / HEIGHT) * 150))
            red = max(0, int(50 - (y / HEIGHT) * 50))
            pygame.draw.line(screen, (red, green, blue), (0, y), (WIDTH, y))

    def run(self):
        while self.running:
            self.draw_background(screen)
            
            self.event_handler.handle_events()

            if not self.paused:
                if random.random() < 0.4:
                    if random.random() < 0.1:
                        new_x = random.randint(0, WIDTH)
                        self.algae_list.append(Algae(new_x, HEIGHT))
                    elif random.random() < 0.4:
                        self.plankton_list.append(Plankton(random.randint(0, WIDTH), random.randint(0, int(HEIGHT/1.5))))
                    elif random.random() < 0.1:
                        self.crustacean_list.append(Crustacean(random.randint(0, WIDTH), random.randint(int(HEIGHT / 3), HEIGHT)))

                new_fish = []
                for fish in self.fish_population[:]:
                    fish.check_mating_readiness()
                    
                    nearest_prey = fish.find_nearest_prey(self.fish_population) if fish.is_predator and not fish.is_dead else None
                    nearest_mate = fish.find_nearest_mate(self.fish_population) if not fish.is_dead else None
                    predators = [f for f in self.fish_population if f.is_predator and not f.is_dead]
                    
                    fish.move(self.algae_list, self.plankton_list, self.crustacean_list, self.dead_algae_parts, nearest_prey, nearest_mate, predators, self.fish_population)
                    fish.eat(self.algae_list, self.plankton_list, self.crustacean_list, self.dead_algae_parts, self.fish_population)
                    
                    if fish.ready_to_mate and nearest_mate:
                        baby = fish.mate(nearest_mate)
                        if baby:
                            new_fish.append(baby)
                    
                    if fish.energy <= 0 and not fish.is_dead:
                        fish.is_dead = True
                        fish.energy = max(fish.energy, 10)
                    if fish.is_dead and fish.y <= 0:
                        self.fish_population.remove(fish)
                
                self.fish_population.extend(new_fish)
                
                for algae in self.algae_list[:]:
                    algae.update(self.algae_list, self.dead_algae_parts)
                    if not algae.segments:
                        self.algae_list.remove(algae)
                for crust in self.crustacean_list[:]:
                    crust.update()
                    if crust.lifetime <= 0:
                        self.crustacean_list.remove(crust)
                for plankton in self.plankton_list[:]:
                    plankton.update()
                    if plankton.lifetime <= 0:
                        self.plankton_list.remove(plankton)
                for dead_part in self.dead_algae_parts[:]:
                    dead_part.update()
                    if dead_part.lifetime <= 0 or dead_part.y <= 0:
                        self.dead_algae_parts.remove(dead_part)

            for algae in self.algae_list:
                algae.draw(screen)
            for crust in self.crustacean_list:
                crust.draw(screen)
            for plankton in self.plankton_list:
                plankton.draw(screen)
            for dead_part in self.dead_algae_parts:
                dead_part.draw(screen)
                
            for fish in self.fish_population:
                fish.draw(screen)
            
            predators = [f for f in self.fish_population if f.is_predator and not f.is_dead]
            prey = [f for f in self.fish_population if not f.is_predator and not f.is_dead]

            stats = font.render(f"Fish: {len([f for f in self.fish_population if not f.is_dead])} "
                               f"Algae: {len(self.algae_list)} Plankton: {len(self.plankton_list)} "
                               f"Crustaceans: {len(self.crustacean_list)} Dead Parts: {len(self.dead_algae_parts)}", 
                               True, (255, 255, 255))
            screen.blit(stats, (10, 10))

            prey_gender_stats = font.render(f"Prey ({len(prey)}) - Male: {len([f for f in prey if f.is_male])} Female: {len([f for f in prey if not f.is_male])}",
                                            True, (255, 255, 255))
            screen.blit(prey_gender_stats, (10, 40))

            predator_gender_stats = font.render(f"Predators ({len(predators)}) - Male: {len([f for f in predators if f.is_male])} Female: {len([f for f in predators if not f.is_male])}",
                                                True, (255, 255, 255))
            screen.blit(predator_gender_stats, (10, 70))
            
            if self.paused:
                pause_text = font.render("PAUSED", True, (255, 255, 255))
                screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - pause_text.get_height()//2))
            
            pygame.display.flip()
            clock.tick(60)


if __name__ == "__main__":
    sim = Simulation()
    sim.run()
    pygame.quit()