import numpy as np

class Search:
    def __init__(self, init_solution):
        self.solution = init_solution

        self.candidate_list #lista sąsiedztwa z której wybieramy następne rozwiązanie
        self.tabu_list #lista zabronień

        self.dP = 0.05
        self.dI = 0.05
        self.dD = 0.05
        self.dg = 0.1
        self.dh = 0.1
        self.db = 1

        self.maxP = 5
        self.minP = 0

        self.maxI = 1
        self.minI = 0

        self.maxD = 1
        self.minD = 0

        self.maxg = 1
        self.ming = 0

        self.maxh = 1
        self.minh = 0

        self.maxb = 6
        self.minb = -1


    def generate_candidates(self):
        for i in range(0, self.solution.size()):
            init_value = self.solution[i]
            x = self.solution[i]
            if x.P + self.dP < self.maxP:
                x.P += self.dP
    def update_candidates(self):

    def check_tabu_list(self, change, position):





class PointSolution:
    def __init__(self, P, I, D, g, h, b):
        self.P = P
        self.I = I
        self.D = D
        self.g = g #gaz
        self.h = h #hamulec
        self.b = b #bieg