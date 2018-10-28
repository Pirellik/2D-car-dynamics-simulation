import pygame
from math import copysign
from car_drawer import CarDrawer
from car_model import Car
from pygame.math import Vector2
import xml.etree.ElementTree as ET

CIRCLE_TAG_NAME = '{http://www.w3.org/2000/svg}circle'

def circleToPoint(circle):
    const = 5
    return (float(circle.attrib['cx'])*const, float(circle.attrib['cy'])*const)

def readSVGFile(SVGFileName):
    return ET.parse(SVGFileName)

def getAllPoints(tree, style):
    circles = []
    for circle in tree.iter(CIRCLE_TAG_NAME):
        if circle.attrib['style'] == style:
            circles.append(circleToPoint(circle))

    return circles
    #return [circleToPoint(circle)
    #        for circle in tree.iter(CIRCLE_TAG_NAME)]

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Car tutorial")
        width = 640
        height = 480
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.ticks = 60
        self.exit = False
        tree = readSVGFile('./track2.svg')

        styleRed = "fill:#000000;stroke:none"
        self.trackPointsRight = getAllPoints(tree, styleRed)
        styleBlack = "fill:#ff0000;stroke:none"
        self.trackPointsLeft = getAllPoints(tree, styleBlack)
        print(self.trackPointsRight)
        print(self.trackPointsLeft)

    def run(self):
        car = Car(0, 0)
        car_drawer = CarDrawer()
        ppu = 32

        #joysticks = []
        #for i in range(pygame.joystick.get_count()):
        #    joysticks.append(pygame.joystick.Joystick(i))
        #    joysticks[-1].init()
        #    print("Detected pad:", joysticks[-1].get_name())

        while not self.exit:
            dt = self.clock.get_time() / 1000

            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            # User input
            throttle = 0
            steering = 0
            brakes = 0

            if pygame.key.get_pressed()[pygame.K_UP]:
                throttle = 5
            else:
                throttle = 0

            if pygame.key.get_pressed()[pygame.K_DOWN]:
                brakes = 5000
            else:
                brakes = 0

            if pygame.key.get_pressed()[pygame.K_LEFT]:
                steering = 20

            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                steering = -20

            #throttle = - joysticks[-1].get_axis(3)
            #steering = - joysticks[-1].get_axis(4) * 30

            # Logic
            car.get_driver_input(throttle, 1, steering, brakes)
            car.update(dt)

            # Drawing
            self.screen.fill((255, 255, 255))
            pos = car.position * 10
            #if pos.x < 10:
            #    pos.x = 10
            #elif pos.x > 620:
            #    pos.x = 620

            #if pos.y < 10:
            #    pos.y = 10
            #elif pos.y > 470:
            #    pos.y = 470

            pos.x = pos.x % 640
            pos.y = pos.y % 480

            car_drawer.draw(self.screen, pos, -car.angle, car.steering)
            pygame.draw.polygon(self.screen, (0, 255, 0), (self.trackPointsLeft), 2)
            pygame.draw.polygon(self.screen, (255, 255, 0), (self.trackPointsRight), 2)
            pygame.display.flip()
            self.clock.tick(self.ticks)
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
