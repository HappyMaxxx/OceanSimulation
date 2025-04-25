import math
import random
import noise

from core.settings import MAX_TEMP, MIN_TEMP


class CurrentGrid:
    def __init__(self, simulation, width, height, grid_size, layers=3):
        self.simulation = simulation
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.cols = width // grid_size + 1
        self.rows = height // grid_size + 1
        self.layers = layers
        self.grid = {}
        
        self.base_strengths = self.generate_base_strengths()
        self.target_base_strengths = self.base_strengths.copy()
        self.base_directions = self.generate_base_directions()
        self.target_base_directions = self.base_directions.copy()
        self.layer_boundaries = self.generate_layer_boundaries()
        self.target_layer_boundaries = [boundary[:] for boundary in self.layer_boundaries]
        
        self.base_layer_boundaries = self.generate_layer_boundaries()  # лише один раз
        self.target_layer_boundaries = [b[:] for b in self.base_layer_boundaries]
        self.layer_boundaries = [b[:] for b in self.base_layer_boundaries]

        self.initialize_grid()

    def generate_base_strengths(self):
        max_strength = 0.5
        min_strength = 0.1
        strengths = []
        for layer in range(self.layers):
            t = layer / (self.layers - 1) if self.layers > 1 else 0
            strength = max_strength - (max_strength - min_strength) * t
            strengths.append(strength)
        return strengths

    def generate_base_directions(self):
        directions = []
        min_angle = -math.pi / 2
        max_angle = math.pi / 2
        for layer in range(self.layers):
            t = layer / (self.layers - 1) if self.layers > 1 else 0
            angle = min_angle + (max_angle - min_angle) * t
            directions.append(angle)
        return directions

    def generate_layer_boundaries(self):
        boundaries = []
        for layer in range(self.layers + 1):
            boundary = []
            base_height = self.height * layer / self.layers
            current_y = base_height
            for col in range(self.cols):
                boundary.append(current_y)
                current_y += random.uniform(-self.height * 0.01, self.height * 0.01)
                current_y = max(0, min(self.height, current_y))
            
            segment_length = random.randint(self.cols // 10, self.cols // 5)
            for col in range(1, self.cols):
                if col % segment_length == 0 or col == self.cols - 1:
                    delta_y = random.uniform(-self.height * 0.1, self.height * 0.1)
                    target_y = base_height + delta_y
                    target_y = max(0, min(self.height, target_y))
                    start_col = max(0, col - segment_length)
                    for i in range(start_col, col + 1):
                        t = (i - start_col) / (col - start_col) if col != start_col else 1
                        t_smooth = t * t * (3 - 2 * t)
                        boundary[i] = (1 - t_smooth) * boundary[start_col] + t_smooth * target_y
                    segment_length = random.randint(self.cols // 10, self.cols // 5)
            
            smoothed_boundary = boundary.copy()
            for col in range(1, self.cols - 1):
                smoothed_boundary[col] = (boundary[col - 1] + boundary[col] + boundary[col + 1]) / 3
            smoothed_boundary[0] = boundary[0]
            smoothed_boundary[-1] = boundary[-1]
            boundaries.append(smoothed_boundary)
        
        for col in range(self.cols):
            for layer in range(1, self.layers):
                if boundaries[layer][col] > boundaries[layer + 1][col]:
                    boundaries[layer][col], boundaries[layer + 1][col] = boundaries[layer + 1][col], boundaries[layer][col]
        
        return boundaries

    def get_layer_at(self, x, y):
        col = int(x // self.grid_size)
        if col >= self.cols:
            col = self.cols - 1
        for layer in range(self.layers):
            if y <= self.layer_boundaries[layer + 1][col]:
                return layer
        return self.layers - 1

    def initialize_grid(self):
        for row in range(self.rows):
            y = row * self.grid_size
            for col in range(self.cols):
                x = col * self.grid_size
                layer = self.get_layer_at(x, y)
                base_direction = self.base_directions[layer] + random.uniform(-math.pi/4, math.pi/4)
                strength = self.base_strengths[layer] * (1 + random.uniform(-0.15, 0.15))
                self.grid[(col, row)] = {"strength": strength, "direction": base_direction}

    def update(self, simulation):
        season = simulation.seasons[simulation.current_season_index]
        season_modifier = {"Spring": 0.8, "Summer": 1.0, "Autumn": 0.9, "Winter": 0.7}[season]
        self.update_targets(season)
        for i in range(self.layers):
            self.base_strengths[i] += (self.target_base_strengths[i] - self.base_strengths[i]) * 0.01
            angle_diff = (self.target_base_directions[i] - self.base_directions[i] + math.pi) % (2 * math.pi) - math.pi
            self.base_directions[i] = (self.base_directions[i] + angle_diff * 0.05) % (2 * math.pi)
        for layer in range(self.layers + 1):
            for col in range(self.cols):
                self.layer_boundaries[layer][col] += (self.target_layer_boundaries[layer][col] - self.layer_boundaries[layer][col]) * 0.005
        for row in range(self.rows):
            y = row * self.grid_size
            for col in range(self.cols):
                x = col * self.grid_size
                layer = self.get_layer_at(x, y)
                current = self.grid[(col, row)]
                temp = simulation.get_temperature(x, y)
                temp_factor = (temp - MIN_TEMP) / (MAX_TEMP - MIN_TEMP)
                target_direction = (self.base_directions[layer] +
                                math.sin(simulation.time * 0.01 + col * 0.1) * math.pi/8 +
                                random.uniform(-math.pi/8, math.pi/8))
                target_strength = self.base_strengths[layer] * season_modifier * (1 + temp_factor * 0.3) * (1 + random.uniform(-0.1, 0.1))
                nearby_segments = simulation.get_nearby_segments(x, y)
                for seg_x, seg_y, _ in nearby_segments:
                    distance = math.hypot(seg_x - x, seg_y - y)
                    if distance < self.grid_size * 2:
                        current["strength"] *= (1 - 0.3 * (1 - distance / (self.grid_size * 2)))
                current["strength"] += (target_strength - current["strength"]) * 0.02
                angle_diff = (target_direction - current["direction"] + math.pi) % (2 * math.pi) - math.pi
                current["direction"] += angle_diff * 0.05

    def update_targets(self, season):
        season_effects = {
            "Spring": {"strength": 0.4, "direction_shift": -math.pi/6, "boundary_shift": -self.height * 0.05},
            "Summer": {"strength": 0.5, "direction_shift": 0.0, "boundary_shift": 0.0},
            "Autumn": {"strength": 0.45, "direction_shift": math.pi/6, "boundary_shift": self.height * 0.03},
            "Winter": {"strength": 0.35, "direction_shift": -math.pi/4, "boundary_shift": -self.height * 0.07}
        }
        
        effect = season_effects[season]
        
        for layer in range(self.layers):
            t = layer / (self.layers - 1) if self.layers > 1 else 0
            strength_noise = noise.pnoise1(self.simulation.time * 0.005 + layer, octaves=4) * 0.2
            direction_noise = noise.pnoise1(self.simulation.time * 0.01 + layer + 10, octaves=4) * math.pi / 4
            
            self.target_base_strengths[layer] = effect["strength"] * (1 - t * 0.3) + strength_noise
            self.target_base_directions[layer] = (self.generate_base_directions()[layer] + 
                                                effect["direction_shift"] + direction_noise) % (2 * math.pi)
        
        for layer in range(self.layers + 1):
            for col in range(self.cols):
                base_height = self.base_layer_boundaries[layer][col] + effect["boundary_shift"]
                noise_value = noise.pnoise2(col * 0.1, self.simulation.time * 0.02 + layer, octaves=4) * self.height * 0.2
                target = max(0, min(self.height, base_height + noise_value))
                self.target_layer_boundaries[layer][col] += (target - self.target_layer_boundaries[layer][col]) * 0.02
        
        min_gap = self.height * 0.02
        for col in range(self.cols):
            for layer in range(1, self.layers):
                below = self.target_layer_boundaries[layer + 1][col]
                above = self.target_layer_boundaries[layer][col]
                if above > below - min_gap:
                    mid = (above + below) / 2
                    self.target_layer_boundaries[layer][col] = mid - min_gap / 2
                    self.target_layer_boundaries[layer + 1][col] = mid + min_gap / 2

    def get_current_at(self, x, y):
        col = int(x // self.grid_size)
        row = int(y // self.grid_size)
        if (col, row) in self.grid:
            return self.grid[(col, row)]["strength"], self.grid[(col, row)]["direction"]
        return 0.3, 0.0