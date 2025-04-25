import random
import tkinter as tk
from threading import Thread
from typing import TYPE_CHECKING

from entities.fish import Fish
from core.settings import (
    DEGISTION_EFECT,
    HEIGHT,
    MAX_ENERGY,
    METABOLISM_EFECT,
    REPRODUCTION_EFECT,
    SIZE_EFECT,
    VISION_REDUCTION_IN_ALGAE,
)

if TYPE_CHECKING:
    from core.simulation import Simulation


class FishDetailsWindow:
    def __init__(self, simulation: 'Simulation', fish: 'Fish') -> None:
        def open_window():
            self.simulation = simulation
            self.fish = fish
            self.simulation.paused = True
            self.window = tk.Tk()

            self.window.title("Fish Details")
            self.window.geometry("670x570")
            self.window.configure(bg='#242424')

            left_frame = tk.Frame(self.window, bg='#242424')
            left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

            tk.Label(left_frame, 
                    text=f"Energy: {int(self.fish.energy)}/{self.fish.max_energy:.1f}",
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

            if self.fish.is_in_algae():
                tk.Label(left_frame, 
                        text="In Algae",
                        font=("Arial", 12), bg='#242424', fg='#5E9F61'
                ).pack(pady=5)

            if not self.fish.is_male:
                tk.Label(left_frame,
                        text=f"Repro Strategy: {'Egg-laying' if self.fish.is_egglayer else 'Live-bearing'}",
                        font=("Arial", 12), bg='#242424', fg='#5E9F61'
                ).pack(pady=5)

            if self.fish.is_pregnant:
                tk.Label(left_frame, 
                        text=f"Pregnant ({self.fish.pregnancy_timer}/{self.fish.pregnancy_duration})",
                        font=("Arial", 12), bg='#242424', fg='#5E9F61'
                ).pack(pady=5)
            
            if self.fish.after_birth_period > 0:
                tk.Label(left_frame, 
                        text=f"After birth period: {self.fish.after_birth_period}",
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
            if trait == 'reproduction_strategy':
                trait = 'reprod_strat'

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


class FishCreationWindow:
    def __init__(self, simulation: 'Simulation', x: int, y: int) -> None:
        def open_window():
            self.simulation = simulation
            self.x = x
            self.y = y
            self.simulation.paused = True
            self.window = tk.Tk()
            self.window.title("Create Fish")
            self.window.geometry("1000x500")
            self.window.configure(bg='#242424')

            self.entries = {}
            self.genome_entries = {}

            content_frame = tk.Frame(self.window, bg='#242424')
            content_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            genome_frame = tk.Frame(content_frame, bg='#242424')
            genome_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)

            tk.Label(genome_frame, text="Genome Alleles (0.0-1.0)", font=("Arial", 12, "bold"), bg='#242424', fg='#5E9F61').grid(row=0, column=0, columnspan=4, pady=5)

            genome_traits = ["speed", "size", "vision", "metabolism", "digestion", "reproduction", "defense", "color", "preferred_depth", "predator", "reproduction_strategy"]
            for i, trait in enumerate(genome_traits):
                tk.Label(genome_frame, text=f"{trait} A1", font=("Arial", 10), bg='#242424', fg='#5E9F61').grid(row=i+1, column=0, sticky="w", pady=2)
                entry1 = tk.Entry(genome_frame, font=("Arial", 10), bg='#333333', fg='#5E9F61', insertbackground='#5E9F61')
                entry1.insert(0, "0.5")
                entry1.grid(row=i+1, column=1, padx=5, pady=2)
                tk.Label(genome_frame, text=f"{trait} A2", font=("Arial", 10), bg='#242424', fg='#5E9F61').grid(row=i+1, column=2, sticky="w", pady=2)
                entry2 = tk.Entry(genome_frame, font=("Arial", 10), bg='#333333', fg='#5E9F61', insertbackground='#5E9F61')
                entry2.insert(0, "0.5")
                entry2.grid(row=i+1, column=3, padx=5, pady=2)
                self.genome_entries[trait] = (entry1, entry2)

            main_frame = tk.Frame(content_frame, bg='#242424')
            main_frame.pack(side=tk.RIGHT, padx=10, fill=tk.Y)

            attributes = [
                ("Energy", 50.0, 0.0, 100.0),
                ("Max Age", 100.0, 10.0, 200.0),
                ("Max Size", 5.0, 1.0, 15.0),
                ("Speed", 2.0, 0.5, 5.0),
                ("Vision", 50.0, 10.0, 100.0),
                ("Metabolism", 0.5, 0.1, 1.0),
                ("Digestion", 0.5, 0.1, 1.0),
                ("Reproduction Rate", 0.5, 0.1, 1.0),
                ("Defense", 0.5, 0.1, 1.0),
                ("Preferred Depth", HEIGHT/2, 0.0, HEIGHT),
                ("Predator (0-1)", 0.5, 0.0, 1.0)
            ]

            for i, (label, default, min_val, max_val) in enumerate(attributes):
                tk.Label(main_frame, text=label, font=("Arial", 10), bg='#242424',
                         fg='#5E9F61').grid(row=i, column=0, sticky="w", pady=2)
                entry = tk.Entry(main_frame, font=("Arial", 10), bg='#333333',
                                 fg='#5E9F61', insertbackground='#5E9F61')
                entry.insert(0, str(default))
                entry.grid(row=i, column=1, padx=5, pady=2)
                self.entries[label] = (entry, min_val, max_val)

            tk.Label(main_frame, text="Gender", font=("Arial", 10), bg='#242424',
                     fg='#5E9F61').grid(row=len(attributes), column=0, sticky="w", pady=2)
            self.gender_var = tk.StringVar(value="Male")
            tk.Radiobutton(main_frame, text="Male", variable=self.gender_var, value="Male",
                           bg='#242424', fg='#5E9F61', selectcolor='#333333').grid(row=len(attributes), column=1, sticky="w")
            tk.Radiobutton(main_frame, text="Female", variable=self.gender_var, value="Female",
                           bg='#242424', fg='#5E9F61', selectcolor='#333333').grid(row=len(attributes), column=1, sticky="e")

            tk.Label(main_frame, text="Reproduction Strategy", font=("Arial", 10), bg='#242424',
                     fg='#5E9F61').grid(row=len(attributes)+1, column=0, sticky="w", pady=2)
            self.repro_var = tk.StringVar(value="egglayer")
            tk.Radiobutton(main_frame, text="Egg", variable=self.repro_var, value="egglayer",
                           bg='#242424', fg='#5E9F61', selectcolor='#333333').grid(row=len(attributes)+1, column=1, sticky="w")
            tk.Radiobutton(main_frame, text="Live", variable=self.repro_var, value="livebearer",
                           bg='#242424', fg='#5E9F61', selectcolor='#333333').grid(row=len(attributes)+1, column=1, sticky="e")

            button_frame = tk.Frame(self.window, bg='#242424')
            button_frame.pack(pady=10)
            tk.Button(button_frame, text="Create", font=("Arial", 12), bg='#333333',
                      fg='#5E9F61', command=self.create_fish).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="Random", font=("Arial", 12), bg='#333333',
                      fg='#5E9F61', command=self.randomize).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="Cancel", font=("Arial", 12), bg='#333333',
                      fg='#5E9F61', command=self.close_window).pack(side=tk.LEFT, padx=5)

            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.mainloop()

        Thread(target=open_window).start()

    def validate_float(self, value, min_val, max_val):
        try:
            val = float(value)
            return max(min_val, min(max_val, val))
        except ValueError:
            return min_val

    def validate_genome_float(self, value):
        try:
            val = float(value)
            return max(0.0, min(1.0, val))
        except ValueError:
            return 0.5

    def randomize(self):
        for label, (entry, min_val, max_val) in self.entries.items():
            entry.delete(0, tk.END)
            if label == "Predator (0-1)":
                entry.insert(0, str(round(random.uniform(0.0, 1.0), 2)))
            else:
                entry.insert(0, str(round(random.uniform(min_val, max_val), 2)))
        
        self.gender_var.set(random.choice(["Male", "Female"]))
        self.repro_var.set(random.choice(["egglayer", "livebearer"]))

        for trait, (entry1, entry2) in self.genome_entries.items():
            entry1.delete(0, tk.END)
            entry2.delete(0, tk.END)
            entry1.insert(0, str(round(random.uniform(0.0, 1.0), 2)))
            entry2.insert(0, str(round(random.uniform(0.0, 1.0), 2)))

    def create_fish(self):
        genome = {}
        for trait, (entry1, entry2) in self.genome_entries.items():
            allele1 = self.validate_genome_float(entry1.get())
            allele2 = self.validate_genome_float(entry2.get())
            genome[trait] = {
                "alleles": [allele1, allele2],
                "dominance": random.choice([0, 1])
            }

        energy = self.validate_float(self.entries["Energy"][0].get(), 0.0, 100.0)
        fish = Fish(
            x=self.x,
            y=self.y,
            simulation=self.simulation,
            energy=energy,
            genome=genome
        )
        
        # Override calculated traits with user inputs
        fish.max_age = self.validate_float(self.entries["Max Age"][0].get(), 10.0, 200.0)
        fish.max_size = self.validate_float(self.entries["Max Size"][0].get(), 1.0, 15.0)
        fish.speed = self.validate_float(self.entries["Speed"][0].get(), 0.5, 5.0)
        fish.vision = self.validate_float(self.entries["Vision"][0].get(), 10.0, 100.0)
        fish.metabolism = self.validate_float(self.entries["Metabolism"][0].get(), 0.1, 1.0)
        fish.digestion = self.validate_float(self.entries["Digestion"][0].get(), 0.1, 1.0)
        fish.reproduction_rate = self.validate_float(self.entries["Reproduction Rate"][0].get(), 0.1, 1.0)
        fish.defense = self.validate_float(self.entries["Defense"][0].get(), 0.1, 1.0)
        fish.preferred_depth = self.validate_float(self.entries["Preferred Depth"][0].get(), 0.0, HEIGHT)
        fish.is_predator = self.validate_float(self.entries["Predator (0-1)"][0].get(), 0.0, 1.0) > 0.5
        fish.is_male = self.gender_var.get() == "Male"
        fish.reproduction_strategy = self.repro_var.get()

        # Recalculate dependent attributes
        fish.max_energy = (MAX_ENERGY * (
            SIZE_EFECT * fish.max_size +
            DEGISTION_EFECT * fish.digestion +
            REPRODUCTION_EFECT * fish.reproduction_rate
        ) / (1 + METABOLISM_EFECT * fish.metabolism)) / 3
        fish.energy = min(energy, fish.max_energy)
        fish.color = (
            max(0, min(255, int(genome["color"]["alleles"][0] *(100 if fish.is_predator else 255) * fish.color_modifier))),
            max(0, min(255, int((100 + fish.size * 10) * (0.5 if fish.is_predator else 1) * fish.color_modifier))),
            max(0, min(255, int(genome["color"]["alleles"][1] * (100 if fish.is_predator else 255) * fish.color_modifier)))
        )
        fish.vision_sq_o = fish.vision ** 2
        fish.vision_sq_a = fish.vision ** 2 * VISION_REDUCTION_IN_ALGAE ** 2

        self.simulation.fish_population.append(fish)
        self.close_window()

    def close_window(self) -> None:
        self.simulation.paused = False
        self.window.destroy()