import numpy as np
from operator import itemgetter
import bisect
import matplotlib.pyplot as plt

#TO DO wstawianie do posortowanej listy

class Search:
    def __init__(self, init_solution):
        self.solution = init_solution # podajemy rozwiązanie początkowe

        self.candidates_list = [] #lista sąsiedztwa z której wybieramy następne rozwiązanie
        #postać: (rozwiązanie, pozycja_w_rozwiązaniu, czas_przejazdu)
        self.tabu_list = [] #lista zabronień
        #postać: (rozwiązanie, pozycja_w_rozwiązaniu, ilość_iteracji)

        #wartosci kroku parametrów
        self.dP = 0.05
        self.dI = 0.05
        self.dD = 0.05
        self.dg = 0.1
        self.dh = 0.1
        self.db = 1

        #ograniczenia na parametry
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

        self.stop_num_of_iterations = 100 # warunek stopu liczba iteracji
        self.stop_time_change = 100 # warunek stopu - poprawa czasu o _ sek
        self.stop_best_time = -110 # warunek stopu - jesli czasu będzie poniżej wartości

        self.first_time = self.simulate(self.solution) #czas dla rozwiązania początkowego
        self.current_time = self.first_time #przechowywany aktualny czas (można zmienić na tablice żeby zapisywać jak sie zmienialy czasy)

        self.num_of_iterations_tabu = 200 #ile iteracji ma zostac na liscie tabu

        self.f, self.ax = plt.subplots(1)

        self.ax.set_xlim(0, 160)
        self.ax.set_ylim(-100, 0)
        self.ax.set_title("Time")
        self.li, = self.ax.plot([], [])

        self.times = []




    def search(self):
        # najpierw generujemy początkową listę sąsiedztwa
        self.generate_candidates()
        print([[x[1], x[2]] for x in self.candidates_list])
        # póżniej tylko aktualizujemy
        iterations = 0
        time_change = 0
        while iterations < self.stop_num_of_iterations and time_change < self.stop_time_change and self.current_time > self.stop_best_time: #warunki stopu
            self.iterate()
            time_change = self.first_time - self.current_time
            iterations += 1
            #print(self.current_time)
            self.times.append(self.current_time)
            self.li.set_xdata(np.arange(iterations))
            self.li.set_ydata(self.times)
            plt.pause(0.01)
            #print([x.g for x in self.solution])
            #print([x[0] for x in self.tabu_list])


    def iterate(self):
        on_tabu_list = True
        i = 0
        while on_tabu_list:
            best_change = self.candidates_list[i]
            on_tabu_list = self.check_tabu_list(best_change[0], best_change[1])
            i += 1

        #print(best_change[0])
        #print([[x[1], x[2]] for x in self.candidates_list])
        self.add_to_tabu(self.solution[best_change[1]], best_change[1])
        self.solution[best_change[1]] = best_change[0]
        self.current_time = self.simulate(self.solution)
        self.update_candidates(best_change[1])
        self.update_tabu()




    def simulate(self, solution):
        return -sum([x.g for x in solution])

    def generate_candidates(self):
        for i in range(0, len(self.solution)-1):

            #zmieniane po jednej wartosci - mniej przypadkow i zmiana 2 mozna rozbic na 2 zmiany po jednej zmiennej
            init_value = self.solution[i]
            x = self.solution[i]

            parameters = x.to_list()
            changes = [self.dP, self.dI, self.dD, self.dg, self.dh, self.db]
            maxVals = [self.maxP, self.maxI, self.maxD, self.maxg, self.maxh, self.maxb]
            minVals = [self.minP, self.minI, self.minD, self.ming, self.minh, self.minb]

            for j in range(0, 5):
                if parameters[j] + changes[j] < maxVals[j]:
                    parameters[j] += changes[j]
                self.solution[i] = PointSolution(parameters)
                t = self.simulate(self.solution) # ZAMIENIC NA DOBRA SYMULACJE
                self.candidates_list.append([PointSolution(parameters), i, t])

                parameters = x.to_list()

                if parameters[j] - changes[j] > minVals[j]:
                    parameters[j] -= changes[j]
                self.solution[i] = PointSolution(parameters)
                t = self.simulate(self.solution)
                self.candidates_list.append([PointSolution(parameters), i, t])

                parameters = x.to_list()

            self.solution[i] = init_value

        self.candidates_list.sort(key=itemgetter(2))



    def update_candidates(self, i): #i - gdzie zmiana wystapila
        init_value = self.solution[i]
        x = self.solution[i]

        parameters = x.to_list()
        changes = [self.dP, self.dI, self.dD, self.dg, self.dh, self.db]
        maxVals = [self.maxP, self.maxI, self.maxD, self.maxg, self.maxh, self.maxb]
        minVals = [self.minP, self.minI, self.minD, self.ming, self.minh, self.minb]

        #aktualizacja czasow
        for j in range(len(self.candidates_list)):
            index = self.candidates_list[j][1]
            x = self.solution[index]
            self.solution[index] = self.candidates_list[j][0]
            self.candidates_list[j][2] = self.simulate(self.solution)
            self.solution[index] = x


        for j in range(0, 5):
            if parameters[j] + changes[j] < maxVals[j]:
                parameters[j] += changes[j]
            self.solution[i] = PointSolution(parameters)
            t = self.simulate(self.solution)  # ZAMIENIC NA DOBRA SYMULACJE
            self.candidates_list.append([PointSolution(parameters), i, t]) #DODAWANIE DO POSORTOWANEJ LISTY

            parameters = x.to_list()

            if parameters[j] - changes[j] > minVals[j]:
                parameters[j] -= changes[j]
            self.solution[i] = PointSolution(parameters)
            t = self.simulate(self.solution)
            self.candidates_list.append([PointSolution(parameters), i, t])

            parameters = x.to_list()

        self.solution[i] = init_value
        self.candidates_list.sort(key=itemgetter(2))

    def update_tabu(self):
        for i in range(0, len(self.tabu_list)-2): #dla -1 czasem przekracza
            #print(i, len(self.tabu_list)-1)
            self.tabu_list[i][2] += 1
            if self.tabu_list[i][2] > self.num_of_iterations_tabu:
                del(self.tabu_list[i])



    def add_to_tabu(self, value, position):
        self.tabu_list.append([value, position, 1])

    def check_tabu_list(self, value, position):
        #TO DO dodać kryterium aspiracji - wziąć pod uwagę jak poprawia i można też ile iteracji już jest na liście
        #poprawic porownywanie
        for x in self.tabu_list:
            if x[1] == position:
                if x[0] == value:
                    #print(x[0], value)
                    return True
        return False

class PointSolution:
    def __init__(self, list):
        self.P = list[0]
        self.I = list[1]
        self.D = list[2]
        self.g = list[3] #gaz
        self.h = list[4] #hamulec
        self.b = list[5] #bieg

    def __eq__(self, solution):
        if self.P != solution.P:
            return False
        if self.I != solution.I:
            return False
        if self.D != solution.D:
            return False
        if self.g != solution.g:
            return False
        if self.h != solution.h:
            return False
        if self.b != solution.b:
            return False
        return True

    def __str__(self):
        return str(self.to_list())

    def to_list(self):
        return [self.P, self.I, self.D, self.g, self.h, self.b]


if __name__ == '__main__':
    solution1 = [PointSolution([1,0,0,0.3,0,0]) for i in range(100)]
    tabu1 = Search(solution1)
    tabu1.search()
