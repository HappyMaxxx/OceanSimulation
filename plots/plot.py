import tkinter as tk
from threading import Thread
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

if TYPE_CHECKING:
    from core.simulation import Simulation

class Plot:
    def __init__(self, simulation: 'Simulation') -> None:
        self.simulation = simulation
        self.fish_info = [] 
        self.energy_info = [] 
        self.size_info = []  
        self.food_info = []
        self.algae_info = []
        self.global_time = 0
        self.window = None
        self.canvas = None
        self.figure = None
        self.current_plot_type = "population"

    def update(self):
        fishes_population = len([f for f in self.simulation.fish_population if not f.is_dead])
        predators = len([f for f in self.simulation.fish_population if f.is_predator and not f.is_dead])
        prey = len([f for f in self.simulation.fish_population if not f.is_predator and not f.is_dead])

        predator_fish = [f for f in self.simulation.fish_population if f.is_predator and not f.is_dead]
        prey_fish = [f for f in self.simulation.fish_population if not f.is_predator and not f.is_dead]
        avg_energy_predators = sum(f.energy for f in predator_fish) / len(predator_fish) if predator_fish else 0
        avg_energy_prey = sum(f.energy for f in prey_fish) / len(prey_fish) if prey_fish else 0

        avg_size_predators = sum(f.size for f in predator_fish) / len(predator_fish) if predator_fish else 0
        avg_size_prey = sum(f.size for f in prey_fish) / len(prey_fish) if prey_fish else 0
        algaes_parts = sum(len(a.segments) for a in self.simulation.algae_list)
        planktons = len(self.simulation.plankton_list)
        crustaceans = len(self.simulation.crustacean_list)
        dead_parts = len(self.simulation.dead_algae_parts)

        self.fish_info.append((self.global_time, fishes_population, predators, prey))
        self.energy_info.append((self.global_time, avg_energy_predators, avg_energy_prey))
        self.size_info.append((self.global_time, avg_size_predators, avg_size_prey))
        self.food_info.append((self.global_time, planktons, crustaceans, dead_parts))
        self.algae_info.append((self.global_time, algaes_parts))
        self.global_time += 1

        if self.window is not None:
            self.update_plot()

    def create_window(self):
        def open_window():
            self.simulation.paused = True
            self.window = tk.Tk()
            self.window.title("Simulation Graphs")
            self.window.geometry("800x600")
            self.window.configure(bg='#242424')

            left_frame = tk.Frame(self.window, bg='#242424')
            left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

            right_frame = tk.Frame(self.window, bg='#242424', width=150)
            right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

            tk.Button(right_frame, text="Population", font=("Arial", 12), bg='#333333',
                      fg='#5E9F61', highlightbackground='#424242',
                      command=lambda: self.switch_plot("population")).pack(pady=5, fill=tk.X)
            tk.Button(right_frame, text="Energy", font=("Arial", 12), bg='#333333',
                      fg='#5E9F61', highlightbackground='#424242',
                      command=lambda: self.switch_plot("energy")).pack(pady=5, fill=tk.X)
            tk.Button(right_frame, text="Size", font=("Arial", 12), bg='#333333',
                      fg='#5E9F61', highlightbackground='#424242',
                      command=lambda: self.switch_plot("size")).pack(pady=5, fill=tk.X)
            tk.Button(right_frame, text="Food", font=("Arial", 12), bg='#333333',
                      fg='#5E9F61', highlightbackground='#424242',
                      command=lambda: self.switch_plot("food")).pack(pady=5, fill=tk.X)
            tk.Button(right_frame, text="Algae", font=("Arial", 12), bg='#333333',
                      fg='#5E9F61', highlightbackground='#424242',
                      command=lambda: self.switch_plot("algae")).pack(pady=5, fill=tk.X)
                    
            self.figure, self.ax = plt.subplots(figsize=(6, 4))

            bottom_frame = tk.Frame(right_frame, bg='#242424')
            bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

            tk.Button(bottom_frame, text="Close", font=("Arial", 12), bg='#333333',
                      fg='#5E9F61', highlightbackground='#424242',
                      command=self.close_window).pack(fill=tk.X)

            self.canvas = FigureCanvasTkAgg(self.figure, master=left_frame)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            self.update_plot()

            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.mainloop()

        if self.window is None or not self.window.winfo_exists():
            Thread(target=open_window).start()

    def switch_plot(self, plot_type):
        self.current_plot_type = plot_type
        self.update_plot()

    def update_plot(self):
        if self.figure is None or self.ax is None:
            return

        self.ax.clear()

        if self.current_plot_type == "population":
            self.ax.set_title("Fish Population Over Time")
            self.ax.set_xlabel("Time")
            self.ax.set_ylabel("Population")
            max_y = max([info[1] for info in self.fish_info] + [1]) * 1.2
            self.ax.set_ylim(0, max_y)
            self.ax.plot([info[0] for info in self.fish_info],
                            [info[1] for info in self.fish_info], label="Total Fish")
            self.ax.plot([info[0] for info in self.fish_info],
                            [info[2] for info in self.fish_info], label="Predators")
            self.ax.plot([info[0] for info in self.fish_info],
                            [info[3] for info in self.fish_info], label="Prey")
            self.ax.legend()

        elif self.current_plot_type == "energy":
            self.ax.set_title("Average Energy Over Time")
            self.ax.set_xlabel("Time")
            self.ax.set_ylabel("Average Energy")
            max_y = max([max(info[1], info[2]) for info in self.energy_info] + [1]) * 1.2
            self.ax.set_ylim(0, max_y)
            self.ax.plot([info[0] for info in self.energy_info],
                            [info[1] for info in self.energy_info], label="Predators")
            self.ax.plot([info[0] for info in self.energy_info],
                            [info[2] for info in self.energy_info], label="Prey")
            self.ax.legend()

        elif self.current_plot_type == "size":
            self.ax.set_title("Average Size Over Time")
            self.ax.set_xlabel("Time")
            self.ax.set_ylabel("Average Size")
            max_y = max([max(info[1], info[2]) for info in self.size_info] + [1]) * 1.2
            self.ax.set_ylim(0, max_y)
            self.ax.plot([info[0] for info in self.size_info],
                            [info[1] for info in self.size_info], label="Predators")
            self.ax.plot([info[0] for info in self.size_info],
                            [info[2] for info in self.size_info], label="Prey")
            self.ax.legend()

        elif self.current_plot_type == "food":
            self.ax.set_title("Food Over Time")
            self.ax.set_xlabel("Time")
            self.ax.set_ylabel("Food")
            max_y = max([max(info[1], info[2], info[3]) for info in self.food_info] + [1]) * 1.3
            self.ax.set_ylim(0, max_y)
            self.ax.plot([info[0] for info in self.food_info],
                            [info[1] for info in self.food_info], label="Plankton")
            self.ax.plot([info[0] for info in self.food_info],
                            [info[2] for info in self.food_info], label="Crustaceans")
            self.ax.plot([info[0] for info in self.food_info],
                            [info[3] for info in self.food_info], label="Dead Parts")
            self.ax.legend()
        
        elif self.current_plot_type == "algae":
            self.ax.set_title("Algae Parts Over Time")
            self.ax.set_xlabel("Time")
            self.ax.set_ylabel("Algae Parts")
            max_y = max([info[1] for info in self.algae_info] + [1]) * 1.2
            self.ax.set_ylim(0, max_y)
            self.ax.plot([info[0] for info in self.algae_info],
                            [info[1] for info in self.algae_info], label="Algae Parts")
            self.ax.legend()

        self.canvas.draw()

    def close_window(self):
        if self.window is not None:
            self.window.destroy()
            self.window = None
            self.figure = None
            self.ax = None
            self.canvas = None
            self.simulation.paused = False

    def show(self):
        self.create_window()