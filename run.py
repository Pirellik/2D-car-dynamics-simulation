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


class Game:
    def __init__(self, width, height):
        pygame.init()
        pygame.display.set_caption("Car model")
        self.window_width = width
        self.window_height = height
        self.screen = pygame.display.set_mode((width, height))
        self.fps = 20

        self.clock = pygame.time.Clock()
        self.ticks = 60
        self.exit = False

    def run(self):

        car = Car(self.window_width / 20, self.window_height / 20)
        track = Track('track3.svg')
        track_drawer = TrackDrawer(track)
        car.position.x, car.position.y = track.path[0][0] / 10 - 1366 / 20, track.path[0][1] / 10 - 768 / 20
        car_drawer = CarDrawer()
        input_provider = JoystickInputProvider()
        if not input_provider.joysticks:
            input_provider = KeyboardInputProvider()
        car_data_display = CarDataDisplay(car)
        trace = [(car.position.x * 10 + 1366/2, car.position.y * 10 + 768/2) for _ in range(3)]

        while not self.exit:
            dt = self.clock.tick(self.fps) / 1000

            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            trace.pop(2)
            trace.insert(0, (car.position.x * 10 + 1366/2, car.position.y * 10 + 768/2))

            # User input
            car_input = input_provider.get_input()
            car.get_driver_input(car_input[0], car_input[1], car_input[2], car_input[3])
            car.update(dt)

            # Drawing
            self.screen.fill((0, 0, 0))
            track_drawer.draw(self.screen, car.position * 10, trace)
            car_drawer.draw(self.screen, car)
            car_data_display.display_data(self.screen)
            pygame.display.flip()
        pygame.quit()

    def run_pid_controller(self):
        car = Car(self.window_width / 20, self.window_height / 20)
        track = Track('track3.svg')
        track_drawer = TrackDrawer(track)
        solution = pd.read_csv('solution.csv', index_col=0)
        track.apply_deformations(list(solution.Deformation))
        car.position.x, car.position.y = track.path[0][0] / 10 - 1366 / 20, track.path[0][1] / 10 - 768 / 20
        car_drawer = CarDrawer()
        car_data_display = CarDataDisplay(car)
        input_provider = AutonomousDriver(solution)
        time = 0
        trace = [(car.position.x * 10 + 1366/2, car.position.y * 10 + 768/2) for _ in range(3)]

        while not self.exit:
            dt = self.clock.tick(self.fps) / 1000
            time += dt
            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            vector = Vector2(40, 0).rotate(-car.angle)
            vector = np.array((vector.x + 1366 / 2, vector.y + 768 / 2))
            front_center = Point(np.array((car.position.x * 10, car.position.y * 10)) + vector)
            if Polygon(track.path).contains(front_center):
                input_provider.line_error = - LineString(track.path).distance(front_center)
            else:
                input_provider.line_error = LineString(track.path).distance(front_center)

            trace.pop(2)
            trace.insert(0, (car.position.x * 10 + 1366 / 2, car.position.y * 10 + 768 / 2))

            # User input

            input_provider.index = 0
            for chunk in track.track_chunks:
                if chunk.is_active:
                    input_provider.index = track.track_chunks.index(chunk)

            car_input = input_provider.get_input()
            car.get_driver_input(car_input[0], car_input[1], car_input[2], car_input[3])
            car.update(dt)

            # Drawing
            self.screen.fill((0, 0, 0))
            track_drawer.draw(self.screen, car.position * 10, trace)
            car_drawer.draw(self.screen, car)
            car_data_display.display_data(self.screen)
            rect = pygame.Rect(front_center.x - car.position.x * 10, front_center.y - car.position.y * 10, 5, 5)
            pygame.draw.rect(self.screen, (0, 0, 255), rect)
            pygame.display.flip()

            if input_provider.index == len(track.track_chunks) - 1:
                break

        finished = True
        for chunk in track.track_chunks:
            if not chunk.is_active:
                finished = False
                print(track.track_chunks.index(chunk))
                break

        print(time, finished)
        pygame.quit()


class Simulator:
    def __init__(self):
        pass

    def run(self, dt):
        car = Car(1366 / 20, 768 / 20)
        solution = pd.read_csv('solution.csv', index_col=0)
        track = Track('track3.svg')
        track.apply_deformations(list(solution.Deformation))
        car.position.x, car.position.y = track.path[0][0] / 10 - 1366 / 20, track.path[0][1] / 10 - 768 / 20
        input_provider = AutonomousDriver(solution)
        time = 0
        trace = [(car.position.x * 10 + 1366 / 2, car.position.y * 10 + 768 / 2) for _ in range(3)]

        while True:
            time += dt

            vector = Vector2(40, 0).rotate(-car.angle)
            vector = np.array((vector.x + 1366 / 2, vector.y + 768 / 2))
            front_center = Point(np.array((car.position.x * 10, car.position.y * 10)) + vector)
            if Polygon(track.path).contains(front_center):
                input_provider.line_error = - LineString(track.path).distance(front_center)
            else:
                input_provider.line_error = LineString(track.path).distance(front_center)

            trace.pop(2)
            trace.insert(0, (car.position.x * 10 + 1366 / 2, car.position.y * 10 + 768 / 2))

            # User input
            indexes = track.check_car_position(trace)
            input_provider.index = 0
            for chunk in track.track_chunks:
                if chunk.is_active:
                    input_provider.index = track.track_chunks.index(chunk)

            car_input = input_provider.get_input()
            car.get_driver_input(car_input[0], car_input[1], car_input[2], car_input[3])
            car.update(dt)

            if input_provider.index == len(track.track_chunks) - 1:
                break

        finished = True
        for chunk in track.track_chunks:
            if not chunk.is_active:
                finished = False
                print(track.track_chunks.index(chunk))
                break

        print(time, finished)
        if finished:
            return time
        else:
            return 99999


if __name__ == '__main__':
    game = Game(1366, 768)
    game.run_pid_controller()
    #game.run()
    sim = Simulator()
    print(sim.run(0.05))
