import xml.etree.ElementTree as ET
import pygame
import numpy as np
from math import sqrt, sin, cos, e, floor
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point


CIRCLE_TAG_NAME = '{http://www.w3.org/2000/svg}circle'


def generate_list_of_factors(size, deviation):
    list_of_factors = []
    for index in range(size):
        list_of_factors.append(e**(- (index - floor(size / 2)) ** 2 / (2 * deviation ** 2)))
    return list_of_factors


class Road:
    def __init__(self, car, road_file_path='track3.svg', resize_factor=2.5):
        self.car = car
        tree = self.read_svg_file(road_file_path)
        width = 65

        self.track_points = [(resize_factor * x, resize_factor * y) for x, y in self.get_all_points(tree)]
        self.track_polygon = Polygon(self.track_points)
        self.path = []
        self.path_for_drawing = []

        self.inner_road = []
        self.outer_road = []

        for index in range(len(self.track_points) - 1):
            a1 = self.track_points[index + 1][1] - self.track_points[index][1]
            b1 = self.track_points[index + 1][0] - self.track_points[index][0]
            if abs(b1) == 0:
                vector = np.array((width, 0))
                continue
            elif abs(a1) == 0:
                vector = np.array((0, width))
                continue
            else:
                a = b1 / a1
                x = width / sqrt(1 + a ** 2)
                vector = np.array((x, - a * x))
            if self.track_polygon.contains(Point(self.track_points[index] + vector)):
                self.inner_road.append(self.track_points[index] + vector)
                self.outer_road.append(self.track_points[index] - vector)
            else:
                self.inner_road.append(self.track_points[index] - vector)
                self.outer_road.append(self.track_points[index] + vector)

            self.path.append((np.array(self.inner_road[- 1]) + np.array(self.outer_road[- 1])) / 2)
            self.path_for_drawing.append((np.array(self.inner_road[- 1]) + np.array(self.outer_road[- 1])) / 2)

        a1 = self.track_points[0][1] - self.track_points[-1][1]
        b1 = self.track_points[0][0] - self.track_points[-1][0]

        if abs(b1) == 0:
            vector = np.array((width, 0))
        elif abs(a1) == 0:
            vector = np.array((0, width))
        else:
            a = b1 / a1
            x = width / sqrt(1 + a ** 2)
            vector = np.array((x, - a * x))
        if self.track_polygon.contains(Point(self.track_points[-1] + vector)):
            self.inner_road.append(self.track_points[-1] + vector)
            self.outer_road.append(self.track_points[-1] - vector)
        else:
            self.inner_road.append(self.track_points[-1] - vector)
            self.outer_road.append(self.track_points[-1] + vector)

        self.path.append((np.array(self.inner_road[- 1]) + np.array(self.outer_road[- 1])) / 2)
        self.path_for_drawing.append((np.array(self.inner_road[- 1]) + np.array(self.outer_road[- 1])) / 2)

        self.inner_road_for_drawing = list(range(len(self.inner_road)))
        self.outer_road_for_drawing = list(range(len(self.outer_road)))

    def modify_path(self, index, deflexion, number_of_neighbours, deviation):
        factors = generate_list_of_factors(number_of_neighbours, deviation)
        for i, factor in enumerate(factors):
            self.path[index + i - floor(len(factors) / 2)] = 0.5 * ((1 + factor * deflexion / 11) * self.outer_road[index + i - floor(len(factors) / 2)] + (1 - factor * deflexion / 11) * self.inner_road[index + i - floor(len(factors) / 2)])
            self.path_for_drawing[index + i - floor(len(factors) / 2)] = 0.5 * ((1 + factor * deflexion / 11) * self.outer_road[index + i - floor(len(factors) / 2)] + (1 - factor * deflexion / 11) * self.inner_road[index + i - floor(len(factors) / 2)])



    @staticmethod
    def circle_to_point(circle):
        const = 6
        return float(circle.attrib['cx']) * const, float(circle.attrib['cy']) * const

    @staticmethod
    def read_svg_file(svg_path):
        return ET.parse(svg_path)

    def get_all_points(self, tree):
        circles = []
        for circle in tree.iter(CIRCLE_TAG_NAME):
                circles.append(self.circle_to_point(circle))
        return circles

    def draw(self, screen):
        for ind, point in enumerate(self.path):
            self.path_for_drawing[ind] = np.array(point) - np.array([self.car.position.x, self.car.position.y]) * 10 + [1366/2, 768/2]
        for ind, point in enumerate(self.inner_road):
            self.inner_road_for_drawing[ind] = np.array(point) - np.array([self.car.position.x, self.car.position.y]) * 10 + [1366/2, 768/2]
        for ind, point in enumerate(self.outer_road):
            self.outer_road_for_drawing[ind] = np.array(point) - np.array([self.car.position.x, self.car.position.y]) * 10 + [1366/2, 768/2]

        pygame.draw.polygon(screen, (0, 255, 0), self.path_for_drawing, 2)
        pygame.draw.polygon(screen, (255, 0, 0), self.inner_road_for_drawing, 2)
        pygame.draw.polygon(screen, (255, 0, 0), self.outer_road_for_drawing, 2)
