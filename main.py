import pygame
import random
import math
import tkinter as tk
from threading import Thread

from settings import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fish Evolution - Food Decay")
clock = pygame.time.Clock()


class Algae:
    def __init__(self, x, base_y):
        self.root_x = x
        self.base_y = base_y
        self.segments = [(x, base_y)]
        self.lowest_y = base_y 
        self.energy_value = 7
        self.growth_timer = random.randint(ALGAE_GROW[0], ALGAE_GROW[1])
        self.max_height = random.randint(int(HEIGHT * 0.3), int(HEIGHT * 0.5))
        self.branch_chance = 0.1
        self.is_alive = True

    def grow(self, simulation):  
        if not self.is_alive or simulation.day_phase == "Night":
            return

        if self.growth_timer > 0:
            self.growth_timer -= 1
            return

        top_y = min(seg[1] for seg in self.segments)
        if self.base_y - top_y >= self.max_height:
            return

        season = simulation.seasons[simulation.current_season_index]
        growth_modifier = {"Spring": 1.1, "Summer": 1.2, "Autumn": 0.9, "Winter": 0.7}[season]

        top_segment = min(self.segments, key=lambda s: s[1])
        new_x = top_segment[0] + random.uniform(-2, 2)
        new_y = top_segment[1] - random.uniform(2, 5) * growth_modifier
        
        self.segments.append((new_x, new_y))
        self.energy_value += random.randint(1, 3)
        if new_y < self.lowest_y:
            self.lowest_y = new_y 
        
        if random.random() < self.branch_chance:
            branch_x = top_segment[0] + random.uniform(-5, 5)
            branch_y = top_segment[1] - random.uniform(2, 5) * growth_modifier
            self.segments.append((branch_x, branch_y))
            self.energy_value += random.randint(1, 2)
            if branch_y < self.lowest_y:
                self.lowest_y = branch_y  

        self.growth_timer = random.randint(ALGAE_GROW[0], ALGAE_GROW[1])
    
    def check_root(self):
        return any(seg[1] >= self.base_y - 3 for seg in self.segments)

    def update(self, algae_list, dead_algae_parts, simulation):
        if not self.check_root() and self.is_alive:
            self.is_alive = False
            for seg_x, seg_y in self.segments[:]:
                if seg_y < self.base_y - 3:
                    dead_algae_parts.append(DeadAlgaePart(seg_x, seg_y))
            self.segments.clear()
            self.lowest_y = float('inf')

        if self.is_alive:
            self.grow(simulation)
            if len(algae_list) < MAX_ALGAE and random.random() < 0.01:
                new_x = self.root_x + random.randint(-20, 20)
                if 0 <= new_x <= WIDTH:
                    algae_list.append(Algae(new_x, self.base_y))  

    def draw(self, screen):
        if not self.segments:
            return
        
        color = (0, 150, 0) if self.is_alive else (0, 125, 0)
        points = [(int(x), int(y)) for x, y in self.segments]
        
        if len(points) >= 2:
            pygame.draw.lines(screen, color, False, points, 2)
        elif len(points) == 1:
            pygame.draw.circle(screen, color, points[0], 2)


class DeadAlgaePart:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy_value = random.randint(2, 5) 
        self.float_speed = random.uniform(0.2, 0.5)  
        self.lifetime = random.randint(DEAD_ALGAE_LIFETIME[0], DEAD_ALGAE_LIFETIME[1])  

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
        self.lifetime = random.randint(CRUSTACEAN_LIFETIME[0], CRUSTACEAN_LIFETIME[1]) 

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
        self.lifetime = random.randint(PLANKTON_LIFETIME[0], PLANKTON_LIFETIME[1])  

    def update(self):
        self.lifetime -= 1

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 200, 200), (int(self.x), int(self.y)), 2)


class Fish:
    def __init__(self, x, y, simulation, energy, genome=None):
        self.x = x
        self.y = y
        self.simulation = simulation
        self.energy = min(energy, MAX_ENERGY)
        self.size = 1.0
        
        if genome is None:
            self.genome = {
                "speed": {"alleles": [random.uniform(0, 1), random.uniform(0, 1)], "dominance": random.choice([0, 1])},
                "size": {"alleles": [random.uniform(0, 1), random.uniform(0, 1)], "dominance": random.choice([0, 1])},
                "vision": {"alleles": [random.uniform(0, 1), random.uniform(0, 1)], "dominance": random.choice([0, 1])},
                "metabolism": {"alleles": [random.uniform(0, 1), random.uniform(0, 1)], "dominance": random.choice([0, 1])},
                "digestion": {"alleles": [random.uniform(0, 1), random.uniform(0, 1)], "dominance": random.choice([0, 1])},
                "reproduction": {"alleles": [random.uniform(0, 1), random.uniform(0, 1)], "dominance": random.choice([0, 1])},
                "defense": {"alleles": [random.uniform(0, 1), random.uniform(0, 1)], "dominance": random.choice([0, 1])},
                "color": {"alleles": [random.uniform(0, 1), random.uniform(0, 1)], "dominance": random.choice([0, 1])},
                "preferred_depth": {"alleles": [random.uniform(0, 1), random.uniform(0, 1)], "dominance": random.choice([0, 1])},
                "predator": {"alleles": [random.uniform(0, 1), random.uniform(0, 1)], "dominance": random.choice([0, 1])}
            }
        else:
            self.genome = genome
        
        self.is_male = random.choice([True, False])
        self.is_predator = None 
        self.age = 0
        
        self.calculate_traits()
        
        self.energy_threshold = 40 if self.is_predator else 20
        self.mate_vision = self.vision * 1.5 
        self.ready_to_mate = False
        self.is_dead = False
        # self.float_speed = ((7 / (self.size * 2 + 0.5)) * 1.4 + 0.2) / 5
        self.float_speed = 1.5 / (1 + self.size)
        
        # Статевий диморфізм
        if self.is_male:
            self.color_modifier = 1.5  # Самці яскравіші
            self.speed *= 0.9  # Але повільніші
        else:
            self.color_modifier = 0.7  # Самки краще маскуються
            self.defense *= 1.1
        
        # Колір риби
        self.color = (
            max(0, min(255, int(self.genome["color"]["alleles"][0] * (100 if self.is_predator else 255) * self.color_modifier))),
            max(0, min(255, int((100 + self.size * 10) * (0.5 if self.is_predator else 1) * self.color_modifier))),
            max(0, min(255, int(self.genome["color"]["alleles"][1] * (100 if self.is_predator else 255) * self.color_modifier)))
        )
        
        # Рухові характеристики
        self.direction = random.uniform(-math.pi/2, math.pi/2)
        self.tail_angle = 0
        self.tail_speed = 0.2
        
        # Епігенетичні змінні
        self.food_scarcity_timer = 0
        self.base_metabolism = self.metabolism
        
        # Тривалість життя та репродукція
        base_lifespan = self.max_size * 4
        variation = random.uniform(0.8, 1.2)
        self.max_age = base_lifespan * variation * (1.2 if self.is_predator else 1.0) * (1 - self.metabolism * 0.3)
        
        base_reproduction_age = self.max_size * 0.4
        repro_variation = random.uniform(0.7, 1.3)
        self.min_reproduction_age = base_reproduction_age * repro_variation * (1.5 if self.is_predator else 1.0)
    
    def calculate_traits(self):
        def get_phenotype(trait):
            alleles = self.genome[trait]["alleles"]
            dom = self.genome[trait]["dominance"]
            if dom == 0:
                return alleles[0] * 0.75 + alleles[1] * 0.25
            else:
                return alleles[1] * 0.75 + alleles[0] * 0.25

        self.is_predator = get_phenotype("predator") > 0.5
        self.speed = get_phenotype("speed") * (1.5 if self.is_predator else 2.5)
        self.max_size = get_phenotype("size") * (10 if self.is_predator else 6) + (5 if self.is_predator else 3)
        self.vision = get_phenotype("vision") * (100 if self.is_predator else 60) + (50 if self.is_predator else 30)
        self.metabolism = get_phenotype("metabolism")
        self.digestion = get_phenotype("digestion")
        self.reproduction_rate = get_phenotype("reproduction") * (0.25 if self.is_predator else 0.45)
        self.defense = get_phenotype("defense")
        self.preferred_depth = get_phenotype("preferred_depth") * (HEIGHT - 2 * self.max_size) + self.max_size
        self.turn_speed = 0.1 if not self.is_predator else 0.08
        self.preferred_depth_range = 50

        # Плейотропні ефекти
        self.metabolism += (self.max_size / 20)
        self.metabolism = min(1.0, self.metabolism)
        self.defense *= (1 - get_phenotype("speed") * 0.4)
        self.speed *= (1 - self.defense * 0.3)
        self.max_size = self.max_size * (1 - self.defense * 0.2)  # Оновлюємо max_size
        self.turn_speed *= (1 - get_phenotype("size") * 0.25)
        self.metabolism += get_phenotype("vision") * 0.2
        self.metabolism = min(1.0, self.metabolism)

        self.energy_penalty = 0
        for trait in ["speed", "size", "vision"]:
            if get_phenotype(trait) > 0.8:
                self.energy_penalty += (get_phenotype(trait) - 0.8) * 0.5

        self.defense_cost = self.defense * 0.05

    def update_epigenetics(self, food_availability):
        if food_availability < 0.3:
            self.food_scarcity_timer += 1
            if self.food_scarcity_timer > 50: 
                self.metabolism = max(0.3, self.metabolism * 0.95) 
                self.digestion = min(1.0, self.digestion * 1.05) 
        else:
            self.food_scarcity_timer = max(0, self.food_scarcity_timer - 1)
            self.metabolism = min(1.0, self.metabolism * 1.01) 

    def grow(self):
        if not self.is_dead and self.size < self.max_size:
            def get_phenotype(trait):
                alleles = self.genome[trait]["alleles"]
                dom = self.genome[trait]["dominance"]
                if dom == 0:
                    return alleles[0] * 0.75 + alleles[1] * 0.25
                else:
                    return alleles[1] * 0.75 + alleles[0] * 0.25

            metabolism_phenotype = get_phenotype("metabolism")
            digestion_phenotype = get_phenotype("digestion")
            speed_phenotype = get_phenotype("speed")

            growth_rate = 0.01 * (self.energy / MAX_ENERGY) * (1 + metabolism_phenotype) * (0.5 + digestion_phenotype * 0.5)
            self.size = min(self.max_size, self.size + growth_rate)
            self.speed = (speed_phenotype * (1.5 if self.is_predator else 2.5) + 
                        (0.5 if self.is_predator else 1)) * (1 - self.size / 20) + metabolism_phenotype * 0.5
    
    def find_nearest_food(self, algae_list, plankton_list, crustacean_list, dead_algae_parts):
        effective_vision = self.vision * (0.7 if self.is_in_algae(algae_list) else 1)  # Зменшення видимості у водоростях

        if self.is_predator:
            if not crustacean_list:
                return None
            closest_crust = min(crustacean_list, key=lambda c: math.hypot(c.x - self.x, c.y - self.y))
            distance = math.hypot(closest_crust.x - self.x, closest_crust.y - self.y)
            return closest_crust if distance < effective_vision else None
        else:
            closest = None
            min_dist = effective_vision  # Обмежуємо пошуком у межах поля зору
            
            for algae in algae_list:
                for seg_x, seg_y in algae.segments:
                    dist = math.hypot(seg_x - self.x, seg_y - self.y)
                    if dist < min_dist:
                        min_dist = dist
                        closest = (algae, (seg_x, seg_y))
            
            for plankton in plankton_list:
                dist = math.hypot(plankton.x - self.x, plankton.y - self.y)
                if dist < min_dist:
                    min_dist = dist
                    closest = plankton
            
            for dead_part in dead_algae_parts:
                dist = math.hypot(dead_part.x - self.x, dead_part.y - self.y)
                if dist < min_dist:
                    min_dist = dist
                    closest = dead_part
            
            return closest
    
    def find_nearest_prey(self, fish_list, algae_list):
        if not fish_list:
            return None
        
        effective_vision = self.vision * (0.7 if self.is_in_algae(algae_list) else 1)  # Зменшення видимості у водоростях
        potential_prey = [f for f in fish_list if f != self and 
                        (f.is_dead or
                        (not f.is_predator) or 
                        (f.is_predator and f.size + EAT_SIZE < self.size))]
        
        if not potential_prey:
            return None
        
        def effective_distance(prey):
            prey_in_algae = prey.is_in_algae(algae_list)
            self_in_algae = self.is_in_algae(algae_list)
            vision = effective_vision * 0.4 if (prey_in_algae and not self_in_algae) else effective_vision
            distance = math.hypot(prey.x - self.x, prey.y - self.y)
            return distance if distance < vision else float('inf')
        
        nearest_prey = min(potential_prey, key=effective_distance, default=None)
        return nearest_prey if effective_distance(nearest_prey) != float('inf') else None
        
    def find_nearest_mate(self, fish_list, algae_list):
        if not fish_list:
            return None
        
        effective_mate_vision = self.mate_vision * (0.7 if self.is_in_algae(algae_list) else 1)  # Зменшення видимості у водоростях
        potential_mates = [f for f in fish_list if f != self and f.ready_to_mate and f.is_predator == self.is_predator and f.is_male != self.is_male]
        
        if not potential_mates:
            return None
        
        def effective_distance(mate):
            mate_in_algae = mate.is_in_algae(algae_list)
            self_in_algae = self.is_in_algae(algae_list)
            vision = effective_mate_vision * 0.4 if (mate_in_algae and not self_in_algae) else effective_mate_vision
            distance = math.hypot(mate.x - self.x, mate.y - self.y)
            return distance if distance < vision else float('inf')
        
        nearest_mate = min(potential_mates, key=effective_distance, default=None)
        return nearest_mate if effective_distance(nearest_mate) != float('inf') else None

    def handle_collision(self, other_fish):
        if self.is_dead or other_fish.is_dead:
            return

        distance = math.hypot(self.x - other_fish.x, self.y - other_fish.y)
        min_distance = self.size + other_fish.size 
        
        if distance < min_distance and distance > 0: 
            overlap = min_distance - distance
            direction_x = (self.x - other_fish.x) / distance
            direction_y = (self.y - other_fish.y) / distance
            
            correction = overlap * OVERLAP_THRESHOLD * 0.8
            self.x += direction_x * correction
            self.y += direction_y * correction
            other_fish.x -= direction_x * correction
            other_fish.y -= direction_y * correction
            
            self.direction = math.atan2(direction_y, direction_x)
            other_fish.direction = math.atan2(-direction_y, -direction_x)

    def is_in_algae(self, algae_list):
        for algae in algae_list:
            for seg_x, seg_y in algae.segments:
                distance = math.hypot(self.x - seg_x, self.y - seg_y)
                if distance < self.size + ALGAE_RAD:
                    return True
        return False

    def move(self, algae_list=None, crustacean_list=None, target_prey=None,
             target_mate=None, target_food=None, predators=None, fish_list=None):

        if self.is_dead:
            self.y -= self.float_speed - self.size * 0.01
            if self.y <= 0:
                return
            return

        temperature = self.simulation.get_temperature(self.y)
        oxygen = self.simulation.get_oxygen(self.x, self.y, algae_list)

        temp_factor = abs(temperature - OPTIMAL_TEMP) / OPTIMAL_TEMP
        metabolism_modifier = 1 + temp_factor * 0.5
        effective_metabolism = self.metabolism * metabolism_modifier

        oxygen_factor = 1.0
        if oxygen < CRITICAL_OXYGEN:
            oxygen_factor = oxygen / CRITICAL_OXYGEN
            effective_metabolism *= (1 + (CRITICAL_OXYGEN - oxygen) * 0.2)

        self.age += APT
        self.grow()

        food_availability = len(algae_list) / MAX_ALGAE if not self.is_predator else len(crustacean_list) / INITIAL_CRUSTACEANS
        self.update_epigenetics(food_availability)

        if self.age >= self.max_age and not self.is_dead:
            self.is_dead = True
            self.energy = max(self.energy, 10)

        current_strength = (HEIGHT - self.y) / HEIGHT * 0.5
        self.x += current_strength

        in_algae = self.is_in_algae(algae_list)
        effective_speed = self.speed * (0.6 if in_algae else 1)
        effective_vision = self.vision * (0.7 if in_algae else 1)

        nearest_predator = None
        if predators:
            if self.is_predator:
                bigger_predators = [p for p in predators if p.size > self.size + EAT_SIZE and p != self]
                if bigger_predators:
                    nearest_predator = min(bigger_predators, key=lambda p: math.hypot(p.x - self.x, p.y - self.y))
            else:
                nearest_predator = min(predators, key=lambda p: math.hypot(p.x - self.x, p.y - self.y), default=None)

        # Пріоритети дій:
        # 1. Втеча від хижака
        # 2. Розмноження (якщо готові)
        # 3. Полювання/пошук їжі
        # 4. Випадковий рух у спокої або рух до preferred_depth

        if nearest_predator and math.hypot(nearest_predator.x - self.x, nearest_predator.y - self.y) < effective_vision * 1.5:
            desired_angle = math.atan2(self.y - nearest_predator.y, self.x - nearest_predator.x)
            angle_diff = desired_angle - self.direction
            angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
            if abs(angle_diff) > self.turn_speed:
                self.direction += self.turn_speed if angle_diff > 0 else -self.turn_speed
            else:
                self.direction = desired_angle
            self.direction = self.direction % (2 * math.pi)
            self.x += math.cos(self.direction) * effective_speed * 1.2
            self.y += math.sin(self.direction) * effective_speed * 1.2

        elif (self.ready_to_mate and target_mate and 
            math.hypot(target_mate.x - self.x, target_mate.y - self.y) < self.mate_vision):
            desired_angle = math.atan2(target_mate.y - self.y, target_mate.x - self.x)
            angle_diff = desired_angle - self.direction
            angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
            if abs(angle_diff) > self.turn_speed:
                self.direction += self.turn_speed if angle_diff > 0 else -self.turn_speed
            else:
                self.direction = desired_angle
            self.direction = self.direction % (2 * math.pi)
            self.x += math.cos(self.direction) * effective_speed
            self.y += math.sin(self.direction) * effective_speed

        elif self.is_predator and (target_prey or target_food) and self.energy < MAX_ENERGY * 0.95:
            target = target_prey if target_prey else target_food

            if target:
                desired_angle = math.atan2(target.y - self.y, target.x - self.x)
                angle_diff = desired_angle - self.direction
                angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
                if abs(angle_diff) > self.turn_speed:
                    self.direction += self.turn_speed if angle_diff > 0 else -self.turn_speed
                else:
                    self.direction = desired_angle
                self.direction = self.direction % (2 * math.pi)
                self.x += math.cos(self.direction) * effective_speed
                self.y += math.sin(self.direction) * effective_speed
        
        elif (self.is_predator and self.energy < MAX_ENERGY * 0.2 and not (target_prey or target_food)):
            desired_angle = math.atan2(self.preferred_depth - self.y, 10)
            angle_diff = desired_angle - self.direction
            angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
            if abs(angle_diff) > self.turn_speed / 2:
                self.direction += (self.turn_speed / 2) if angle_diff > 0 else -(self.turn_speed / 2)
            self.direction = max(-math.pi/2, min(math.pi/2, self.direction))
            self.x += math.cos(self.direction) * effective_speed
            self.y += math.sin(self.direction) * effective_speed

        elif not self.is_predator and target_food and self.energy < MAX_ENERGY * 0.95:
            if isinstance(target_food, tuple):
                algae, (target_x, target_y) = target_food
            else:
                target_x, target_y = target_food.x, target_food.y
            
            if math.hypot(target_x - self.x, target_y - self.y) < effective_vision:
                desired_angle = math.atan2(target_y - self.y, target_x - self.x)
                angle_diff = desired_angle - self.direction
                angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
                if abs(angle_diff) > self.turn_speed:
                    self.direction += self.turn_speed if angle_diff > 0 else -self.turn_speed
                else:
                    self.direction = desired_angle
                self.direction = self.direction % (2 * math.pi)
                self.x += math.cos(self.direction) * effective_speed
                self.y += math.sin(self.direction) * effective_speed
        else:
            in_algae = self.is_in_algae(algae_list)
            effective_speed = self.speed * (0.6 if in_algae else 1)

            depth_difference = abs(self.y - self.preferred_depth)
            if depth_difference > self.preferred_depth_range and random.random() < 0.3:  
                desired_angle = math.atan2(self.preferred_depth - self.y, 10)
                angle_diff = desired_angle - self.direction
                angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
                if abs(angle_diff) > self.turn_speed * 0.5:
                    self.direction += (self.turn_speed * 0.5) if angle_diff > 0 else -(self.turn_speed * 0.5)
                else:
                    self.direction = desired_angle
                self.direction = self.direction % (2 * math.pi)
                idle_speed = effective_speed * 0.4  
            else:
                if random.random() < 0.15: 
                    self.direction += random.uniform(-self.turn_speed * 0.3, self.turn_speed * 0.3)
                    self.direction = self.direction % (2 * math.pi)
                idle_speed = effective_speed * 0.2 

            self.x += math.cos(self.direction) * idle_speed
            self.y += math.sin(self.direction) * idle_speed

            self.direction = max(-math.pi/2, min(math.pi/2, self.direction))

        if fish_list:
            for other_fish in fish_list:
                if other_fish != self:
                    self.handle_collision(other_fish)

        if self.x > WIDTH + self.size:
            self.x = -self.size
        elif self.x < -self.size:
            self.x = WIDTH + self.size
        self.y = max(self.size, min(HEIGHT - self.size, self.y))

        energy_cost = (effective_speed * self.size * 0.005 * effective_metabolism * 
                      (1 - self.defense * 0.5) / oxygen_factor)
        if effective_metabolism > self.digestion + 0.3:
            energy_cost *= 1.15
        energy_cost += self.defense_cost
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
                            prey.energy = -1
                            fish_list.remove(prey)
                        elif not prey.is_predator:
                            escape_chance = prey.defense * 0.35
                            if random.random() >= escape_chance:
                                energy_gain = prey.energy * (0.5 + self.digestion * 0.5)
                                self.energy = min(MAX_ENERGY, self.energy + energy_gain)
                                fish_list.remove(prey)
                                if random.random() < prey.defense * 0.2:
                                    # Невдача з можливим ушкодженням хижака
                                    self.energy -= 5
                            else:
                                pass

                        elif prey.is_predator and prey.size + EAT_SIZE < self.size:
                            escape_chance = prey.defense * 0.35
                            if random.random() >= escape_chance:
                                energy_gain = prey.energy * (0.5 + self.digestion * 0.5)
                                self.energy = min(MAX_ENERGY, self.energy + energy_gain)
                                fish_list.remove(prey)
                                if random.random() < prey.defense * 0.2:
                                    # Невдача з можливим ушкодженням хижака
                                    self.energy -= 5
                            else:
                                pass
        else:
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
            
            for plankton in plankton_list[:]:
                distance = math.hypot(self.x - plankton.x, self.y - plankton.y)
                if distance < self.size + 5:
                    energy_gain = plankton.energy_value * (0.5 + self.digestion * 0.5)
                    self.energy = min(MAX_ENERGY, self.energy + energy_gain)
                    plankton_list.remove(plankton)
            
            for dead_part in dead_algae_parts[:]:
                distance = math.hypot(self.x - dead_part.x, self.y - dead_part.y)
                if distance < self.size + 5:
                    energy_gain = dead_part.energy_value * (0.5 + self.digestion * 0.5)
                    self.energy = min(MAX_ENERGY, self.energy + energy_gain)
                    dead_algae_parts.remove(dead_part)
    
    def check_mating_readiness(self):
        if not self.is_dead:
            self.ready_to_mate = (self.energy > self.energy_threshold and 
                                random.random() < self.reproduction_rate * (0.7 + self.digestion * 0.3) *
                                (1 - self.defense * 0.2) and self.age >= self.min_reproduction_age)
            
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
            self_alleles = self.genome[key]["alleles"]
            partner_alleles = partner.genome[key]["alleles"]
            self_dom = self.genome[key]["dominance"]
            partner_dom = partner.genome[key]["dominance"]
            
            if random.random() < 0.7:
                self_allele = self_alleles[self_dom]
            else:
                self_allele = random.choice(self_alleles)
            if random.random() < 0.7:
                partner_allele = partner_alleles[partner_dom]
            else:
                partner_allele = random.choice(partner_alleles)
            
            mutation_range = 0.05 if key == 'predator' else 0.15
            if random.random() < MUTATION_RATE:
                self_allele = max(0, min(1, self_allele + random.uniform(-mutation_range, mutation_range)))
            if random.random() < MUTATION_RATE:
                partner_allele = max(0, min(1, partner_allele + random.uniform(-mutation_range, mutation_range)))
            
            child_genome[key] = {
                "alleles": [self_allele, partner_allele],
                "dominance": random.choice([0, 1])
            }
        
        energy_cost = 30 * (1 + self.metabolism * 0.5)
        self.energy -= energy_cost
        partner.energy -= energy_cost
        self.ready_to_mate = False
        partner.ready_to_mate = False
        
        return Fish(self.x, self.y, self.simulation, 30, child_genome)
    
    def draw(self, screen, show_vision, show_targets, nearest_prey=None, nearest_mate=None, nearest_food=None):
        # Відображення зони видимості
        if show_vision:
            vision_surface = pygame.Surface((self.vision * 2, self.vision * 2), pygame.SRCALPHA)
            vision_color = (255, 0, 0, 50) if self.is_predator else (0, 255, 0, 50)
            if self.is_dead:
                vision_color = (100, 100, 100, 20)
            pygame.draw.circle(vision_surface, vision_color, (self.vision, self.vision), int(self.vision))

            base_x = int(self.x - self.vision)
            base_y = int(self.y - self.vision)
            screen.blit(vision_surface, (base_x, base_y))

            if base_x < 0:
                screen.blit(vision_surface, (base_x + WIDTH, base_y))
            elif base_x + self.vision * 2 > WIDTH:  
                screen.blit(vision_surface, (base_x - WIDTH, base_y))
        
        # Відображення ліній до цілей
        if show_targets and not self.is_dead and self.energy < MAX_ENERGY * 0.95:
            if self.is_predator and nearest_prey and math.hypot(nearest_prey.x - self.x, nearest_prey.y - self.y) < self.vision:
                pygame.draw.line(screen, (255, 0, 0), (int(self.x), int(self.y)), (int(nearest_prey.x), int(nearest_prey.y)))
            elif self.is_predator and nearest_food and math.hypot(nearest_food.x - self.x, nearest_food.y - self.y) < self.vision:
                pygame.draw.line(screen, (255, 0, 0), (int(self.x), int(self.y)), (int(nearest_food.x), int(nearest_food.y)))
            elif not self.is_predator and nearest_food:
                if isinstance(nearest_food, tuple):
                    _, (target_x, target_y) = nearest_food
                else: 
                    target_x, target_y = nearest_food.x, nearest_food.y
                if math.hypot(target_x - self.x, target_y - self.y) < self.vision:
                    pygame.draw.line(screen, (0, 255, 0), (int(self.x), int(self.y)), (int(target_x), int(target_y)))
            elif nearest_mate and self.ready_to_mate and math.hypot(nearest_mate.x - self.x, nearest_mate.y - self.y) < self.mate_vision:
                pygame.draw.line(screen, (255, 255, 0), (int(self.x), int(self.y)), (int(nearest_mate.x), int(nearest_mate.y)))

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
        pygame.draw.line(screen, (255, 255, 255), (int(self.x), int(self.y)), (int(tail_x), int(tail_y)), 2)


class FishDetailsWindow:
    def __init__(self, simulation: 'Simulation', fish: 'Fish') -> None:
        def open_window():
            self.simulation = simulation
            self.fish = fish
            self.simulation.paused = True
            self.window = tk.Tk()

            self.window.title("Fish Details")
            self.window.geometry("660x570")
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
        for trait, data in genome.items():
            alleles = data["alleles"]
            dom = data["dominance"]
            dominant_allele = alleles[dom]
            recessive_allele = alleles[1 - dom]
            phenotype = dominant_allele * 0.75 + recessive_allele * 0.25  # Неповна домінантність

            if trait == 'preferred_depth':
                trait = 'pred_depth'

            canvas.create_text(20, y_pos, 
                             text=f"{trait}:", 
                             anchor="w", 
                             fill="#5E9F61", 
                             font=("Arial", 10))
            
            canvas.create_text(100, y_pos, 
                             text=f"A1: {alleles[0]:.2f}{' (D)' if dom == 0 else ''}", 
                             anchor="w", 
                             fill="#5E9F61", 
                             font=("Arial", 10))
            canvas.create_text(180, y_pos, 
                             text=f"A2: {alleles[1]:.2f}{' (D)' if dom == 1 else ''}", 
                             anchor="w", 
                             fill="#5E9F61", 
                             font=("Arial", 10))
            
            canvas.create_text(260, y_pos, 
                             text=f"{phenotype:.2f}", 
                             anchor="w", 
                             fill="#5E9F61", 
                             font=("Arial", 10))
            
            bar_width = int(phenotype * 100)
            canvas.create_rectangle(320, y_pos-5, 320 + bar_width, y_pos+5, 
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
                
                print("Temperature:", self.simulation.get_temperature(mouse_y))

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.simulation.paused = not self.simulation.paused

                elif event.key == pygame.K_v or event.unicode.lower() == "м":
                    if not self.simulation.show_vision:
                        self.simulation.active_modes.append("Vision") 
                    else:
                        self.simulation.active_modes.remove("Vision")

                    self.simulation.show_vision = not self.simulation.show_vision

                elif event.key == pygame.K_c or event.unicode.lower() == "с":
                    if not self.simulation.show_targets:
                        self.simulation.active_modes.append("Targets")
                    else:
                        self.simulation.active_modes.remove("Targets")

                    self.simulation.show_targets = not self.simulation.show_targets
                
                elif event.key == pygame.K_x or event.unicode.lower() == "ч":
                    if not self.simulation.show_temp_map:
                        self.simulation.active_modes.append("Temp Map")
                    else:
                        self.simulation.active_modes.remove("Temp Map")

                    self.simulation.show_temp_map = not self.simulation.show_temp_map

                elif event.key == pygame.K_z or event.unicode.lower() == "я":
                    if not self.simulation.show_oxygen_map:
                        self.simulation.active_modes.append("Oxy Map")
                    else:
                        self.simulation.active_modes.remove("Oxy Map")

                    self.simulation.show_oxygen_map = not self.simulation.show_oxygen_map


class UI:
    def __init__(self, simulation: 'Simulation') -> None:
        self.simulation = simulation
        self.font = pygame.font.Font(None, 24)

    def draw_statistic(self):
        predators = [f for f in self.simulation.fish_population if f.is_predator and not f.is_dead]
        prey = [f for f in self.simulation.fish_population if not f.is_predator and not f.is_dead]

        stats = self.font.render(f"Fish: {len([f for f in self.simulation.fish_population if not f.is_dead])} "
                            f"Algae: {len(self.simulation.algae_list)} Plankton: {len(self.simulation.plankton_list)} "
                            f"Crustaceans: {len(self.simulation.crustacean_list)} Dead Parts: {len(self.simulation.dead_algae_parts)}", 
                            True, (255, 255, 255))
        screen.blit(stats, (10, 10))

        prey_gender_stats = self.font.render(f"Prey ({len(prey)}) - Male: {len([f for f in prey if f.is_male])} Female: {len([f for f in prey if not f.is_male])}",
                                        True, (255, 255, 255))
        screen.blit(prey_gender_stats, (10, 30))

        predator_gender_stats = self.font.render(f"Predators ({len(predators)}) - Male: {len([f for f in predators if f.is_male])} Female: {len([f for f in predators if not f.is_male])}",
                                            True, (255, 255, 255))
        screen.blit(predator_gender_stats, (10, 50))

        time_info = self.font.render(f"Phase: {self.simulation.day_phase} ({self.simulation.time})  Season: {self.simulation.seasons[self.simulation.current_season_index]}", 
                                     True, (255, 255, 255))
        screen.blit(time_info, (10, 70))
        
        if self.simulation.paused:
            pause_text = self.font.render("PAUSED", True, (255, 255, 255))
            screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - pause_text.get_height()//2))
    
    def draw_active_modes(self):
        x_pos = WIDTH - 100 
        y_pos = 10  

        for mode in self.simulation.active_modes:
            if mode == "Vision":
                mode_text = self.font.render("Vision", True, (255, 255, 255))
            elif mode == "Targets":
                mode_text = self.font.render("Targets", True, (255, 255, 255))
            elif mode == 'Temp Map':
                mode_text = self.font.render("Temp Map", True, (255, 255, 255))
            elif mode == 'Oxy Map':
                mode_text = self.font.render("Oxy Map", True, (255, 255, 255))

            screen.blit(mode_text, (x_pos, y_pos))
            y_pos += 20
    
    def draw_maps(self):
        map_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        if self.simulation.show_temp_map:
            for y in range(0, HEIGHT, 10):
                for x in range(0, WIDTH, 10):
                    temp = self.simulation.get_temperature(y)
                    red = min(255, max(int((temp - MIN_TEMP) / (MAX_TEMP - MIN_TEMP) * 255), 0))
                    blue = min(255, max(int((MAX_TEMP - temp) / (MAX_TEMP - MIN_TEMP) * 255), 0))
                    pygame.draw.rect(map_surface, (red, 0, blue, 100), (x, y, 10, 10))
            screen.blit(map_surface, (0, 0))
        
        elif self.simulation.show_oxygen_map:
            for y in range(0, HEIGHT, 10):
                for x in range(0, WIDTH, 10):
                    oxygen = self.simulation.get_oxygen(x, y, self.simulation.algae_list)
                    green = min(255, int((oxygen - MIN_OXYGEN) / (MAX_OXYGEN - MIN_OXYGEN) * 255))
                    pygame.draw.rect(map_surface, (0, green, 0, 100), (x, y, 10, 10))
            screen.blit(map_surface, (0, 0))

    def draw(self):
        self.draw_maps()
        self.draw_active_modes()
        self.draw_statistic()


class Simulation:
    def __init__(self):
        self.event_handler = EventHandler(self)
        self.ui = UI(self)

        self.fish_population = [Fish(random.randint(0, WIDTH), random.randint(0, HEIGHT), self, random.randint(40, 60))
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
        self.background = self.create_background(WIDTH, HEIGHT)

        self.show_vision = False
        self.show_targets = False
        self.show_temp_map = False
        self.show_oxygen_map = False
        self.active_modes = []

        self.time = 0 
        self.day_length = 1800 # 1 день - 30 секунд
        self.season_length = 10800 # 1 сезон - 3 хвилин
        self.seasons = ["Spring", "Summer", "Autumn", "Winter"]
        self.current_season_index = 0
        self.day_phase = "Day"

    @staticmethod
    def create_background(width, height):
        background = pygame.Surface((width, height))
        for y in range(height):
            blue = max(0, int(255 - (y / height) * 205))
            green = max(0, int(150 - (y / height) * 150))
            red = max(0, int(50 - (y / height) * 50))
            pygame.draw.line(background, (red, green, blue), (0, y), (width, y))
        return background

    def update_time(self):
        self.time += 1
        day_progress = (self.time % self.day_length) / self.day_length
        self.day_phase = "Day" if day_progress < 0.5 else "Night"
        
        season_progress = (self.time % self.season_length) / self.season_length
        self.current_season_index = int((self.time // self.season_length) % 4)

    def get_temperature(self, y):
        depth_factor = 1 - (y / HEIGHT)
        base_temp = MIN_TEMP + (MAX_TEMP - MIN_TEMP) * depth_factor
        
        day_night_modifier = 1.0 if self.day_phase == "Day" else 0.9
        
        season = self.seasons[self.current_season_index]
        if season == "Summer":
            season_modifier = 1.1 
        elif season == "Winter":
            season_modifier = 0.8  
        else:  
            season_modifier = 1.0
        
        return base_temp * day_night_modifier * season_modifier

    def get_oxygen(self, x, y, algae_list):
        depth_factor = y / HEIGHT
        base_oxygen = MAX_OXYGEN - (MAX_OXYGEN - MIN_OXYGEN) * depth_factor
        
        oxygen_boost = 0
        if self.day_phase == "Day":
            for algae in algae_list:
                for seg_x, seg_y in algae.segments:
                    distance = math.hypot(x - seg_x, y - seg_y)
                    if distance < OXYGEN_BOOST_RADIUS:
                        oxygen_boost = max(oxygen_boost, OXYGEN_BOOST * (1 - distance / OXYGEN_BOOST_RADIUS))
        
        season = self.seasons[self.current_season_index]
        if season == "Summer":
            oxygen_boost *= 1.2 
        elif season == "Winter":
            oxygen_boost *= 0.7
        
        return min(MAX_OXYGEN, base_oxygen + oxygen_boost)

    def run(self):
        while self.running:
            screen.blit(self.background, (0, 0))
            self.event_handler.handle_events()

            if not self.paused:
                self.update_time()
                season = self.seasons[self.current_season_index]
                spawn_rate_modifier = {"Spring": 1.1, "Summer": 1.2, "Autumn": 0.9, "Winter": 0.7}[season]

                if random.random() < 0.3 * spawn_rate_modifier:
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

                    nearest_prey = fish.find_nearest_prey(self.fish_population, self.algae_list) if fish.is_predator and not fish.is_dead else None
                    nearest_mate = fish.find_nearest_mate(self.fish_population, self.algae_list) if not fish.is_dead else None
                    nearest_food = fish.find_nearest_food(self.algae_list, self.plankton_list, self.crustacean_list, self.dead_algae_parts) if not fish.is_dead else None
                    predators = [f for f in self.fish_population if f.is_predator and not f.is_dead]  # Локальний список хижаків

                    fish.move(self.algae_list, self.crustacean_list, nearest_prey, nearest_mate, nearest_food, predators, self.fish_population)
                    fish.eat(self.algae_list, self.plankton_list, self.crustacean_list, self.dead_algae_parts, self.fish_population)
                    
                    if fish.ready_to_mate and nearest_mate:
                        if baby := fish.mate(nearest_mate):
                            new_fish.append(baby)
                    
                    if fish.energy <= 0 and not fish.is_dead:
                        fish.is_dead = True
                        fish.energy = random.randint(5, 15) + fish.size * 0.5
                    
                    if fish.is_dead and fish.y <= 0:
                        self.fish_population.remove(fish)

                self.fish_population.extend(new_fish)

                for algae in self.algae_list[:]:
                    algae.update(self.algae_list, self.dead_algae_parts, self)
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
                nearest_prey = fish.find_nearest_prey(self.fish_population,
                                    self.algae_list) if fish.is_predator and not fish.is_dead and self.show_targets else None
                nearest_mate = fish.find_nearest_mate(self.fish_population,
                                    self.algae_list) if not fish.is_dead and self.show_targets else None
                nearest_food = fish.find_nearest_food(self.algae_list, self.plankton_list, self.crustacean_list,
                                    self.dead_algae_parts) if not fish.is_dead and self.show_targets  else None
                fish.draw(screen, self.show_vision, self.show_targets, nearest_prey, nearest_mate, nearest_food)

            self.ui.draw()

            pygame.display.flip()
            clock.tick(60)


if __name__ == "__main__":
    sim = Simulation()
    sim.run()
    pygame.quit()