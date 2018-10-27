from shapely.geometry.polygon import Polygon
from shapely.affinity import rotate
import pygame


class CarDrawer:
    def __init__(self, length=50, width=20):
        self.length = length
        self.width = width

    def draw(self, screen, position, angle, steering):
        pos_x, pos_y = position
        car = Polygon([(pos_x - self.length / 2, pos_y - self.width / 2), (pos_x - self.length / 2, pos_y + self.width / 2),
                         (pos_x + self.length / 2, pos_y + self.width / 2), (pos_x + self.length / 2, pos_y - self.width / 2)])
        front_axle = Polygon(
            [(pos_x + self.length * 3 / 10, pos_y + self.width * 5 / 6), (pos_x + self.length * 3 / 10, pos_y - self.width * 5 / 6),
             (pos_x + self.length * 3 / 10, pos_y + self.width * 5 / 6)])
        front_tire_1 = Polygon(
            [(pos_x + self.length * 1.5 / 10, pos_y + self.width * 5 / 6), (pos_x + self.length * 1.5 / 10, pos_y + self.width),
             (pos_x + 4.5 / 10 * self.length, pos_y + self.width), (pos_x + 4.5 / 10 * self.length, pos_y + self.width * 5 / 6)])
        front_tire_2 = Polygon(
            [(pos_x + self.length * 1.5 / 10, pos_y - self.width * 5 / 6), (pos_x + self.length * 1.5 / 10, pos_y - self.width),
             (pos_x + 4.5 / 10 * self.length, pos_y - self.width), (pos_x + 4.5 / 10 * self.length, pos_y - self.width * 5 / 6)])
        rear_axle = Polygon(
            [(pos_x - self.length * 3 / 10, pos_y + self.width * 5 / 6), (pos_x - self.length * 3 / 10, pos_y - self.width * 5 / 6),
             (pos_x - self.length * 3 / 10, pos_y + self.width * 5 / 6)])
        rear_tire_1 = Polygon(
            [(pos_x - self.length * 1.5 / 10, pos_y + self.width * 5 / 6), (pos_x - self.length * 1.5 / 10, pos_y + self.width),
             (pos_x - 4.5 / 10 * self.length, pos_y + self.width), (pos_x - 4.5 / 10 * self.length, pos_y + self.width * 5 / 6)])
        rear_tire_2 = Polygon(
            [(pos_x - self.length * 1.5 / 10, pos_y - self.width * 5 / 6), (pos_x - self.length * 1.5 / 10, pos_y - self.width),
             (pos_x - 4.5 / 10 * self.length, pos_y - self.width), (pos_x - 4.5 / 10 * self.length, pos_y - self.width * 5 / 6)])
        rear_center = (pos_x - self.length * 3 / 10, pos_y)

        car = rotate(car, angle, rear_center)
        x, y = car.exterior.xy
        pygame.draw.polygon(screen, (0, 255, 0), [(xx, yy) for xx, yy in zip(x, y)], 2)
        front_axle = rotate(front_axle, angle, rear_center)
        x_axle, y_axle = front_axle.exterior.xy
        pygame.draw.polygon(screen, (0, 255, 0), [(xx, yy) for xx, yy in zip(x_axle, y_axle)], 2)
        front_tire_1 = rotate(front_tire_1, angle, rear_center)
        front_tire_1 = rotate(front_tire_1, - steering, (x_axle[0], y_axle[0]))
        x, y = front_tire_1.exterior.xy
        pygame.draw.polygon(screen, (0, 255, 0), [(xx, yy) for xx, yy in zip(x, y)], 2)
        front_tire_2 = rotate(front_tire_2, angle, rear_center)
        front_tire_2 = rotate(front_tire_2, - steering, (x_axle[1], y_axle[1]))
        x, y = front_tire_2.exterior.xy
        pygame.draw.polygon(screen, (0, 255, 0), [(xx, yy) for xx, yy in zip(x, y)], 2)
        rear_axle = rotate(rear_axle, angle, rear_center)
        x, y = rear_axle.exterior.xy
        pygame.draw.polygon(screen, (0, 255, 0), [(xx, yy) for xx, yy in zip(x, y)], 2)
        rear_tire_1 = rotate(rear_tire_1, angle, rear_center)
        x, y = rear_tire_1.exterior.xy
        pygame.draw.polygon(screen, (0, 255, 0), [(xx, yy) for xx, yy in zip(x, y)], 2)
        rear_tire_2 = rotate(rear_tire_2, angle, rear_center)
        x, y = rear_tire_2.exterior.xy
        pygame.draw.polygon(screen, (0, 255, 0), [(xx, yy) for xx, yy in zip(x, y)], 2)
        rect = pygame.Rect(rear_center[0], rear_center[1], 5, 5)
        pygame.draw.rect(screen, (255, 0, 0), rect)
