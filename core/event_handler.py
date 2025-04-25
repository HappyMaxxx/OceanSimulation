from typing import TYPE_CHECKING

import pygame

from entities.simple_organisms import Crustacean, Plankton
from ui.fish_windows import FishCreationWindow, FishDetailsWindow
from core.settings import MOUSE_CLICK

if TYPE_CHECKING:
    from core.simulation import Simulation

class EventHandler:
    def __init__(self, simulation: 'Simulation') -> None:
        self.simulation = simulation

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.simulation.running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                if 'Creative' in self.simulation.modes.active_modes:
                    if not MOUSE_CLICK:
                        if event.button != 1:
                            break
                        
                    if 'Plankton' in self.simulation.modes.active_modes \
                                and 'Deleting' not in self.simulation.modes.active_modes \
                                    and event.button == 1:
                        self.simulation.plankton_list.append(Plankton(mouse_x, mouse_y))
                    elif 'Crustacean' in self.simulation.modes.active_modes \
                                and 'Deleting' not in self.simulation.modes.active_modes:
                        self.simulation.crustacean_list.append(Crustacean(mouse_x, mouse_y))
                    elif 'Fish' in self.simulation.modes.active_modes \
                                and 'Deleting' not in self.simulation.modes.active_modes \
                                    and event.button == 1:
                        FishCreationWindow(self.simulation, mouse_x, mouse_y)
                    
                    elif 'Deleting' in self.simulation.modes.active_modes:
                        if 'Fish' in self.simulation.modes.active_modes:
                            for fish in self.simulation.fish_population:
                                dist_sq = (fish.x - mouse_x) ** 2 + (fish.y - mouse_y) ** 2
                                threshold_sq = (fish.size + 5) ** 2
                                if dist_sq < threshold_sq:
                                    self.simulation.fish_population.remove(fish)
                                    break
                        
                        elif 'Plankton' in self.simulation.modes.active_modes:
                            for plankton in self.simulation.plankton_list:
                                dist_sq = (plankton.x - mouse_x) ** 2 + (plankton.y - mouse_y) ** 2
                                threshold_sq = 4
                                if dist_sq < threshold_sq:
                                    self.simulation.plankton_list.remove(plankton)
                                    break
                        
                        elif 'Crustacean' in self.simulation.modes.active_modes:
                            for crustacean in self.simulation.crustacean_list:
                                dist_sq = (crustacean.x - mouse_x) ** 2 + (crustacean.y - mouse_y) ** 2
                                threshold_sq = 9
                                if dist_sq < threshold_sq:
                                    self.simulation.crustacean_list.remove(crustacean)
                                    break

                else:
                    if event.button != 1:
                        break

                    for fish in self.simulation.fish_population:
                        dist_sq = (fish.x - mouse_x) ** 2 + (fish.y - mouse_y) ** 2
                        threshold_sq = (fish.size + 5) ** 2
                        if dist_sq < threshold_sq:
                            FishDetailsWindow(self.simulation, fish)
                            break
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.simulation.paused = not self.simulation.paused

                elif event.key == pygame.K_v or event.unicode.lower() == "м":
                    self.simulation.modes.toggle_mode('show_vision', "Vision")

                elif event.key == pygame.K_q or event.unicode.lower() == "й":
                    self.simulation.plot.show()

                elif event.key == pygame.K_w or event.unicode.lower() == "ц":
                    self.simulation.show_stats = not self.simulation.show_stats

                elif event.key == pygame.K_e or event.unicode.lower() == "у":
                    self.simulation.show_fps = not self.simulation.show_fps
                
                elif event.key == pygame.K_a or event.unicode.lower() == "ф":
                    self.simulation.modes.toggle_mode('show_current', "Current")

                elif event.key == pygame.K_s or event.unicode.lower() == "і":
                    self.simulation.modes.toggle_mode('creative', "Creative")
                
                if "Creative" in self.simulation.modes.active_modes:
                    if event.key == pygame.K_z or event.unicode.lower() == "я":
                        self.simulation.modes.toggle_mode('cre_plankton', "Plankton")

                    elif event.key == pygame.K_x or event.unicode.lower() == "ч":
                        self.simulation.modes.toggle_mode('cre_crustacean', "Crustacean")
                    
                    elif event.key == pygame.K_c or event.unicode.lower() == "с":
                        self.simulation.modes.toggle_mode('cre_fish', "Fish")
                    
                    elif event.key == pygame.K_d or event.unicode.lower() == "в":
                        self.simulation.modes.toggle_mode('cre_del', "Deleting")

                else:
                    if event.key == pygame.K_z or event.unicode.lower() == "я":
                        self.simulation.modes.toggle_mode('show_oxygen_map', "Oxy Map")
                    
                    elif event.key == pygame.K_x or event.unicode.lower() == "ч":
                        self.simulation.modes.toggle_mode('show_temp_map', "Temp Map")
                    
                    elif event.key == pygame.K_c or event.unicode.lower() == "с":
                        self.simulation.modes.toggle_mode('show_targets', "Targets")