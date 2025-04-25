import cProfile
import pygame

from core.profiling import profile
from core.settings import HEIGHT, PROFILING, WIDTH
from core.simulation import Simulation

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fish Simulation")
clock = pygame.time.Clock()

def main():
    sim.start_generation()
    if PROFILING:
        cProfile.run('sim.run()', 'profile_output')
        profile() # You can also run the profiling.py file separately to profile the last startup in profiling mode
    else:
        sim.run()
    pygame.quit()

if __name__ == "__main__":
    sim = Simulation(screen, clock)
    main()