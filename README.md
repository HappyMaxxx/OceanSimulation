# Fish Simulation

## Overview
Fish Simulation is a Python-based project that models an underwater ecosystem using Pygame. It simulates the behavior and interactions of various aquatic entities such as fish, algae, plankton, crustaceans, and dead algae parts. The simulation incorporates environmental factors like temperature, oxygen levels, water currents, and seasonal changes to create a dynamic and realistic ecosystem. The project includes genetic and epigenetic mechanisms for fish, allowing for evolution and adaptation over time.

## Features
- **Dynamic Ecosystem**: Simulates fish, algae, plankton, crustaceans, and environmental factors like water currents, temperature, and oxygen.
- **Genetic System**: Fish have genomes with traits (e.g., speed, size, vision) that influence their behavior and survival.
- **Epigenetics**: Fish adapt to environmental conditions like food scarcity through epigenetic changes.
- **Seasonal and Day-Night Cycles**: Affects growth, spawning, and environmental conditions.
- **Interactive UI**: Allows users to toggle modes (e.g., vision, temperature maps), pause the simulation, and view detailed fish statistics.
- **Real-Time Plotting**: Displays population, energy, size, food, and algae trends using Matplotlib.
- **Creative Mode**: Enables users to add or remove entities manually.
- **Event Handling**: Supports mouse and keyboard inputs for interaction.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/HappyMaxxx/OceanSimulation fish-simulation
   cd fish-simulation
   ```
2. Create and activate a Python virtual environment:  
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # For Linux and macOS
   # or
   python -m venv venv
   venv\Scripts\activate     # For Windows
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the simulation:
   ```bash
   python main.py
   ```

## Usage
- **Run the Simulation**: Execute `main.py` to start the simulation. The ecosystem initializes with a generation phase, followed by real-time simulation.
- **Controls**:
  - **Space**: Pause/unpause the simulation.
  - **V**: Toggle vision display for fish.
  - **Q**: Open the plot window showing population and other metrics.
  - **W**: Toggle statistics display (e.g., fish count, algae count).
  - **E**: Toggle FPS display.
  - **A**: Toggle water current visualization.
  - **S**: Toggle creative mode.
  - **Z**: Toggle oxygen map (or plankton placement in creative mode).
  - **X**: Toggle temperature map (or crustacean placement in creative mode).
  - **C**: Toggle target lines (or fish placement in creative mode).
  - **D**: Toggle deletion mode in creative mode.
  - **Left Click**: View fish details or place/remove entities in creative mode.
- **Creative Mode**: Activate with `S` to manually add/remove fish, plankton, or crustaceans.
- **Plots**: Press `Q` to view real-time graphs of population, energy, size, food, and algae.

## Project Structure
- 'main.py' – Entry point of the simulation.
- 'core/' – Contains the core simulation logic.
- 'entities/' – Defines ecosystem entities.
- 'ui/' – User interface components.
- 'plots/' – Real-time data visualization.
- 'tests/' – Unit tests for components, program for testing formulas.
- 'requirements.txt' – Python dependencies.
- 'README.md' – Project documentation.
- 'LICENSE' – Project license file.

## Key Classes
- **Simulation**: Manages the overall simulation, including time, seasons, and entity updates.
- **Fish**: Represents fish with genetic traits, behaviors (e.g., eating, mating), and epigenetics.
- **Algae**: Simulates algae growth and decay, contributing to oxygen levels.
- **Plankton/Crustacean**: Food sources with lifecycles and movement.
- **Egg**: Represents fish eggs with incubation and survival mechanics.
- **CurrentGrid**: Models layered water currents with seasonal variations.
- **Plot**: Generates real-time graphs using Matplotlib.
- **UI/EventHandler**: Handles user interface and input events.
- **FishDetailsWindow**: Displays detailed fish statistics in a Tkinter window.

## Configuration
Simulation parameters (e.g., screen dimensions, initial populations, genetic mutation rates) are defined in `settings.py`. Adjust these to modify the simulation's behavior.

## Notes
- The simulation uses a grid-based system for efficient collision detection and environmental calculations.
- Performance can be monitored with FPS display (`E`) or profiled using `cProfile` (enable `PROFILING` in `core/settings.py`).
- The project is designed for educational and experimental purposes, showcasing ecological and evolutionary concepts.

## Requirements
- Python 3.8+
- Pygame
- Matplotlib
- NumPy
- Noise
- Tkinter (included with standard Python)

Install dependencies using:
```bash
pip install pygame matplotlib numpy pynoise
```

## Contributing
Contributions are welcome! Please fork the repository, create a new branch, and submit a pull request with your changes. Ensure code follows PEP 8 style guidelines.

## License
This project is licensed under the Apache 2.0 License. See the `LICENSE` file for details.

## Acknowledgments
- Built with Pygame for rendering and event handling.
- Uses Matplotlib for plotting and Tkinter for GUI elements.
- Incorporates the `noise` library for natural-looking environmental variations.