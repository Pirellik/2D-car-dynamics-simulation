import pygame
from pygame.math import Vector2
from car_drawer import CarDrawer
from car_model import Car
from track import *
import pandas as pd
from input_providers import *
from car_data_display import CarDataDisplay
from shapely.geometry import Point, Polygon, LineString
from shapely.affinity import rotate
from tqdm import tqdm
from tabu_search import Search, PointSolution
from simulator import Simulator
from game import Game


if __name__ == '__main__':
    game = Game(1366, 768)
    game.run_pid_controller()
    #game.run()
    sim = Simulator('track3.svg')
    solution = pd.read_csv('solution.csv', index_col=0)
    solution2 = pd.read_csv('solution2.csv', index_col=0)
    times = []
    for ind in tqdm(range(5)):
        if ind < 2:
            times.append(sim.run(0.05, solution))
        else:
            times.append(sim.run(0.05, solution2))
    for time in times:
        print(time)
