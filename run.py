import pygame
from car_drawer import CarDrawer
from car_model import Car
from road import Road
import pandas as pd
from input_providers import RecordedInputProvider, JoystickInputProvider, KeyboardInputProvider
from car_data_display import CarDataDisplay


class Game:
    def __init__(self, width, height):
        pygame.init()
        pygame.display.set_caption("Car model")
        self.window_width = width
        self.window_height = height
        self.screen = pygame.display.set_mode((width, height))
        self.fps = 100

        self.clock = pygame.time.Clock()
        self.ticks = 60
        self.exit = False

    def record(self):
        car = Car(self.window_width / 20, self.window_height / 20)
        car_drawer = CarDrawer()
        input_provider = JoystickInputProvider()
        if not input_provider.joysticks:
            input_provider = KeyboardInputProvider()
        road = Road(car, 'track2.svg')
        car_data_display = CarDataDisplay(car)
        recorded_inputs = pd.DataFrame(columns=['Throttle', 'Brakes', 'Steering', 'Gear'])

        while not self.exit:
            dt = self.clock.tick(self.fps) / 1000

            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            # User input
            throttle, gear, brakes, steering = input_provider.get_input()
            car.get_driver_input(throttle, gear, brakes, steering)
            car.update(dt)

            # Recording
            recorded_inputs = recorded_inputs.append({'Throttle': throttle,
                                                      'Brakes': brakes,
                                                      'Steering': steering,
                                                      'Gear': gear}, ignore_index=True)
            # Drawing
            self.screen.fill((255, 255, 255))
            road.draw(self.screen)
            car_drawer.draw(self.screen, car)
            car_data_display.display_data(self.screen)
            pygame.display.flip()

        pygame.quit()
        return recorded_inputs

    def play_recorded(self, recording_path):
        car = Car(self.window_width / 20, self.window_height / 20)
        car_drawer = CarDrawer()
        input_provider = RecordedInputProvider(recording_path)
        road = Road(car, 'track2.svg')
        car_data_display = CarDataDisplay(car)

        while not self.exit:
            dt = self.clock.tick(self.fps) / 1000

            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            # User input
            car_input = input_provider.get_input()
            if car_input is None: break
            car.get_driver_input(car_input[0], car_input[1], car_input[2], car_input[3])
            car.update(dt)

            # Drawing
            self.screen.fill((255, 255, 255))
            road.draw(self.screen)
            car_drawer.draw(self.screen, car)
            car_data_display.display_data(self.screen)
            pygame.display.flip()

        pygame.quit()

    def run(self):
        car = Car(self.window_width / 20, self.window_height / 20)
        car_drawer = CarDrawer()
        input_provider = JoystickInputProvider()
        if not input_provider.joysticks:
            input_provider = KeyboardInputProvider()
        road = Road(car, 'track2.svg')
        car_data_display = CarDataDisplay(car)

        while not self.exit:
            dt = self.clock.tick(self.fps) / 1000

            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            # User input
            car_input = input_provider.get_input()
            car.get_driver_input(car_input[0], car_input[1], car_input[2], car_input[3])
            car.update(dt)

            # Drawing
            self.screen.fill((255, 255, 255))
            road.draw(self.screen)
            car_drawer.draw(self.screen, car)
            car_data_display.display_data(self.screen)
            pygame.display.flip()
        pygame.quit()


if __name__ == '__main__':
    game = Game(1366, 768)
    #game.record().to_csv("run.csv")
    #game.play_recorded('run.csv')
    game.run()
