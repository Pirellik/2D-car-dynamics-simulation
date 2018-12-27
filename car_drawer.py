from shapely.geometry.polygon import Polygon
from shapely.affinity import rotate
import pygame


class CarDrawer:
    def __init__(self, length=55, width=20, init_position=(1366/2, 768/2)):
        self.length = length
        self.width = width
        self.trace = []
        self.init_position = init_position
        pos_x = self.init_position[0]
        pos_y = self.init_position[1]
        self.r_center = (pos_x, pos_y)

        self.car_model = Polygon([(pos_x - self.length * 2 / 10, pos_y - self.width / 2),
                                  (pos_x - self.length * 2 / 10, pos_y + self.width / 2),
                                  (pos_x + self.length * 8 / 10, pos_y + self.width / 2),
                                  (pos_x + self.length * 8 / 10, pos_y - self.width / 2)])

        self.f_axle =    Polygon([(pos_x + self.length * 6 / 10, pos_y + self.width * 5 / 6),
                                  (pos_x + self.length * 6 / 10, pos_y - self.width * 5 / 6),
                                  (pos_x + self.length * 6 / 10, pos_y + self.width * 5 / 6)])
        self.f_tire_1 =  Polygon([(pos_x + self.length * 4.5 / 10, pos_y + self.width * 5 / 6),
                                  (pos_x + self.length * 4.5 / 10, pos_y + self.width * 7 / 6),
                                  (pos_x + 7.5 / 10 * self.length, pos_y + self.width * 7 / 6),
                                  (pos_x + 7.5 / 10 * self.length, pos_y + self.width * 5 / 6)])
        self.f_tire_2 =  Polygon([(pos_x + self.length * 4.5 / 10, pos_y - self.width * 5 / 6),
                                  (pos_x + self.length * 4.5 / 10, pos_y - self.width * 7 / 6),
                                  (pos_x + 7.5 / 10 * self.length, pos_y - self.width * 7 / 6),
                                  (pos_x + 7.5 / 10 * self.length, pos_y - self.width * 5 / 6)])
        self.r_axle =    Polygon([(pos_x, pos_y + self.width * 5 / 6),
                                  (pos_x, pos_y - self.width * 5 / 6),
                                  (pos_x, pos_y + self.width * 5 / 6)])
        self.r_tire_1 =  Polygon([(pos_x + self.length * 1.5 / 10, pos_y + self.width * 5 / 6),
                                  (pos_x + self.length * 1.5 / 10, pos_y + self.width * 7 / 6),
                                  (pos_x - 1.5 / 10 * self.length, pos_y + self.width * 7 / 6),
                                  (pos_x - 1.5 / 10 * self.length, pos_y + self.width * 5 / 6)])
        self.r_tire_2 =  Polygon([(pos_x + self.length * 1.5 / 10, pos_y - self.width * 5 / 6),
                                  (pos_x + self.length * 1.5 / 10, pos_y - self.width * 7 / 6),
                                  (pos_x - 1.5 / 10 * self.length, pos_y - self.width * 7 / 6),
                                  (pos_x - 1.5 / 10 * self.length, pos_y - self.width * 5 / 6)])

    def draw(self, screen, car):
        car_color = (181, 25, 253)
        angle = -car.angle
        steering = car.steering

        car_model = rotate(self.car_model, angle, self.r_center)
        x, y = car_model.exterior.xy
        pygame.draw.polygon(screen, (0, 0, 255), [(xx, yy) for xx, yy in zip(x, y)])
        f_axle = rotate(self.f_axle, angle, self.r_center)
        x_axle, y_axle = f_axle.exterior.xy
        pygame.draw.polygon(screen, car_color, [(xx, yy) for xx, yy in zip(x_axle, y_axle)], 2)
        f_tire_1 = rotate(self.f_tire_1, angle, self.r_center)
        f_tire_1 = rotate(f_tire_1, - steering, (x_axle[0], y_axle[0]))
        x, y = f_tire_1.exterior.xy
        pygame.draw.polygon(screen, (0, 0, 0), [(xx, yy) for xx, yy in zip(x, y)])
        f_tire_2 = rotate(self.f_tire_2, angle, self.r_center)
        f_tire_2 = rotate(f_tire_2, - steering, (x_axle[1], y_axle[1]))
        x, y = f_tire_2.exterior.xy
        pygame.draw.polygon(screen, (0, 0, 0), [(xx, yy) for xx, yy in zip(x, y)])
        r_axle = rotate(self.r_axle, angle, self.r_center)
        x, y = r_axle.exterior.xy
        pygame.draw.polygon(screen, car_color, [(xx, yy) for xx, yy in zip(x, y)], 2)
        r_tire_1 = rotate(self.r_tire_1, angle, self.r_center)
        x, y = r_tire_1.exterior.xy
        pygame.draw.polygon(screen, (0, 0, 0), [(xx, yy) for xx, yy in zip(x, y)])
        r_tire_2 = rotate(self.r_tire_2, angle, self.r_center)
        x, y = r_tire_2.exterior.xy
        pygame.draw.polygon(screen, (0, 0, 0), [(xx, yy) for xx, yy in zip(x, y)])
        rect = pygame.Rect(self.r_center[0], self.r_center[1], 5, 5)
        pygame.draw.rect(screen, (255, 0, 0), rect)
