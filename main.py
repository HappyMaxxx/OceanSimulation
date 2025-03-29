import pygame
import random
import math
import tkinter as tk
from threading import Thread

from settings import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fish Evolution - Food Decay")
font = pygame.font.Font(None, 36)
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
        
        self.is_male = random.choice([True, False])
        
        self.age = 0
        self.max_size = (sum(self.genome["size"]) / 2) * (10 if self.is_predator else 6) + (5 if self.is_predator else 3)
        
        if self.is_predator:
            self.speed = (sum(self.genome["speed"]) / 2) * 1.5 + 0.5
            self.size = 3
            self.vision = (sum(self.genome["vision"]) / 2) * 100 + 50
            self.mate_vision = (sum(self.genome["vision"]) / 2) * 150 + 75
            self.reproduction_rate = (sum(self.genome["reproduction"]) / 2) * 0.1
            self.energy_threshold = 40
        else:
            self.speed = (sum(self.genome["speed"]) / 2) * 2.5 + 1
            self.size = 2
            self.vision = (sum(self.genome["vision"]) / 2) * 60 + 30
            self.mate_vision = (sum(self.genome["vision"]) / 2) * 80 + 40
            self.reproduction_rate = (sum(self.genome["reproduction"]) / 2) * 0.3
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

        self.age += 0.1
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
        if (not partner or not self.ready_to_mate or not partner.ready_to_mate or 
            self.is_predator != partner.is_predator or self.is_dead or partner.is_dead or 
            self.is_male == partner.is_male):
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
                    text=f"Age: {self.fish.age:.1f}",
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
        self.food_list = [Food(random.randint(0, WIDTH), random.randint(0, HEIGHT))
                        for _ in range(INITIAL_FOOD)]
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
                if random.random() < 0.05:
                    if random.random() < 0.7:
                        self.food_list.append(Food(random.randint(0, WIDTH), random.randint(int(HEIGHT/2), HEIGHT)))
                    else:
                        self.food_list.append(Food(random.randint(0, WIDTH), random.randint(0, int(HEIGHT/2))))
                
                new_fish = []
                for fish in self.fish_population[:]:
                    fish.check_mating_readiness()
                    
                    nearest_food = fish.find_nearest_food(self.food_list) if not fish.is_predator else None
                    nearest_prey = fish.find_nearest_prey(self.fish_population) if fish.is_predator and not fish.is_dead else None
                    nearest_mate = fish.find_nearest_mate(self.fish_population) if not fish.is_dead else None
                    
                    predators = [f for f in self.fish_population if f.is_predator and not f.is_dead]
                    fish.move(nearest_food, nearest_prey, nearest_mate, predators)
                    fish.eat(self.food_list, self.fish_population)
                    
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
                
                for food in self.food_list[:]:
                    food.update()
                    if food.lifetime <= 0:
                        self.food_list.remove(food)

            for food in self.food_list:
                green = int(255 * (food.lifetime / food.initial_lifetime))
                pygame.draw.circle(screen, (0, green, 0), (int(food.x), int(food.y)), 3)
                
            for fish in self.fish_population:
                fish.draw(screen)
            
            predators = len([f for f in self.fish_population if f.is_predator and not f.is_dead])
            stats = font.render(f"Fish: {len([f for f in self.fish_population if not f.is_dead])} Predators: {predators}  Food: {len(self.food_list)}",
                              True, (255, 255, 255))
            screen.blit(stats, (10, 10))
            
            if self.paused:
                pause_text = font.render("PAUSED", True, (255, 255, 255))
                screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - pause_text.get_height()//2))
            
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    sim = Simulation()
    sim.run()
    pygame.quit()