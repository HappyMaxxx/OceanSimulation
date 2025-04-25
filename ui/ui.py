import math
from typing import TYPE_CHECKING

import pygame

from core.settings import HEIGHT, MAX_OXYGEN, MAX_TEMP, MIN_OXYGEN, MIN_TEMP, WIDTH

if TYPE_CHECKING:
    from core.simulation import Simulation


class UI:
    def __init__(self, simulation: 'Simulation', screen, clock) -> None:
        self.simulation = simulation
        self.font = pygame.font.Font(None, 24)
        self.screen = screen
        self.clock = clock

    def draw_statistic(self):
        predators = [f for f in self.simulation.fish_population if f.is_predator and not f.is_dead]
        prey = [f for f in self.simulation.fish_population if not f.is_predator and not f.is_dead]

        sim = self.simulation

        if self.simulation.show_stats:
            stats = self.font.render(f"Fish: {len([f for f in sim.fish_population if not f.is_dead])} "
                                f"Algae: {len(sim.algae_list)} Plankton: {len(sim.plankton_list)} "
                                f"Crustaceans: {len(sim.crustacean_list)} Dead Parts: {len(sim.dead_algae_parts)} "
                                f"Pregnants: {len([f for f in sim.fish_population if f.is_pregnant and not f.is_dead])} "
                                f"Eggs: {len(sim.egg_list)} ",
                                True, (255, 255, 255))
            self.screen.blit(stats, (10, 10))

            prey_gender_stats = self.font.render(f"Prey ({len(prey)}) - Male: {len([f for f in prey if f.is_male])} "
                                            f"Female: {len([f for f in prey if not f.is_male])}",
                                            True, (255, 255, 255))
            self.screen.blit(prey_gender_stats, (10, 30))

            predator_gender_stats = self.font.render(f"Predators ({len(predators)}) - Male: {len([f for f in predators if f.is_male])} "
                                                f"Female: {len([f for f in predators if not f.is_male])}",
                                                True, (255, 255, 255))
            self.screen.blit(predator_gender_stats, (10, 50))

            time_info = self.font.render(f"Phase: {sim.day_phase} {sim.time // sim.day_length:.0f} ({sim.time}) "
                                    f"Season: {sim.seasons[sim.current_season_index]}", 
                                    True, (255, 255, 255))
            self.screen.blit(time_info, (10, 70))
        
        if self.simulation.paused:
            pause_text = self.font.render("PAUSED", True, (255, 255, 255))
            self.screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - pause_text.get_height()//2))

        if self.simulation.show_fps:
            fps = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, (255, 255, 255))
            self.screen.blit(fps, (10, HEIGHT - 15))

        # pygame.draw.line(screen, (255, 255, 255), (0, LINE_LEVEL), (WIDTH, LINE_LEVEL), 1)
    
    def draw_active_modes(self):
        x_pos = WIDTH - 100 
        y_pos = 10  

        for mode in self.simulation.modes.active_modes:
            if mode == "Vision":
                mode_text = self.font.render("Vision", True, (255, 255, 255))
            elif mode == "Targets":
                mode_text = self.font.render("Targets", True, (255, 255, 255))
            elif mode == 'Temp Map':
                mode_text = self.font.render("Temp Map", True, (255, 255, 255))
            elif mode == 'Oxy Map':
                mode_text = self.font.render("Oxy Map", True, (255, 255, 255))
            elif mode == 'Current':
                mode_text = self.font.render("Current", True, (255, 255, 255))
            elif mode == 'Creative':
                mode_text = self.font.render("Creative", True, (255, 255, 255))
            elif mode == 'Plankton':
                mode_text = self.font.render("Plankton", True, (255, 255, 255))
            elif mode == 'Crustacean':
                mode_text = self.font.render("Crustacean", True, (255, 255, 255))
            elif mode == 'Fish':
                mode_text = self.font.render("Fish", True, (255, 255, 255))
            elif mode == 'Deleting':
                mode_text = self.font.render("Deleting", True, (255, 255, 255))
            else:
                continue

            self.screen.blit(mode_text, (x_pos, y_pos))
            y_pos += 20
    
    def draw_maps(self):
        map_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        if self.simulation.modes.show_temp_map:
            for y in range(0, HEIGHT, 10):
                for x in range(0, WIDTH, 10):
                    temp = self.simulation.get_temperature(x, y)
                    red = min(255, max(int((temp - MIN_TEMP) / (MAX_TEMP - MIN_TEMP) * 255), 0))
                    blue = min(255, max(int((MAX_TEMP - temp) / (MAX_TEMP - MIN_TEMP) * 255), 0))
                    pygame.draw.rect(map_surface, (red, 0, blue, 100), (x, y, 10, 10))
            self.screen.blit(map_surface, (0, 0))
        
        elif self.simulation.modes.show_oxygen_map:
            for y in range(0, HEIGHT, 10):
                for x in range(0, WIDTH, 10):
                    oxygen = self.simulation.get_oxygen(x, y, self.simulation.algae_list)
                    green = min(255, int((oxygen - MIN_OXYGEN) / (MAX_OXYGEN - MIN_OXYGEN) * 255))
                    pygame.draw.rect(map_surface, (0, green, 0, 100), (x, y, 10, 10))
            self.screen.blit(map_surface, (0, 0))

    def generate_colors(self, num_layers):
        colors = []
        for layer in range(num_layers):
            t = layer / (num_layers - 1) if num_layers > 1 else 0

            red = int(255 - (255 - 200) * t)
            green = int(200 + (255 - 200) * (1 - abs(1 - 2 * t)))
            blue = int(200 + (255 - 200) * t)
            colors.append((red, green, blue, 1))
        return colors

    def draw_current(self):
        if self.simulation.modes.show_current:
            grid = self.simulation.current_grid
            arrow_length = 15
            
            colors = self.generate_colors(grid.layers)
            
            for layer in range(1, grid.layers):
                boundary = grid.layer_boundaries[layer]
                points = [(col * grid.grid_size, boundary[col]) for col in range(len(boundary))]
                if len(points) > 1:
                    pygame.draw.lines(self.screen, (255, 255, 255, 50), False, points, 1)
            
            for (col, row), current in grid.grid.items():
                strength = current["strength"]
                direction = current["direction"]
                x = col * grid.grid_size + grid.grid_size / 2
                y = row * grid.grid_size + grid.grid_size / 2
                
                layer = grid.get_layer_at(x, y)
                color = colors[layer]  
                
                end_x = x + arrow_length * math.cos(direction) * strength * 2
                end_y = y + arrow_length * math.sin(direction) * strength * 2
                
                pygame.draw.line(self.screen, color, (x, y), (end_x, end_y), 2)
                
                arrow_head_size = 5
                angle_offset = math.pi / 6
                left_wing_x = end_x - arrow_head_size * math.cos(direction + angle_offset)
                left_wing_y = end_y - arrow_head_size * math.sin(direction + angle_offset)
                right_wing_x = end_x - arrow_head_size * math.cos(direction - angle_offset)
                right_wing_y = end_y - arrow_head_size * math.sin(direction - angle_offset)
                
                pygame.draw.line(self.screen, color, (end_x, end_y), (left_wing_x, left_wing_y), 2)
                pygame.draw.line(self.screen, color, (end_x, end_y), (right_wing_x, right_wing_y), 2)

    def draw_generation_progress(self):
        self.screen.blit(self.simulation.background, (0, 0))
        
        for algae in self.simulation.algae_list:
            algae.draw(self.screen)
        for plankton in self.simulation.plankton_list:
            plankton.draw(self.screen)
        for crust in self.simulation.crustacean_list:
            crust.draw(self.screen)
        for fish in self.simulation.fish_population:
            fish.draw(self.screen, False, False)
        
        progress = self.simulation.generation_step / self.simulation.max_generation_steps * 100
        generation_text = self.font.render(f"Water generating: {progress:.1f}%", True, (255, 255, 255))
        self.screen.blit(generation_text, (WIDTH // 2 - generation_text.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()

    def draw(self):
        self.draw_maps()
        self.draw_current()
        self.draw_active_modes()
        self.draw_statistic()