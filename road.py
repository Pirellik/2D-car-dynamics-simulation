import xml.etree.ElementTree as ET
import pygame
import numpy as np
from math import sqrt, sin, cos
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point


CIRCLE_TAG_NAME = '{http://www.w3.org/2000/svg}circle'


class Road:
    def __init__(self, car, road_file_path='track3.svg', resize_factor=2.5):
        self.car = car
        tree = self.read_svg_file(road_file_path)
        width = 65

        self.track_points_left = [(resize_factor * x, resize_factor * y) for x, y in self.get_all_points(tree)]

        self.track_points_left1 = [(resize_factor * x, resize_factor * y) for x, y in self.get_all_points(tree)]
        self.track_polygon = Polygon(self.track_points_left)

        self.inner_road = []
        self.outer_road = []

        for index in range(len(self.track_points_left) - 1):
            a1 = self.track_points_left[index + 1][1] - self.track_points_left[index][1]
            b1 = self.track_points_left[index + 1][0] - self.track_points_left[index][0]
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
            if self.track_polygon.contains(Point(self.track_points_left[index] + vector)):
                self.inner_road.append(list(self.track_points_left[index] + vector))
                self.outer_road.append(list(self.track_points_left[index] - vector))
            else:
                self.inner_road.append(list(self.track_points_left[index] - vector))
                self.outer_road.append(list(self.track_points_left[index] + vector))

        a1 = self.track_points_left[0][1] - self.track_points_left[-1][1]
        b1 = self.track_points_left[0][0] - self.track_points_left[-1][0]

        if abs(b1) == 0:
            vector = np.array((width, 0))
        elif abs(a1) == 0:
            vector = np.array((0, width))
        else:
            a = b1 / a1
            x = width / sqrt(1 + a ** 2)
            vector = np.array((x, - a * x))
        if self.track_polygon.contains(Point(self.track_points_left[-1] + vector)):
            self.inner_road.append(list(self.track_points_left[-1] + vector))
            self.outer_road.append(list(self.track_points_left[-1] - vector))
        else:
            self.inner_road.append(list(self.track_points_left[-1] - vector))
            self.outer_road.append(list(self.track_points_left[-1] + vector))

        self.inner_road1 = list(range(len(self.inner_road)))
        self.outer_road1 = list(range(len(self.outer_road)))


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
        for ind, point in enumerate(self.track_points_left):
            self.track_points_left1[ind] = list(np.array(point) - np.array([self.car.position.x, self.car.position.y]) * 10 + [1366/2, 768/2])
        for ind, point in enumerate(self.inner_road):
            self.inner_road1[ind] = list(np.array(point) - np.array([self.car.position.x, self.car.position.y]) * 10 + [1366/2, 768/2])
        for ind, point in enumerate(self.outer_road):
            self.outer_road1[ind] = list(np.array(point) - np.array([self.car.position.x, self.car.position.y]) * 10 + [1366/2, 768/2])

        pygame.draw.polygon(screen, (0, 255, 0), self.track_points_left1, 2)
        pygame.draw.polygon(screen, (255, 0, 0), self.inner_road1, 2)
        pygame.draw.polygon(screen, (255, 0, 0), self.outer_road1, 2)
