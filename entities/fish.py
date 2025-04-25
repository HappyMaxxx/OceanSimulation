import math
import random
from typing import TYPE_CHECKING

import pygame

from core.settings import *

if TYPE_CHECKING:
    from core.simulation import Simulation


class Egg:
    def __init__(self, x, y, simulation: "Simulation", genome, incubation_time, survival_chance):
        self.x = x
        self.y = y
        self.simulation = simulation
        self.genome = genome
        self.incubation_time = incubation_time  
        self.survival_chance = survival_chance  
        self.energy_value = random.randint(2, 5) 
        self.lifetime = incubation_time
        self.float_speed = random.uniform(0.1, 0.3)  

    def update(self):
        strength, direction = self.simulation.current_grid.get_current_at(self.x, self.y)
        current_x = strength * math.cos(direction)
        current_y = strength * math.sin(direction)
        self.x += current_x * 0.5
        self.y += current_y * 0.5 - self.float_speed

        self.lifetime -= 3

        if self.y <= 0 or self.y >= HEIGHT:
            return False
        
        if random.random() > self.survival_chance:
            return False
        
        return True

    def hatch(self):
        if self.lifetime <= 0 and random.random() < self.survival_chance:
            return Fish(self.x, self.y, self.simulation, energy=20, genome=self.genome)
        return None

    def draw(self, screen):
        pygame.draw.circle(screen, (244, 54, 5), (int(self.x), int(self.y)), 2)


class Fish:
    def __init__(self, x, y, simulation: "Simulation", energy, genome=None,
                 nearest_food=None, nearest_prey=None, nearest_mate=None):
        self.x = x
        self.y = y
        self.simulation = simulation

        self.nearest_food = nearest_food
        self.nearest_prey = nearest_prey
        self.nearest_mate = nearest_mate

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
                "predator": {"alleles": [random.uniform(0, 0.75), random.uniform(0, 0.85)], "dominance": random.choice([0, 1])},
                "reproduction_strategy": {"alleles": [random.uniform(0, 1), random.uniform(0, 1)], "dominance": random.choice([0, 1])}
            }
        else:
            self.genome = genome
        
        self.is_male = random.choice([True, False])
        self.is_predator = None 
        self.age = 0
        
        self.calculate_traits()
        
        self.max_energy = (MAX_ENERGY * (
            SIZE_EFECT * self.max_size +
            DEGISTION_EFECT * self.digestion +
            REPRODUCTION_EFECT * self.reproduction_rate
        ) / (1 + METABOLISM_EFECT * self.metabolism)) / 3

        self.energy = energy if energy is not None else random.uniform(0, self.max_energy)

        self.energy_threshold = 35 if self.is_predator else 20
        self.mate_vision = self.vision * 1.5 
        self.ready_to_mate = False
        self.is_dead = False
        self.float_speed = 1.5 / (1 + self.size) / 2
        
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

        self.vision_sq_o = self.vision ** 2
        self.vision_sq_a = self.vision ** 2 * VISION_REDUCTION_IN_ALGAE ** 2

        self.is_pregnant = False
        self.pregnancy_timer = 0
        self.pregnancy_duration = round(random.uniform(*PREDATOR_PREGNANCY_DUR)) \
            if self.is_predator else round(random.uniform(*PREY_PREGNANCY_DUR))
        self.pregnancy_energy_cost = 0.1 if self.is_predator else 0.05
        self.child_genome = None
        self.after_birth_period = 0
        self.after_birth_duration = round(random.uniform(*PREDATOR_AFTER_BIRTH_DUR)) \
            if self.is_predator else round(random.uniform(*PREY_AFTER_BIRTH_DUR))
        self.kids_num = None

        self.is_egglayer = self.reproduction_strategy == "egglayer"

    def calculate_traits(self):
        def get_phenotype(trait):
            alleles = self.genome[trait]["alleles"]
            dom = self.genome[trait]["dominance"]
            if dom == 0:
                return alleles[0] * 0.75 + alleles[1] * 0.25
            else:
                return alleles[1] * 0.75 + alleles[0] * 0.25

        self.is_predator = get_phenotype("predator") > 0.5

        if self.is_predator:
            if self.genome["predator"]["alleles"][0] > self.genome["predator"]["alleles"][1] \
                and self.genome["predator"]["alleles"][1] < 0.5:
                self.genome["predator"]["alleles"][1] = 0.5
            elif self.genome["predator"]["alleles"][1] > self.genome["predator"]["alleles"][0] \
                and self.genome["predator"]["alleles"][0] < 0.5:
                self.genome["predator"]["alleles"][0] = 0.5
        else:
            if self.genome["predator"]["alleles"][0] > self.genome["predator"]["alleles"][1] \
                and self.genome["predator"]["alleles"][0] > 0.5:
                self.genome["predator"]["alleles"][0] = 0.49
            elif self.genome["predator"]["alleles"][1] > self.genome["predator"]["alleles"][0] \
                and self.genome["predator"]["alleles"][1] > 0.5:
                self.genome["predator"]["alleles"][1] = 0.49

        repro_strategy_val = get_phenotype("reproduction_strategy")
        self.reproduction_strategy = "egglayer" if (repro_strategy_val < 0.3 \
            if self.is_predator else repro_strategy_val < 0.7) else "livebearer"

        self.speed = get_phenotype("speed") * (1.5 if self.is_predator else 2.5)
        self.max_size = get_phenotype("size") * (10 if self.is_predator else 6) + (5 if self.is_predator else 3)
        self.vision = get_phenotype("vision") * (80 if not self.is_predator else 60) + (50 if not self.is_predator else 40)
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

            growth_rate = 0.01 * (self.energy / self.max_energy) * (1 + metabolism_phenotype) * (0.5 + digestion_phenotype * 0.5)
            self.size = min(self.max_size, self.size + growth_rate)
            self.speed = (speed_phenotype * (1.5 if self.is_predator else 2.5) + 
                        (0.5 if self.is_predator else 1)) * (1 - self.size / 20) + metabolism_phenotype * 0.5
    
    def find_nearest_food(self, algae_list, plankton_list, crustacean_list, dead_algae_parts):
        if self.is_predator:
            if not crustacean_list:
                return None
            closest_crust = min(crustacean_list, key=lambda c: (c.x - self.x) ** 2 + (c.y - self.y) ** 2)
            dist_sq = (closest_crust.x - self.x) ** 2 + (closest_crust.y - self.y) ** 2
            vision_sq = self.vision_sq_a if self.is_in_algae else self.vision_sq_o

            if self.simulation.egg_list:
                closest_egg = min(self.simulation.egg_list, key=lambda c: (c.x - self.x) ** 2 + (c.y - self.y) ** 2)
                dist_sq_egg = (closest_egg.x - self.x) ** 2 + (closest_egg.y - self.y) ** 2
                if dist_sq_egg < dist_sq:
                    return closest_egg if dist_sq_egg < vision_sq else None

            return closest_crust if dist_sq < vision_sq else None

        else:
            closest = None
            min_dist_sq = self.vision_sq_a if self.is_in_algae else self.vision_sq_o
            
            for algae in algae_list:
                for seg_x, seg_y in algae.segments:
                    dist_sq = (seg_x - self.x) ** 2 + (seg_y - self.y) ** 2
                    if dist_sq < min_dist_sq:
                        min_dist_sq = dist_sq
                        closest = (algae, (seg_x, seg_y))
            
            for plankton in plankton_list:
                dist_sq = (plankton.x - self.x) ** 2 + (plankton.y - self.y) ** 2
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    closest = plankton
            
            for dead_part in dead_algae_parts:
                dist_sq = (dead_part.x - self.x) ** 2 + (dead_part.y - self.y) ** 2
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    closest = dead_part
            
            return closest
    
    def find_nearest_prey(self, fish_list):
        if not fish_list:
            return None
        
        effective_vision = self.vision * (VISION_REDUCTION_IN_ALGAE if self.is_in_algae() else 1)
        potential_prey = [f for f in fish_list if f != self and 
                        (f.is_dead or
                        (not f.is_predator) or 
                        (f.is_predator and f.size + EAT_SIZE < self.size))]
        
        if not potential_prey:
            return None
        
        def effective_distance(prey):
            prey_in_algae = prey.is_in_algae()
            self_in_algae = self.is_in_algae()
            vision = effective_vision * 0.4 \
                if (prey_in_algae and not self_in_algae) else effective_vision
            vision_sq_adj = vision * vision
            dist_sq = (prey.x - self.x) ** 2 + (prey.y - self.y) ** 2
            return dist_sq if dist_sq < vision_sq_adj else float('inf')
        
        nearest_prey = min(potential_prey, key=effective_distance, default=None)
        return nearest_prey if effective_distance(nearest_prey) != float('inf') else None
        
    def find_nearest_mate(self, fish_list):
        if not fish_list or self.is_pregnant or self.is_dead:
            return None
        
        effective_mate_vision = self.mate_vision * (VISION_REDUCTION_IN_ALGAE 
                                                    if self.is_in_algae() else 1)
        
        potential_mates = [f for f in fish_list if f != self and f.ready_to_mate
                           and f.is_predator == self.is_predator and f.is_male != self.is_male]
        
        if not potential_mates:
            return None
        
        def effective_distance(mate):
            mate_in_algae = mate.is_in_algae()
            self_in_algae = self.is_in_algae()
            vision = effective_mate_vision * 0.4 if (mate_in_algae and not self_in_algae) else effective_mate_vision
            vision_sq_adj = vision * vision
            dist_sq = (mate.x - self.x) ** 2 + (mate.y - self.y) ** 2
            return dist_sq if dist_sq < vision_sq_adj else float('inf')
        
        nearest_mate = min(potential_mates, key=effective_distance, default=None)
        return nearest_mate if effective_distance(nearest_mate) != float('inf') else None

    def handle_collision(self, other_fish):
        if self.is_dead or other_fish.is_dead:
            return
        
        dx = self.x - other_fish.x
        dy = self.y - other_fish.y
        dist_sq = dx * dx + dy * dy
        min_distance = self.size + other_fish.size
        min_dist_sq = min_distance * min_distance
        
        if dist_sq < min_dist_sq and dist_sq > 0:
            distance = math.hypot(dx, dy)
            overlap = min_distance - distance
            direction_x = dx / distance
            direction_y = dy / distance
            
            self.x += direction_x * overlap * OVERLAP_THRESHOLD
            self.y += direction_y * overlap * OVERLAP_THRESHOLD
            other_fish.x -= direction_x * overlap * 0.5
            other_fish.y -= direction_y * overlap * 0.5
            
            new_direction = math.atan2(direction_y, direction_x)
            self.direction = self.direction * 0.5 + new_direction * 0.5
            other_fish.direction = other_fish.direction * 0.5 + math.atan2(-direction_y, -direction_x) * 0.5

    def is_in_algae(self):
        nearby_segments = self.simulation.get_nearby_segments(self.x, self.y)
        threshold_sq = (self.size + ALGAE_RAD) ** 2
        for seg_x, seg_y, _ in nearby_segments:
            dist_sq = (self.x - seg_x) ** 2 + (self.y - seg_y) ** 2
            if dist_sq < threshold_sq:
                return True
        return False

    def move(self, predators=None, fish_list=None):
        sim = self.simulation

        if self.is_dead:
            strength, direction = sim.current_grid.get_current_at(self.x, self.y)
            current_x = strength * math.cos(direction)
            current_y = strength * math.sin(direction)
            
            self.x += current_x * CURRENT_MOVEMENT_FACTOR
            self.y += current_y * CURRENT_MOVEMENT_FACTOR - (self.float_speed * 1.2 - self.size * 0.02)
            if self.y <= 0: 
                return
            return

        self.nearest_food = target_food = self.find_nearest_food(sim.algae_list, sim.plankton_list,
                                                   sim.crustacean_list, sim.dead_algae_parts)
        self.nearest_prey = target_prey = self.find_nearest_prey(fish_list) if self.is_predator else None
        self.nearest_mate = target_mate = self.find_nearest_mate(fish_list)

        strength, direction = sim.current_grid.get_current_at(self.x, self.y)
        current_x = strength * math.cos(direction)
        current_y = strength * math.sin(direction)
        current_vector = math.hypot(current_x, current_y)  
        current_angle = math.atan2(current_y, current_x)

        in_algae = self.is_in_algae()
        base_speed = self.speed * (0.6 if in_algae else 1)  
        angle_diff = (self.direction - current_angle + math.pi) % (2 * math.pi) - math.pi  
        resistance_factor = math.cos(angle_diff) 
        effective_speed = base_speed * (1 - current_vector * 0.5 * (1 - resistance_factor)) 
        effective_speed = max(0, effective_speed) 

        self.x += current_x * 0.5  
        self.y += current_y * 0.5

        temperature = self.simulation.get_temperature(self.x, self.y)
        oxygen = self.simulation.get_oxygen(self.x, self.y, sim.algae_list)

        temp_factor = abs(temperature - OPTIMAL_TEMP) / OPTIMAL_TEMP
        metabolism_modifier = 1 + temp_factor * 0.3
        effective_metabolism = self.metabolism * metabolism_modifier * 0.75

        oxygen_factor = 1.0
        if oxygen < CRITICAL_OXYGEN:
            oxygen_factor = oxygen / CRITICAL_OXYGEN
            effective_metabolism *= (1 + (CRITICAL_OXYGEN - oxygen) * 0.2)

        self.age += APT
        self.grow()

        food_availability = len(sim.algae_list) / MAX_ALGAE if not self.is_predator else len(sim.crustacean_list) / INITIAL_CRUSTACEANS
        self.update_epigenetics(food_availability)

        if self.age >= self.max_age and not self.is_dead:
            self.is_dead = True
            self.energy = max(self.energy, 10)

        current_strength = (HEIGHT - self.y) / HEIGHT * 0.5  
        self.x += current_strength

        effective_vision = self.vision * (VISION_REDUCTION_IN_ALGAE if in_algae else 1)

        if sim.seasons[sim.current_season_index] == "Spring":
            self.reproduction_rate = 0.55 if not self.is_predator else 0.35
        else:
            self.reproduction_rate = 0.45 if not self.is_predator else 0.25

        nearest_predator = None
        if predators:
            if self.is_predator:
                bigger_predators = [p for p in predators if p.size > self.size + EAT_SIZE and p != self]
                if bigger_predators:
                    nearest_predator = min(bigger_predators, key=lambda p: math.hypot(p.x - self.x, p.y - self.y))
            else:
                nearest_predator = min(predators, key=lambda p: math.hypot(p.x - self.x, p.y - self.y), default=None)

        effective_speed = effective_speed * (0.65 if in_algae else 1) 
        if self.is_pregnant:
            effective_speed *= 0.85

        # Пріоритети дій:
        # 1. Втеча від хижака
        # 2. Розмноження (якщо готові)
        # 3. Полювання/пошук їжі
        # 4. Випадковий рух у спокої або рух до preferred_depth

        vision_sq = self.vision_sq_a if self.is_in_algae else self.vision_sq_o
        if nearest_predator and (nearest_predator.x - self.x) ** 2 + (nearest_predator.y - self.y) ** 2 < vision_sq:
            base_angle = math.atan2(self.y - nearest_predator.y, self.x - nearest_predator.x)

            if self.y > HEIGHT - LINE_LEVEL:
                possible_angles = [base_angle + math.pi / 3, base_angle - math.pi / 3, base_angle]
                best_angle = base_angle
                max_dist = -float('inf')
                
                for angle in possible_angles:
                    new_x = self.x + math.cos(angle) * effective_speed
                    new_y = self.y + math.sin(angle) * effective_speed
                    dist_sq = (nearest_predator.x - new_x) ** 2 + (nearest_predator.y - new_y) ** 2
                    if dist_sq > max_dist:
                        max_dist = dist_sq
                        best_angle = angle
                desired_angle = best_angle
            else:
                desired_angle = base_angle

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

        elif self.is_predator and (target_prey or target_food) and self.energy < self.max_energy * 0.95:
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
        
        elif (self.is_predator and self.energy < self.max_energy * 0.2 and not (target_prey or target_food)):
            desired_angle = math.atan2(self.preferred_depth - self.y, 10)
            angle_diff = desired_angle - self.direction
            angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
            if abs(angle_diff) > self.turn_speed / 2:
                self.direction += (self.turn_speed / 2) if angle_diff > 0 else -(self.turn_speed / 2)
            self.direction = max(-math.pi/2, min(math.pi/2, self.direction))
            self.x += math.cos(self.direction) * effective_speed
            self.y += math.sin(self.direction) * effective_speed

        elif not self.is_predator and target_food and self.energy < self.max_energy * 0.95:
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
            depth_difference = abs(self.y - self.preferred_depth)
            if depth_difference > self.preferred_depth_range and self.simulation.get_random() < 0.2:  
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
                if self.y > LINE_LEVEL and not self.is_pregnant:
                    if self.simulation.get_random() < 0.7:  
                        self.direction = random.uniform(-math.pi / 6, 0)  
                    else:  
                        self.direction += random.uniform(-self.turn_speed * 0.2, self.turn_speed * 0.2)

                elif self.is_pregnant and self.y < LINE_LEVEL and not in_algae:
                    if self.simulation.get_random() < 0.7:  
                        self.direction = random.uniform(3 * math.pi / 2, 2 * math.pi)
                    else:  
                        self.direction += random.uniform(-self.turn_speed * 0.2, self.turn_speed * 0.2)

                elif self.simulation.get_random() < 0.15: 

                    self.direction += random.uniform(-self.turn_speed * 0.2, self.turn_speed * 0.2)

                idle_speed = effective_speed * IDLE_MOVEMENT_FACTOR 

            self.x += math.cos(self.direction) * idle_speed
            self.y += math.sin(self.direction) * idle_speed

        if self.simulation.get_random() < 0.25:
            self.direction += random.uniform(-self.turn_speed * 0.1, self.turn_speed * 0.1)
        elif in_algae and self.simulation.get_random() < 0.25:
            self.direction += random.uniform(-self.turn_speed * 0.3, -self.turn_speed * 0.1)

        # Обробка колізій з іншими рибами
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
                      (1 - self.defense * 0.4) / oxygen_factor)
        if effective_metabolism > self.digestion + 0.3:
            energy_cost *= 1.15
        energy_cost += self.defense_cost
        energy_cost += self.pregnancy_energy_cost if self.is_pregnant else 0
        self.energy -= energy_cost
        
    def eat(self, fish_list):
        if self.is_dead or self.energy >= self.max_energy * 0.95:
            return
        
        sim = self.simulation
        threshold_sq = (self.size + 5) ** 2
        
        if self.is_predator:
            for crust in sim.crustacean_list[:]:
                dist_sq = (self.x - crust.x) ** 2 + (self.y - crust.y) ** 2
                if dist_sq < threshold_sq:
                    energy_gain = crust.energy_value * (0.5 + self.digestion * 0.5)
                    self.energy = min(self.max_energy, self.energy + energy_gain)
                    sim.crustacean_list.remove(crust)
            
            for prey in fish_list[:]:
                if prey != self:
                    dist_sq = (self.x - prey.x) ** 2 + (self.y - prey.y) ** 2
                    prey_size_sq = (self.size + prey.size) ** 2
                    if dist_sq < prey_size_sq:
                        if prey.is_dead:
                            energy_gain = prey.energy * (0.5 + self.digestion * 0.5) * 0.7
                            self.energy = min(self.max_energy, self.energy + energy_gain)
                            prey.energy = -1
                            fish_list.remove(prey)
                        elif not prey.is_predator:
                            escape_chance = prey.defense * 0.35
                            if self.simulation.get_random() >= escape_chance:
                                energy_gain = prey.energy * (0.5 + self.digestion * 0.5)
                                self.energy = min(self.max_energy, self.energy + energy_gain)
                                fish_list.remove(prey)
                                if self.simulation.get_random() < prey.defense * 0.2:
                                    # Невдача з можливим ушкодженням хижака
                                    self.energy -= 5
                            else:
                                pass

                        elif prey.is_predator and prey.size + EAT_SIZE < self.size:
                            escape_chance = prey.defense * 0.35
                            if self.simulation.get_random() >= escape_chance:
                                energy_gain = prey.energy * (0.5 + self.digestion * 0.5)
                                self.energy = min(self.max_energy, self.energy + energy_gain)
                                fish_list.remove(prey)
                                if self.simulation.get_random() < prey.defense * 0.2:
                                    # Невдача з можливим ушкодженням хижака
                                    self.energy -= 5
                            else:
                                pass

            for egg in sim.egg_list[:]:
                dist_sq = (self.x - egg.x) ** 2 + (self.y - egg.y) ** 2
                if dist_sq < threshold_sq:
                    energy_gain = egg.energy_value * (0.5 + self.digestion * 0.5)
                    self.energy = min(self.max_energy, self.energy + energy_gain)
                    sim.egg_list.remove(egg)
        else:
            for algae in sim.algae_list[:]:
                for i, (seg_x, seg_y) in enumerate(algae.segments[:]):
                    dist_sq = (self.x - seg_x) ** 2 + (self.y - seg_y) ** 2
                    if dist_sq < threshold_sq:
                        energy_gain = 3 * (0.5 + self.digestion * 0.5)
                        self.energy = min(self.max_energy, self.energy + energy_gain)
                        algae.segments.pop(i)
                        sim.remove_segment_from_grid(seg_x, seg_y, algae)
                        algae.energy_value = max(0, algae.energy_value - 3)
                        if not algae.segments:
                            sim.algae_list.remove(algae)
                        break
            
            for plankton in sim.plankton_list[:]:
                distance = math.hypot(self.x - plankton.x, self.y - plankton.y)
                if distance < self.size + 5:
                    energy_gain = plankton.energy_value * (0.5 + self.digestion * 0.5)
                    self.energy = min(self.max_energy, self.energy + energy_gain)
                    sim.plankton_list.remove(plankton)
            
            for dead_part in sim.dead_algae_parts[:]:
                distance = math.hypot(self.x - dead_part.x, self.y - dead_part.y)
                if distance < self.size + 5:
                    energy_gain = dead_part.energy_value * (0.5 + self.digestion * 0.5)
                    self.energy = min(self.max_energy, self.energy + energy_gain)
                    sim.dead_algae_parts.remove(dead_part)
    
    def check_mating_readiness(self):
        if self.after_birth_period > 0:
            self.after_birth_period -= 1
            return None
        
        if not self.is_dead and not self.is_pregnant:
            self.ready_to_mate = (self.energy > self.energy_threshold and 
                                self.simulation.get_random() < self.reproduction_rate * (0.7 + self.digestion * 0.3) *
                                (1 - self.defense * 0.2) and self.age >= self.min_reproduction_age)
            
    def mate(self, partner):
        if (not partner or not self.ready_to_mate or not partner.ready_to_mate or 
            self.is_predator != partner.is_predator or self.is_dead or partner.is_dead or 
            self.is_male == partner.is_male or 
            self.age < self.min_reproduction_age or partner.age < partner.min_reproduction_age):
            return None

        dist_sq = (self.x - partner.x) ** 2 + (self.y - partner.y) ** 2
        threshold_sq = ((self.size + partner.size) * 2) ** 2
        if dist_sq > threshold_sq or self.energy < self.max_energy * 0.2 or partner.energy < partner.max_energy * 0.2:
            return None

        if not self.is_male:
            if self.is_egglayer:
                kids_num = self.kids_num = random.randint(10, 15) if self.is_predator else random.randint(15, 25)
            else:
                kids_num = self.kids_num = random.randint(1, 2) if self.is_predator else random.randint(1, 3)
        else:
            if partner.is_egglayer:
                kids_num = partner.kids_num = random.randint(10, 15) if partner.is_predator else random.randint(15, 25)
            else:
                kids_num = partner.kids_num = random.randint(1, 2) if partner.is_predator else random.randint(1, 3)

        kid_genomes = []
        for _ in range(kids_num):
            child_genome = {}
            for key in self.genome:
                self_alleles = self.genome[key]["alleles"]
                partner_alleles = partner.genome[key]["alleles"]
                self_dom = self.genome[key]["dominance"]
                partner_dom = partner.genome[key]["dominance"]
                if self.simulation.get_random() < 0.7:
                    self_allele = self_alleles[self_dom]
                else:
                    self_allele = random.choice(self_alleles)
                if self.simulation.get_random() < 0.7:
                    partner_allele = partner_alleles[partner_dom]
                else:
                    partner_allele = random.choice(partner_alleles)
                mutation_range = 0.15
                if self.simulation.get_random() < MUTATION_RATE and key != "predator":
                    self_allele = max(0, min(1, self_allele + random.uniform(-mutation_range, mutation_range)))
                if self.simulation.get_random() < MUTATION_RATE and key != "predator":
                    partner_allele = max(0, min(1, partner_allele + random.uniform(-mutation_range, mutation_range)))
                child_genome[key] = {
                    "alleles": [self_allele, partner_allele],
                    "dominance": random.choice([0, 1])
                }
            kid_genomes.append(child_genome)

        base_energy_cost = self.max_energy * 0.25 / 2
        energy_cost = base_energy_cost * (1 + self.metabolism * 0.25)

        if not self.is_male:
            if self.is_egglayer:
                for genome in kid_genomes:
                    incubation_time = random.randint(100, 150) if self.is_predator else random.randint(80, 110)
                    survival_chance = 0.88 if not self.is_predator else 0.73
                    egg = Egg(self.x + random.uniform(-2, 2), self.y + random.uniform(-2, 2), self.simulation, genome, incubation_time, survival_chance)
                    self.simulation.egg_list.append(egg)
                self.after_birth_period = self.after_birth_duration / 4.5
            else:
                self.is_pregnant = True
                self.child_genome = kid_genomes
        else:
            if partner.is_egglayer:
                for genome in kid_genomes:
                    incubation_time = random.randint(100, 150) if partner.is_predator else random.randint(80, 110)
                    survival_chance = 0.88 if not partner.is_predator else 0.73
                    egg = Egg(partner.x + random.uniform(-2, 2), partner.y + random.uniform(-2, 2), self.simulation, genome, incubation_time, survival_chance)
                    self.simulation.egg_list.append(egg)
                partner.after_birth_period = self.after_birth_duration / 4.5
            else:
                partner.is_pregnant = True
                partner.child_genome = kid_genomes

        self.energy -= energy_cost if not (not self.is_male and self.is_egglayer) else energy_cost * 0.55
        partner.energy -= energy_cost if not (not partner.is_male and partner.is_egglayer) else energy_cost * 0.55
        self.ready_to_mate = False
        partner.ready_to_mate = False
        return None

    def give_birth(self):
        if self.is_dead or not self.is_pregnant or self.is_egglayer:
            return None

        if self.pregnancy_timer < self.pregnancy_duration:
            self.pregnancy_timer += 1
            return None

        self.is_pregnant = False
        self.pregnancy_timer = 0
        kids = []
        for i in range(self.kids_num):
            kids.append(Fish(self.x, self.y, self.simulation, 20, self.child_genome[i]))
        self.child_genome = None
        self.kids_num = None
        self.energy -= 5 * (1 + self.metabolism * 0.25)
        self.after_birth_period = self.after_birth_duration
        return kids

    def draw(self, screen, show_vision, show_targets):
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
        if show_targets and not self.is_dead and self.energy < self.max_energy * 0.95:
            if self.is_predator and self.nearest_prey and math.hypot(self.nearest_prey.x - self.x, self.nearest_prey.y - self.y) < self.vision:
                pygame.draw.line(screen, (255, 0, 0), (int(self.x), int(self.y)), (int(self.nearest_prey.x), int(self.nearest_prey.y)))
            elif self.is_predator and self.nearest_food and math.hypot(self.nearest_food.x - self.x, self.nearest_food.y - self.y) < self.vision:
                pygame.draw.line(screen, (255, 0, 0), (int(self.x), int(self.y)), (int(self.nearest_food.x), int(self.nearest_food.y)))
            elif not self.is_predator and self.nearest_food:
                if isinstance(self.nearest_food, tuple):
                    _, (target_x, target_y) = self.nearest_food
                else: 
                    target_x, target_y = self.nearest_food.x, self.nearest_food.y
                if math.hypot(target_x - self.x, target_y - self.y) < self.vision:
                    pygame.draw.line(screen, (0, 255, 0), (int(self.x), int(self.y)), (int(target_x), int(target_y)))
            elif self.nearest_mate and self.ready_to_mate and math.hypot(self.nearest_mate.x - self.x, self.nearest_mate.y - self.y) < self.mate_vision:
                pygame.draw.line(screen, (255, 255, 0), (int(self.x), int(self.y)), (int(self.nearest_mate.x), int(self.nearest_mate.y)))

        # Відображення риби
        if self.is_dead:
            pygame.draw.circle(screen, (100, 100, 100), (int(self.x), int(self.y)), int(self.size))
        else:
            if self.is_predator:
                pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), int(self.size) + 2, 1)
            if self.ready_to_mate:
                pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), int(self.size) + 3, 1)
            if self.is_pregnant:
                pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), int(self.size) + 4, 1)
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