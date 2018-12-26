from shapely.geometry.polygon import Polygon
from shapely.affinity import rotate
import pygame


class CarDrawer:
    def __init__(self, length=50, width=20, init_position=(1366/2, 768/2)):
        self.length = length
        self.width = width
        self.trace = []
        self.init_position = init_position
        pos_x = self.init_position[0]
        pos_y = self.init_position[1]
        self.car_model = Polygon([(pos_x - self.length / 2 + self.length * 3 / 10, pos_y - self.width / 2), (pos_x - self.length / 2 + self.length * 3 / 10, pos_y + self.width / 2),
                         (pos_x + self.length / 2 + self.length * 3 / 10, pos_y + self.width / 2), (pos_x + self.length / 2 + self.length * 3 / 10, pos_y - self.width / 2)])

    def draw(self, screen, car):
        car_color = (181, 25, 253)
        pos_x, pos_y = 1366 / 2, 768 / 2
        angle = -car.angle
        steering = car.steering
        if len(self.trace) >= 1000:
            self.trace.pop(0)
        if not self.trace:
            self.trace.append((10 * car.position.x + 1366/2, 10 * car.position.y + 768/2))
            self.trace.append((10 * car.position.x + 1366 / 2, 10 * car.position.y + 768 / 2))
        else:
            self.trace.append((10 * car.position.x + 1366 / 2, 10 * car.position.y + 768 / 2))

        front_axle = Polygon(
            [(pos_x + self.length * 3 / 10 + self.length * 3 / 10, pos_y + self.width * 5 / 6), (pos_x + self.length * 3 / 10 + self.length * 3 / 10, pos_y - self.width * 5 / 6),
             (pos_x + self.length * 3 / 10 + self.length * 3 / 10, pos_y + self.width * 5 / 6)])
        front_tire_1 = Polygon(
            [(pos_x + self.length * 1.5 / 10 + self.length * 3 / 10, pos_y + self.width * 5 / 6), (pos_x + self.length * 1.5 / 10 + self.length * 3 / 10, pos_y + self.width),
             (pos_x + 4.5 / 10 * self.length + self.length * 3 / 10, pos_y + self.width), (pos_x + 4.5 / 10 * self.length + self.length * 3 / 10, pos_y + self.width * 5 / 6)])
        front_tire_2 = Polygon(
            [(pos_x + self.length * 1.5 / 10 + self.length * 3 / 10, pos_y - self.width * 5 / 6), (pos_x + self.length * 1.5 / 10 + self.length * 3 / 10, pos_y - self.width),
             (pos_x + 4.5 / 10 * self.length + self.length * 3 / 10, pos_y - self.width), (pos_x + 4.5 / 10 * self.length + self.length * 3 / 10, pos_y - self.width * 5 / 6)])
        rear_axle = Polygon(
            [(pos_x - self.length * 3 / 10 + self.length * 3 / 10, pos_y + self.width * 5 / 6), (pos_x - self.length * 3 / 10 + self.length * 3 / 10, pos_y - self.width * 5 / 6),
             (pos_x - self.length * 3 / 10 + self.length * 3 / 10, pos_y + self.width * 5 / 6)])
        rear_tire_1 = Polygon(
            [(pos_x - self.length * 1.5 / 10 + self.length * 3 / 10, pos_y + self.width * 5 / 6), (pos_x - self.length * 1.5 / 10 + self.length * 3 / 10, pos_y + self.width),
             (pos_x - 4.5 / 10 * self.length + self.length * 3 / 10, pos_y + self.width), (pos_x - 4.5 / 10 * self.length + self.length * 3 / 10, pos_y + self.width * 5 / 6)])
        rear_tire_2 = Polygon(
            [(pos_x - self.length * 1.5 / 10 + self.length * 3 / 10, pos_y - self.width * 5 / 6), (pos_x - self.length * 1.5 / 10 + self.length * 3 / 10, pos_y - self.width),
             (pos_x - 4.5 / 10 * self.length + self.length * 3 / 10, pos_y - self.width), (pos_x - 4.5 / 10 * self.length + self.length * 3 / 10, pos_y - self.width * 5 / 6)])
        rear_center = (pos_x, pos_y)

        #pygame.draw.lines(screen, (0, 0, 255), False, [(x - car.position.x * 10, y - car.position.y * 10) for x, y in self.trace], 2)
        car_model = rotate(self.car_model, angle, rear_center)
        x, y = car_model.exterior.xy
        pygame.draw.polygon(screen, car_color, [(xx, yy) for xx, yy in zip(x, y)], 2)
        front_axle = rotate(front_axle, angle, rear_center)
        x_axle, y_axle = front_axle.exterior.xy

        front_center = ((x_axle[0] + x_axle[1]) / 2, (y_axle[0] + y_axle[1]) / 2)
        #print(front_center)
        car.front_center = front_center

        pygame.draw.polygon(screen, car_color, [(xx, yy) for xx, yy in zip(x_axle, y_axle)], 2)
        front_tire_1 = rotate(front_tire_1, angle, rear_center)
        front_tire_1 = rotate(front_tire_1, - steering, (x_axle[0], y_axle[0]))
        x, y = front_tire_1.exterior.xy
        pygame.draw.polygon(screen, car_color, [(xx, yy) for xx, yy in zip(x, y)], 2)
        front_tire_2 = rotate(front_tire_2, angle, rear_center)
        front_tire_2 = rotate(front_tire_2, - steering, (x_axle[1], y_axle[1]))
        x, y = front_tire_2.exterior.xy
        pygame.draw.polygon(screen, car_color, [(xx, yy) for xx, yy in zip(x, y)], 2)
        rear_axle = rotate(rear_axle, angle, rear_center)
        x, y = rear_axle.exterior.xy
        pygame.draw.polygon(screen, car_color, [(xx, yy) for xx, yy in zip(x, y)], 2)
        rear_tire_1 = rotate(rear_tire_1, angle, rear_center)
        x, y = rear_tire_1.exterior.xy
        pygame.draw.polygon(screen, car_color, [(xx, yy) for xx, yy in zip(x, y)], 2)
        rear_tire_2 = rotate(rear_tire_2, angle, rear_center)
        x, y = rear_tire_2.exterior.xy
        pygame.draw.polygon(screen, car_color, [(xx, yy) for xx, yy in zip(x, y)], 2)
        rect = pygame.Rect(rear_center[0], rear_center[1], 5, 5)
        pygame.draw.rect(screen, (255, 0, 0), rect)
        rect = pygame.Rect(front_center[0], front_center[1], 5, 5)
        pygame.draw.rect(screen, (255, 0, 0), rect)
