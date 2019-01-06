import numpy as np
from operator import itemgetter
import bisect
import matplotlib.pyplot as plt
from simulator import Simulator
from input_providers import *
from tqdm import tqdm
from math import floor, e

class Search:
    def __init__(self, init_solution, track):
        self.solution = init_solution # podajemy rozwiązanie początkowe

        self.candidates_list = [] #lista sąsiedztwa z której wybieramy następne rozwiązanie
        #postać: (rozwiązanie PointSolution, pozycja_w_rozwiązaniu, czas_przejazdu)
        # postać gauss: (rozwiązanie PointSolution, pozycja_w_rozwiązaniu, czas_przejazdu, ktory element zostal zmieniony)
        self.tabu_list = [] #lista zabronień
        #postać: (rozwiązanie PointSolution, pozycja_w_rozwiązaniu, ilość_iteracji)

        #wartosci kroku parametrów
        self.dP = 0.05
        self.dI = 0.05
        self.dD = 0.05
        self.dthrottle = 0.1
        self.dgear = 1
        self.dbrakes = 0.1

        #ograniczenia na parametry
        self.maxP = 5
        self.minP = 0

        self.maxI = 1
        self.minI = 0

        self.maxD = 20
        self.minD = 0

        self.maxthrottle = 2
        self.minthrottle = 0

        self.maxbrakes = 1
        self.minbrakes = 0

        self.maxgear = 6
        self.mingear = 0 #wsteczny nie potrzebny

        self.stop_num_of_iterations = 5 # warunek stopu liczba iteracji
        self.stop_time_change = 100 # warunek stopu - poprawa czasu o _ sek
        self.stop_best_time = -110 # warunek stopu - jesli czasu będzie poniżej wartości

        # symulator do pobierania czasów przejazdu
        self.sim = Simulator(track)

        self.first_time = self.simulate(self.solution) #czas dla rozwiązania początkowego
        self.current_time = self.first_time #przechowywany aktualny czas (można zmienić na tablice żeby zapisywać jak sie zmienialy czasy)
        self.best_time = self.first_time

        self.num_of_iterations_tabu = 10 #ile iteracji ma zostac na liscie tabu

        self.f0, self.ax0 = plt.subplots(1)
        self.f1, self.ax1 = plt.subplots(1)
        self.f2, self.ax2 = plt.subplots(1)
        self.f3, self.ax3 = plt.subplots(1)

        self.ax0.set_xlim(0, self.stop_num_of_iterations)
        self.ax0.set_ylim(0, 10)
        self.ax0.set_title("Current Time")
        self.liTime, = self.ax0.plot([], [])

        self.ax1.set_xlim(0, self.stop_num_of_iterations)
        self.ax1.set_ylim(0, 10)
        self.ax1.set_title("Candidates Times")
        self.liCandiTime, = self.ax1.plot([], [])

        self.ax2.set_xlim(0, self.stop_num_of_iterations)
        self.ax2.set_ylim(0, 100)
        self.ax2.set_title("Tabu size")
        self.liTabuSize, = self.ax2.plot([], [])

        self.ax3.set_xlim(0, self.stop_num_of_iterations)
        self.ax3.set_ylim(0, 10)
        self.ax3.set_title("Tabu usage")
        self.liTabuUsage, = self.ax3.plot([], [])

        self.plot_times = []
        self.plot_tabu_used = []
        self.plot_tabu_size = []
        self.plot_candidates_times_min = []
        self.plot_candidates_times_max = []
        self.plot_candidates_times_mean = []

        self.use_gaussian = False
        self.solutionSize = len(self.solution.values)

        self.changes = [self.dP, self.dI, self.dD, self.dthrottle, self.dgear, self.dbrakes]
        self.maxVals = [self.maxP, self.maxI, self.maxD, self.maxthrottle, self.maxgear, self.maxbrakes]
        self.minVals = [self.minP, self.minI, self.minD, self.minthrottle, self.mingear, self.minbrakes]

        self.aspiration_time = 0.1


    def search(self):
        # najpierw generujemy początkową listę sąsiedztwa
        if(self.use_gaussian):
            self.generate_candidates_gaussian()
        else:
            self.generate_candidates()

        # póżniej tylko aktualizujemy
        iterations = 0
        time_change = 0
        while iterations < self.stop_num_of_iterations and time_change < self.stop_time_change and self.current_time > self.stop_best_time: #warunki stopu
            self.iterate()
            time_change = self.first_time - self.current_time
            iterations += 1
            if self.current_time < self.best_time:
                self.best_time = self.current_time
                self.solution.to_csv("solutionOpt.csv")

            self.plot_times.append(self.current_time)
            self.plot_tabu_size.append(len(self.tabu_list))
            self.plot_candidates_times_min.append(self.candidates_list[0][2])
            self.plot_candidates_times_max.append(self.candidates_list[len(self.candidates_list) - 1][2])
            self.plot_candidates_times_mean.append(np.mean([x[2] for x in self.candidates_list]))


            self.liTime.set_xdata(np.arange(iterations))
            self.liTabuSize.set_xdata(np.arange(iterations))
            self.liTabuUsage.set_xdata(np.arange(iterations))

            self.liTime.set_ydata(self.plot_times)
            self.liTabuSize.set_ydata(self.plot_tabu_size)
            self.liTabuUsage.set_ydata(self.plot_tabu_used)

            print(self.current_time)
            plt.pause(0.01)

        self.ax1.plot(np.arange(iterations), self.plot_candidates_times_min)
        self.ax1.plot(np.arange(iterations), self.plot_candidates_times_max)
        self.ax1.plot(np.arange(iterations), self.plot_candidates_times_mean)
        plt.pause(6000)

    def iterate(self):
        on_tabu_list = True
        i = 0

        while on_tabu_list:
            best_change = self.candidates_list[i]
            on_tabu_list = self.check_tabu_list(best_change[0], best_change[1])
            #kryterium aspiracji
            if self.current_time - best_change[2] > self.aspiration_time:
                on_tabu_list = False
                print("Uzyte kryterium aspiracji. Poprawa czasu: ", self.current_time - best_change[2])
            i += 1

        self.plot_tabu_used.append(i-1)
        self.add_to_tabu(PointSolution(self.solution.values[best_change[1]].copy()), best_change[1])


        if(self.use_gaussian):
            self.modify_gaussian(best_change[0].to_list(), best_change[1], best_change[3])
            self.update_candidates_gaussian(best_change[1])
        else:
            self.solution.iloc[best_change[1]] = best_change[0].to_list()
            self.update_candidates(best_change[1])
        #self.current_time = self.simulate(self.solution)
        self.current_time = best_change[2]
        self.update_tabu()




    def simulate(self, solution):
        return self.sim.run(0.05, solution)

    def generate_candidates(self):
        for i in tqdm(range(0, len(self.solution.values)-1)):

            #zmieniane po jednej wartosci - mniej przypadkow i zmiana 2 mozna rozbic na 2 zmiany po jednej zmiennej
            #zmieniac nie tylko o dt - teraz strasznie wolno zmierza
            init_value = self.solution.values[i].copy()
            x = self.solution.values[i].copy()

            parameters = x.copy()
            changes = [self.dP, self.dI, self.dD, self.dthrottle, self.dgear, self.dbrakes]
            maxVals = [self.maxP, self.maxI, self.maxD, self.maxthrottle, self.maxgear, self.maxbrakes]
            minVals = [self.minP, self.minI, self.minD, self.minthrottle, self.mingear, self.minbrakes]

            for j in range(0, 5):
                if parameters[j] + changes[j] < maxVals[j]:
                    parameters[j] += changes[j]
                self.solution.iloc[i] = parameters.copy()
                t = self.simulate(self.solution)
                self.candidates_list.append([PointSolution(parameters), i, t])

                parameters = x.copy()

                if parameters[j] - changes[j] > minVals[j]:
                    parameters[j] -= changes[j]
                self.solution.iloc[i] = parameters.copy()
                t = self.simulate(self.solution)
                self.candidates_list.append([PointSolution(parameters), i, t])

                parameters = x.copy()

            self.solution.iloc[i] = init_value.copy()

        self.candidates_list.sort(key=itemgetter(2))



    def update_candidates(self, i): #i - gdzie zmiana wystapila
        init_value = self.solution.values[i].copy()
        x = self.solution.values[i].copy()

        parameters = x.copy()
        changes = [self.dP, self.dI, self.dD, self.dthrottle, self.dgear, self.dbrakes]
        maxVals = [self.maxP, self.maxI, self.maxD, self.maxthrottle, self.maxgear, self.maxbrakes]
        minVals = [self.minP, self.minI, self.minD, self.minthrottle, self.mingear, self.minbrakes]

        #aktualizacja czasow - trzeba bo jak sie zmienia rozwiazanie to sie wszystko zmienia
        for j in tqdm(range(len(self.candidates_list))):
            index = self.candidates_list[j][1]
            x = self.solution.values[index].copy()
            self.solution.iloc[index] = self.candidates_list[j][0].to_list()
            self.candidates_list[j][2] = self.simulate(self.solution)
            self.solution.iloc[index] = x.copy()


        for j in range(0, 5):
            if parameters[j] + changes[j] < maxVals[j]:
                parameters[j] += changes[j]
            self.solution.iloc[i] = parameters.copy()
            t = self.simulate(self.solution)  # ZAMIENIC NA DOBRA SYMULACJE
            self.candidates_list.append([PointSolution(parameters), i, t]) #DODAWANIE DO POSORTOWANEJ LISTY

            parameters = x.copy()

            if parameters[j] - changes[j] > minVals[j]:
                parameters[j] -= changes[j]
            self.solution.iloc[i] = parameters.copy()
            t = self.simulate(self.solution)
            self.candidates_list.append([PointSolution(parameters), i, t])

            parameters = x.copy()
        self.solution.iloc[i] = init_value.copy()
        self.candidates_list.sort(key=itemgetter(2))

    def generate_candidates_gaussian(self):
        for i in tqdm(range(0, len(self.solution.values)-1)):

            #zmieniane po jednej wartosci - mniej przypadkow i zmiana 2 mozna rozbic na 2 zmiany po jednej zmiennej
            #zmieniac nie tylko o dt - teraz strasznie wolno zmierza
            parameters = [0, 0, 0, 0, 0, 0, 0]

            for j in range(0, 5):
                parameters[j] = self.changes[j]
                self.modify_gaussian(parameters, i, j)
                t = self.simulate(self.solution)
                self.candidates_list.append([PointSolution(parameters), i, t, j])
                self.modify_gaussian((-1)*parameters, i, j)

                parameters[j] = -self.changes[j]
                self.modify_gaussian(parameters, i, j)
                t = self.simulate(self.solution)
                self.candidates_list.append([PointSolution(parameters), i, t, j])
                self.modify_gaussian((-1)*parameters, i, j)

                parameters = [0, 0, 0, 0, 0, 0, 0]

        self.candidates_list.sort(key=itemgetter(2))



    def update_candidates_gaussian(self, i): #i - gdzie zmiana wystapila

        #aktualizacja czasow - trzeba bo jak sie zmienia rozwiazanie to sie wszystko zmienia
        for j in tqdm(range(len(self.candidates_list))):
            index = self.candidates_list[j][1]
            self.modify_gaussian(self.candidates_list[j][0].to_list(), index, self.candidates_list[j][3])
            self.candidates_list[j][2] = self.simulate(self.solution)
            self.modify_gaussian((-1)*self.candidates_list[j][0].to_list(), index, self.candidates_list[j][3])

        self.candidates_list.sort(key=itemgetter(2))

    def modify_gaussian(self, parameters, position, changePosition):
        factors = generate_list_of_factors(7)
        if len(parameters) == 0:
            return
        for i in range(-3, 3):
            newPosition = i + position
            if newPosition < 0 or newPosition >= self.solutionSize:
                continue
            newParameters = parameters.copy()
            if(changePosition != 4):
                newParameters[changePosition] *= factors[i+3]
            solutionSum = self.solution.iloc[newPosition][changePosition] + newParameters[changePosition]
            if solutionSum > self.maxVals[changePosition]:
                self.solution.iloc[newPosition, changePosition] = self.maxVals[changePosition]
            elif solutionSum < self.minVals[changePosition]:
                self.solution.iloc[newPosition, changePosition] = self.minVals[changePosition]
            else:
                self.solution.iloc[newPosition, changePosition] = solutionSum

    def update_tabu(self):
        for i in range(0, len(self.tabu_list)-2): #dla -1 czasem przekracza - jedno rozwiązanie puste jest
            self.tabu_list[i][2] += 1
            if self.tabu_list[i][2] > self.num_of_iterations_tabu:
                del(self.tabu_list[i])



    def add_to_tabu(self, value, position):
        self.tabu_list.append([value, position, 1])

    def check_tabu_list(self, value, position):
        for x in self.tabu_list:
            if x[1] == position:
                if x[0] == value:
                    return True
        return False




class PointSolution:
    def __init__(self, list):
        self.P = list[0]
        self.I = list[1]
        self.D = list[2]
        self.throttle = list[3] #gaz
        self.gear = list[4] #bieg
        self.brakes = list[5] #hamulec
        self.deformation = list[6] #deformacja

    def __eq__(self, solution):
        if self.P != solution.P:
            return False
        if self.I != solution.I:
            return False
        if self.D != solution.D:
            return False
        if self.throttle != solution.throttle:
            return False
        if self.gear != solution.gear:
            return False
        if self.brakes != solution.brakes:
            return False
        if self.deformation != solution.deformation:
            return False
        return True

    def __str__(self):
        return str(self.to_list())

    def to_list(self):
        return [self.P, self.I, self.D, self.throttle, self.gear, self.brakes, self.deformation]


def generate_list_of_factors(size):
    deviation = (size - 1) / 4
    list_of_factors = []
    for index in range(size):
        list_of_factors.append(e**(- (index - floor(size / 2)) ** 2 / (2 * deviation ** 2)))
    return list_of_factors


if __name__ == '__main__':
    #plt.plot(list(range(21)), generate_list_of_factors(21))
    #plt.show()
    #solution1 = [PointSolution([1,0,0,0.3,0,0,0.5]) for i in range(100)]
    solution1 = pd.read_csv('solution3.csv', index_col=0)
    tabu1 = Search(solution1, 'track6.svg')
    tabu1.search()
    #plt.pause(5)
