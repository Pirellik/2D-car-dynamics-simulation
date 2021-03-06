from input_providers import *
from tqdm import tqdm
from tabu_search import Search, PointSolution
from simulator import Simulator
from game import Game


if __name__ == '__main__':
    game = Game(1366, 768)
    game.run_pid_controller('track6.svg', 'solution3.csv', 0.05)
    #game.run()
    sim = Simulator('track6.svg')
    solution = pd.read_csv('solutionOpt.csv', index_col=0)
    print(sim.run(0.05, solution))

