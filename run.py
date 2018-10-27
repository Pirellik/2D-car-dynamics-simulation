import pygame
from math import copysign
from car_drawer import CarDrawer
from car_model import Car


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Car tutorial")
        width = 1920
        height = 1080
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.ticks = 60
        self.exit = False

    def run(self):
        car = Car(0, 0)
        car_drawer = CarDrawer()
        ppu = 32

        joysticks = []
        for i in range(pygame.joystick.get_count()):
            joysticks.append(pygame.joystick.Joystick(i))
            joysticks[-1].init()
            print("Detected pad:", joysticks[-1].get_name())

        while not self.exit:
            dt = self.clock.get_time() / 1000

            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            # User input
            throttle = - joysticks[-1].get_axis(3)
            steering = - joysticks[-1].get_axis(4) * 30

            # Logic
            car.get_driver_input(throttle, 1, steering)
            car.update(dt)

            # Drawing
            self.screen.fill((255, 255, 255))
            car_drawer.draw(self.screen, car.position * 10, -car.angle, car.steering)
            pygame.display.flip()
            self.clock.tick(self.ticks)
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
