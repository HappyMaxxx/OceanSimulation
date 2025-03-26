import pygame
import random
import math

from settings import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fish Evolution - Food Decay")
clock = pygame.time.Clock()

class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        if y < HEIGHT / 3:
            self.energy_value = random.randint(20, 40)
        else:
            self.energy_value = random.randint(5, 15)
        self.lifetime = FOOD_LIFETIME
        self.initial_lifetime = FOOD_LIFETIME  

    def update(self):
        self.lifetime -= 1 

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
        
        self.age = 0
        self.max_size = (sum(self.genome["size"]) / 2) * (10 if self.is_predator else 6) + (5 if self.is_predator else 3)
        
        if self.is_predator:
            self.speed = (sum(self.genome["speed"]) / 2) * 1.5 + 0.5
            self.size = 3
            self.vision = (sum(self.genome["vision"]) / 2) * 100 + 50        # Зір для їжі/здобичі
            self.mate_vision = (sum(self.genome["vision"]) / 2) * 150 + 75  # Більший зір для розмноження
            self.reproduction_rate = (sum(self.genome["reproduction"]) / 2) * 0.1
            self.energy_threshold = 40
        else:
            self.speed = (sum(self.genome["speed"]) / 2) * 2.5 + 1
            self.size = 2
            self.vision = (sum(self.genome["vision"]) / 2) * 60 + 30         # Зір для їжі
            self.mate_vision = (sum(self.genome["vision"]) / 2) * 80 + 40   # Більший зір для розмноження
            self.reproduction_rate = (sum(self.genome["reproduction"]) / 2) * 0.3
            self.energy_threshold = 20
        
        self.metabolism = sum(self.genome["metabolism"]) / 2
        self.digestion = sum(self.genome["digestion"]) / 2
        self.defense = sum(self.genome["defense"]) / 2
        self.preferred_depth = (sum(self.genome["preferred_depth"]) / 2) * HEIGHT
        
        self.speed *= (1 - self.size / 20)
        self.speed += self.metabolism * 0.5
        
        self.color = (
            max(0, min(255, int(self.genome["color"][0] * (100 if self.is_predator else 255)))),
            max(0, min(255, int((100 + self.size * 10) * (0.5 if self.is_predator else 1)))),
            max(0, min(255, int(self.genome["color"][1] * (100 if self.is_predator else 255))))
        )
        self.direction = random.uniform(-math.pi/2, math.pi/2)
        self.ready_to_mate = False
        self.turn_speed = 0.1 if not self.is_predator else 0.08
        self.tail_angle = 0
        self.tail_speed = 0.2
        self.is_dead = False
        self.float_speed = 0.5
    
    def grow(self):
        if not self.is_dead and self.size < self.max_size:
            growth_rate = 0.01 * (self.energy / MAX_ENERGY) * (1 + self.metabolism)
            self.size = min(self.max_size, self.size + growth_rate)
            self.speed = ((sum(self.genome["speed"]) / 2) * (1.5 if self.is_predator else 2.5) + 
                         (0.5 if self.is_predator else 1)) * (1 - self.size / 20) + self.metabolism * 0.5
    
    def find_nearest_food(self, food_list):
        if not food_list:
            return None
        return min(food_list, key=lambda f: math.hypot(f.x - self.x, f.y - self.y))
    
    def find_nearest_prey(self, fish_list):
        if not fish_list:
            return None
        potential_prey = [f for f in fish_list if f != self and (f.size + 3 < self.size or f.is_dead)]
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
    
    def move(self, target_food=None, target_prey=None, target_mate=None, predators=None):
        if self.is_dead:
            self.y -= self.float_speed
            if self.y <= 0:
                return
            return

        self.age += 1
        self.grow()

        current_strength = (HEIGHT - self.y) / HEIGHT * 0.5
        self.x += current_strength

        nearest_predator = None
        if predators:
            if self.is_predator:
                bigger_predators = [p for p in predators if p.size > self.size and p != self]
                if bigger_predators:
                    nearest_predator = min(bigger_predators, key=lambda p: math.hypot(p.x - self.x, p.y - self.y))
            else:
                nearest_predator = min(predators, key=lambda p: math.hypot(p.x - self.x, p.y - self.y), default=None)

        if self.is_predator and self.energy < MAX_ENERGY * 0.2: 
            self.preferred_depth = random.uniform(0, HEIGHT / 3)
        elif self.is_predator and self.energy > MAX_ENERGY * 0.8: 
            self.preferred_depth = (sum(self.genome["preferred_depth"]) / 2) * HEIGHT

        # Пріоритет дій:
        # 1. Втеча від хижака
        # 2. Розмноження (якщо готові)
        # 3. Полювання/пошук їжі
        # 4. Рух до preferred_depth
        
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
        elif self.is_predator and target_prey and math.hypot(target_prey.x - self.x, target_prey.y - self.y) < self.vision:
            # Полювання для хижаків - третій пріоритет
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
        elif not self.is_predator and target_food and math.hypot(target_food.x - self.x, target_food.y - self.y) < self.vision:
            # Пошук їжі для не-хижаків - третій пріоритет
            desired_angle = math.atan2(target_food.y - self.y, target_food.x - self.x)
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
            # Рух до preferred_depth - найнижчий пріоритет
            desired_angle = math.atan2(self.preferred_depth - self.y, 10)
            angle_diff = desired_angle - self.direction
            angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
            if abs(angle_diff) > self.turn_speed / 2:
                self.direction += (self.turn_speed / 2) if angle_diff > 0 else -(self.turn_speed / 2)
            self.direction = max(-math.pi/2, min(math.pi/2, self.direction))
            self.x += math.cos(self.direction) * self.speed
            self.y += math.sin(self.direction) * self.speed

        if self.x > WIDTH + self.size:
            self.x = -self.size
        elif self.x < -self.size:
            self.x = WIDTH + self.size
        self.y = max(self.size, min(HEIGHT - self.size, self.y))

        energy_cost = self.speed * self.size * 0.01 * self.metabolism * (1 - self.defense * 0.5)
        self.energy -= energy_cost
    
    def eat(self, food_list, fish_list):
        if self.is_dead:
            return
        
        if self.is_predator:
            for prey in fish_list[:]:
                if prey != self and (prey.size + 3 < self.size or prey.is_dead):
                    distance = math.hypot(self.x - prey.x, self.y - prey.y)
                    if distance < self.size + prey.size:
                        energy_gain = prey.energy * (0.5 + self.digestion * 0.5)
                        if prey.is_dead:
                            energy_gain *= 0.7
                        self.energy = min(MAX_ENERGY, self.energy + energy_gain)
                        fish_list.remove(prey)
        else:
            for food in food_list[:]:
                distance = math.hypot(self.x - food.x, self.y - food.y)
                if distance < self.size + 5:
                    energy_gain = food.energy_value * (0.5 + self.digestion * 0.5)
                    self.energy = min(MAX_ENERGY, self.energy + energy_gain)
                    food_list.remove(food)
    
    def check_mating_readiness(self):
        if not self.is_dead:
            self.ready_to_mate = self.energy > self.energy_threshold and random.random() < self.reproduction_rate
    
    def mate(self, partner):
        if not partner or not self.ready_to_mate or not partner.ready_to_mate or self.is_predator != partner.is_predator or self.is_dead or partner.is_dead:
            return None
        
        distance = math.hypot(self.x - partner.x, self.y - partner.y)
        if distance > (self.size + partner.size) * 2:
            return None
        
        if self.energy < 30 or partner.energy < 30:
            return None
        
        child_genome = {}
        for key in self.genome:
            self_allele = random.choice(self.genome[key])
            partner_allele = random.choice(partner.genome[key])
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
                pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), int(self.size) + 1, 1)

            if self.ready_to_mate:
                pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), int(self.size) + 2, 1)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))
        self.tail_angle += self.tail_speed * self.speed if not self.is_dead else 0
        tail_offset = math.sin(self.tail_angle) * self.size * 0.3
        tail_x = self.x - math.cos(self.direction) * self.size * 1.5
        tail_y = self.y - math.sin(self.direction) * self.size * 0.5 + tail_offset
        pygame.draw.line(screen, (255, 255, 255), (int(self.x), int(self.y)), 
                        (int(tail_x), int(tail_y)), 2)


def draw_background(screen):
    for y in range(HEIGHT):
        blue = max(0, int(255 - (y / HEIGHT) * 205))
        green = max(0, int(150 - (y / HEIGHT) * 150))
        red = max(0, int(50 - (y / HEIGHT) * 50))
        pygame.draw.line(screen, (red, green, blue), (0, y), (WIDTH, y))

fish_population = [Fish(random.randint(0, WIDTH), random.randint(0, HEIGHT), 50) 
                  for _ in range(NUM_FISH)]
food_list = [Food(random.randint(0, WIDTH), random.randint(0, HEIGHT)) 
             for _ in range(INITIAL_FOOD)]

running = True
font = pygame.font.Font(None, 36)

while running:
    draw_background(screen)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    if random.random() < 0.05:
        if random.random() < 0.7:
            food_list.append(Food(random.randint(0, WIDTH), random.randint(int(HEIGHT/2), HEIGHT)))
        else:
            food_list.append(Food(random.randint(0, WIDTH), random.randint(0, int(HEIGHT/2))))
    
    new_fish = []
    for fish in fish_population[:]:
        fish.check_mating_readiness()
        
        nearest_food = fish.find_nearest_food(food_list) if not fish.is_predator else None
        nearest_prey = fish.find_nearest_prey(fish_population) if fish.is_predator and not fish.is_dead else None
        nearest_mate = fish.find_nearest_mate(fish_population) if not fish.is_dead else None
        
        predators = [f for f in fish_population if f.is_predator and not f.is_dead]
        fish.move(nearest_food, nearest_prey, nearest_mate, predators)
        fish.eat(food_list, fish_population)
        
        if fish.ready_to_mate and nearest_mate:
            baby = fish.mate(nearest_mate)
            if baby:
                new_fish.append(baby)
        
        if fish.energy <= 0 and not fish.is_dead:
            fish.is_dead = True
            fish.energy = max(fish.energy, 10)
        if fish.is_dead and fish.y <= 0:
            fish_population.remove(fish)
    
    fish_population.extend(new_fish)
    
    for food in food_list[:]:
        food.update()
        if food.lifetime <= 0:
            food_list.remove(food)
        else:
            green = int(255 * (food.lifetime / food.initial_lifetime))
            pygame.draw.circle(screen, (0, green, 0), (int(food.x), int(food.y)), 3)
    
    for fish in fish_population:
        fish.draw(screen)
    
    predators = len([f for f in fish_population if f.is_predator and not f.is_dead])
    stats = font.render(f"Fish: {len(fish_population)}  Predators: {predators}  Food: {len(food_list)}",
                         True, (255, 255, 255)
                        )
    screen.blit(stats, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()