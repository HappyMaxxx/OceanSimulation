import math
import random

import pygame

from core.environment import CurrentGrid
from core.event_handler import EventHandler
from core.mode_manager import ModeManager
from entities.algae import Algae
from entities.fish import Fish
from entities.simple_organisms import Crustacean, Plankton
from plots.plot import Plot
from ui.ui import UI
from core.settings import *


class Simulation:
    def __init__(self, screen, clock):
        # Environment parameters
        self.screen = screen
        self.clock = clock

        # Core managers and UI
        self.event_handler = EventHandler(self)
        self.ui = UI(self, screen, clock)
        self.modes = ModeManager()
        self.plot = Plot(self)

        # Game objects
        self.dead_algae_parts = []
        self.egg_list = []

        # Game state
        self.running = True
        self.paused = False
        self.show_stats = True
        self.show_fps = False

        # Background and grids
        self.background = self.create_background(WIDTH, HEIGHT)
        self.grid_size = 10
        self.grid_cell_size = 50
        self.oxygen_grid = {}
        self.temperature_grid = {}
        self.algae_grid = {}

        # Time and seasons
        self.time = 0 
        self.day_length = DAY_LENGTH
        self.season_length = SEASON_LENGTH
        self.seasons = ["Spring", "Summer", "Autumn", "Winter"]
        self.current_season_index = 0
        self.day_phase = "Day"
        self.prev_season_modifier = 0.8
        self.current_season_modifier = 1.0

        # Water currents
        self.current_strength = 0.3
        self.current_direction = 0.0  # in radians
        self.vertical_current_strength = 0.0

        self.target_strength = 0.3
        self.target_direction = 0.0
        self.target_vertical_strength = 0.0

        self.current_change_timer = 0
        self.current_change_interval = DAY_LENGTH * 3.5
        self.current_grid = CurrentGrid(self, WIDTH, HEIGHT, 50, layers=5)

        # Generation logic
        self.is_generating = False
        self.generation_step = 0
        self.max_generation_steps = 1000
        self.generation_objects = []
        self.algae_to_grow = []

        # Randomness and frame tracking
        self.random_buffer = [random.random() for _ in range(1000)]
        self.random_index = 0
        self.frame_counter = 0

    def get_random(self):
        self.random_index = (self.random_index + 1) % len(self.random_buffer)
        if self.random_index == 0:
            self.random_buffer = [random.random() for _ in range(1000)]
        return self.random_buffer[self.random_index]
    
    def add_segment_to_grid(self, seg_x, seg_y, algae):
        grid_x = int(seg_x // self.grid_cell_size)
        grid_y = int(seg_y // self.grid_cell_size)
        key = (grid_x, grid_y)
        if key not in self.algae_grid:
            self.algae_grid[key] = []
        self.algae_grid[key].append((seg_x, seg_y, algae))

    def remove_segment_from_grid(self, seg_x, seg_y, algae):
        grid_x = int(seg_x // self.grid_cell_size)
        grid_y = int(seg_y // self.grid_cell_size)
        key = (grid_x, grid_y)
        if key in self.algae_grid:
            self.algae_grid[key] = [seg for seg in self.algae_grid[key]
                                    if not (seg[0] == seg_x and seg[1] == seg_y and seg[2] == algae)]
            if not self.algae_grid[key]:
                del self.algae_grid[key]

    def get_nearby_segments(self, x, y):
        grid_x = int(x // self.grid_cell_size)
        grid_y = int(y // self.grid_cell_size)
        nearby_segments = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                key = (grid_x + dx, grid_y + dy)
                if key in self.algae_grid:
                    nearby_segments.extend(self.algae_grid[key])
        return nearby_segments

    def start_generation(self):
        self.is_generating = True
        self.generation_step = 0
        self.paused = True

        self.algae_list = [Algae(random.randint(0, WIDTH), HEIGHT, self) for _ in range(INITIAL_ALGAE)]
        for algae in self.algae_list:
            self.add_segment_to_grid(algae.segments[0][0], algae.segments[0][1], algae)
        self.plankton_list = [] 
        self.crustacean_list = []  
        self.fish_population = []  

    def update_generation(self):
        if not self.is_generating or self.generation_step >= self.max_generation_steps:
            self.is_generating = False
            self.paused = False
            self.update_oxygen_grid()
            self.update_temperature_grid()
            return

        # Event handling to avoid the “Program does not respond” message
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.is_generating = False

        self.random_buffer.append(random.random())
        for algae in self.algae_list:
            if algae.is_alive and self.get_random() < 0.2:
                algae.grow()
                algae.growth_timer = min(algae.growth_timer, round(random.uniform(*ALGAE_GROW)/10))

        if len(self.plankton_list) < INITIAL_PLANKTON and self.get_random() < 0.05: 
            self.plankton_list.append(Plankton(random.randint(0, WIDTH), random.randint(0, int(HEIGHT/1.5))))

        if len(self.crustacean_list) < INITIAL_CRUSTACEANS and self.get_random() < 0.02:  
            self.crustacean_list.append(Crustacean(random.randint(0, WIDTH), random.randint(int(HEIGHT / 3), HEIGHT)))

        if len(self.fish_population) < NUM_FISH and self.get_random() < 0.1:  
            self.fish_population.append(Fish(random.randint(0, WIDTH), random.randint(0, LINE_LEVEL - random.randint(0, 20)),
                                            self, random.randint(40, 60)))

        self.generation_step += 1

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
        
        self.current_grid.update(self)

        target_season_modifier = {"Spring": 1.0, "Summer": 1.1, "Autumn": 0.9, "Winter": 0.8}[self.seasons[self.current_season_index]]
        transition_duration = self.season_length * 0.1 
        if self.time % self.season_length < transition_duration:
            progress = (self.time % self.season_length) / transition_duration
            self.current_season_modifier = self.prev_season_modifier + (target_season_modifier - self.prev_season_modifier) * progress
        elif self.time % self.season_length > self.season_length - transition_duration:
            progress = ((self.season_length - (self.time % self.season_length)) / transition_duration)
            next_season_index = (self.current_season_index + 1) % 4
            next_season_modifier = {"Spring": 1.0, "Summer": 1.1, "Autumn": 0.9, "Winter": 0.8}[self.seasons[next_season_index]]
            self.current_season_modifier = target_season_modifier + (next_season_modifier - target_season_modifier) * (1 - progress)
        else:
            self.current_season_modifier = target_season_modifier
        
        if self.time % self.season_length == 0:
            self.prev_season_modifier = target_season_modifier

        if self.time == self.season_length * 4:
            self.time = 0
            self.current_season_index = 0
            self.prev_season_modifier = 0.8
            self.current_season_modifier = 1.0

    def update_temperature_grid(self):
        self.temperature_grid.clear()
        grid_width = WIDTH // self.grid_size 
        grid_height = HEIGHT // self.grid_size

        for gy in range(grid_height):
            y = gy * self.grid_size
            depth_factor = 1 - (y / HEIGHT)
            base_temp = MIN_TEMP + (MAX_TEMP - MIN_TEMP) * depth_factor
            for gx in range(grid_width):
                self.temperature_grid[(gx, gy)] = base_temp

        day_progress = (self.time % self.day_length) / self.day_length
        day_night_modifier = 0.95 + 0.05 * math.sin(day_progress * 2 * math.pi)

        season = self.seasons[self.current_season_index]
        season_modifier = {"Spring": 1.0, "Summer": 1.1, "Autumn": 0.9, "Winter": 0.8}[season]

        for (gx, gy), temp in self.temperature_grid.items():
            self.temperature_grid[(gx, gy)] = temp * day_night_modifier * season_modifier

    def get_temperature(self, x, y):
        gx = int(x // self.grid_size)
        gy = int(y // self.grid_size)
        
        return self.temperature_grid.get((gx, gy), MIN_TEMP)

    def update_oxygen_grid(self):
        self.oxygen_grid.clear()
        grid_width = WIDTH // self.grid_size
        grid_height = HEIGHT // self.grid_size 

        for gy in range(grid_height):
            y = gy * self.grid_size
            depth_factor = y / HEIGHT
            base_oxygen = MAX_OXYGEN - (MAX_OXYGEN - MIN_OXYGEN) * depth_factor
            for gx in range(grid_width):
                self.oxygen_grid[(gx, gy)] = base_oxygen

        day_progress = (self.time % self.day_length) / self.day_length
        day_night_factor = 0.5 + 0.5 * math.sin(day_progress * 2 * math.pi - math.pi / 2)

        season = self.seasons[self.current_season_index]
        season_modifier = {"Spring": 1.0, "Summer": 1.2, "Autumn": 0.9, "Winter": 0.7}[season]

        for algae in self.algae_list:
            for seg_x, seg_y in algae.segments:
                gx = int(seg_x // self.grid_size)
                gy = int(seg_y // self.grid_size)
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        grid_x = gx + dx
                        grid_y = gy + dy
                        if (grid_x, grid_y) in self.oxygen_grid:
                            center_x = grid_x * self.grid_size + self.grid_size / 2
                            center_y = grid_y * self.grid_size + self.grid_size / 2
                            distance = math.hypot(center_x - seg_x, center_y - seg_y)
                            if distance < OXYGEN_BOOST_RADIUS:
                                boost = OXYGEN_BOOST * (1 - distance / OXYGEN_BOOST_RADIUS) * day_night_factor * season_modifier
                                self.oxygen_grid[(grid_x, grid_y)] = min(
                                    MAX_OXYGEN, self.oxygen_grid[(grid_x, grid_y)] + boost
                                )

    def get_oxygen(self, x, y, algae_list):
        gx = int(x // self.grid_size)
        gy = int(y // self.grid_size)
        
        return self.oxygen_grid.get((gx, gy), MIN_OXYGEN)

    def run(self):
        while self.running:
            self.screen.blit(self.background, (0, 0))
            if not self.is_generating:
                self.event_handler.handle_events()

            if self.is_generating:
                self.update_generation()
                self.ui.draw_generation_progress()
            if not self.paused:
                self.update_time()
                self.plot.update()
                self.update_temperature_grid()
                self.update_oxygen_grid()
                
                # TODO: change
                if len([f for f in self.fish_population if not f.is_dead]) < 1:
                    self.plot.show()
                    self.running = False
                    continue

                season = self.seasons[self.current_season_index]
                spawn_rate_modifier = {"Spring": 1.1, "Summer": 1.2, "Autumn": 0.9, "Winter": 0.7}[season]

                if self.get_random() < 0.3 * spawn_rate_modifier:
                    if self.get_random() < 0.0035 and len(self.algae_list) < MAX_ALGAE:
                        new_x = random.randint(0, WIDTH)
                        new_algae = Algae(new_x, HEIGHT, self)
                        self.algae_list.append(new_algae)
                        self.add_segment_to_grid(new_x, HEIGHT, new_algae)
                    elif self.get_random() < 0.15:
                        self.plankton_list.append(Plankton(random.randint(0, WIDTH), random.randint(0, int(HEIGHT/1.5))))
                    elif self.get_random() < 0.05:
                        self.crustacean_list.append(Crustacean(random.randint(0, WIDTH), random.randint(int(HEIGHT / 3), HEIGHT)))

                new_fish = []
                for fish in self.fish_population[:]:
                    fish.check_mating_readiness()

                    predators = [f for f in self.fish_population if f.is_predator and not f.is_dead] 

                    fish.move(predators, self.fish_population)
                    fish.eat(self.fish_population)
                    kids = fish.give_birth()

                    if kids:
                        for kid in kids:
                            new_fish.append(kid)

                    if fish.ready_to_mate and fish.nearest_mate:
                        fish.mate(fish.nearest_mate)
                    
                    if fish.energy <= 0 and not fish.is_dead:
                        fish.is_dead = True
                        fish.energy = random.randint(5, 15) + fish.size * 0.5
                    
                    if fish.is_dead and fish.y <= 0:
                        self.fish_population.remove(fish)

                self.fish_population.extend(new_fish)

                if self.frame_counter % 2 == 0:
                    for algae in self.algae_list[:]:
                        algae.update(self.algae_list, self.dead_algae_parts)
                        if not algae.segments:
                            self.algae_list.remove(algae)

                    for plankton in self.plankton_list[:]:
                        plankton.update()
                        if plankton.lifetime <= 0:
                            self.plankton_list.remove(plankton)

                    for dead_part in self.dead_algae_parts[:]:
                        dead_part.update()
                        if dead_part.lifetime <= 0 or dead_part.y <= 0:
                            self.dead_algae_parts.remove(dead_part)
                    
                    for crust in self.crustacean_list[:]:
                        crust.update()
                        if crust.lifetime <= 0:
                            self.crustacean_list.remove(crust)

                    for egg in self.egg_list[:]:
                        if not egg.update():
                            self.egg_list.remove(egg)
                        else:
                            hatched_fish = egg.hatch()
                            if hatched_fish:
                                self.fish_population.append(hatched_fish)
                                self.egg_list.remove(egg)

                self.frame_counter += 1

            if not self.is_generating:
                for algae in self.algae_list:
                    algae.draw(self.screen)
                for crust in self.crustacean_list:
                    crust.draw(self.screen)
                for plankton in self.plankton_list:
                    plankton.draw(self.screen)
                for dead_part in self.dead_algae_parts:
                    dead_part.draw(self.screen)
                for egg in self.egg_list:
                    egg.draw(self.screen)

                for fish in self.fish_population:
                    fish.draw(self.screen, self.modes.show_vision, self.modes.show_targets)

                self.ui.draw()

            pygame.display.flip()
            self.clock.tick(25)