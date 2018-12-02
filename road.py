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


class RoadChunk:
    def __init__(self, point_1, point_2, point_3, point_4):
        self.polygon = Polygon([point_1, point_2, point_3, point_4])
        self.is_active = False


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

        self.road_chunks = []




        self.path_deflexions = [0.5 for _ in range(len(self.path))]

    def modify_path(self, index, deflexion, number_of_neighbours, deviation):
        if index + number_of_neighbours / 2 > len(self.path) - 1:
            index = index - len(self.path) - 1
        factors = generate_list_of_factors(number_of_neighbours, deviation)
        for i, factor in enumerate(factors):
            self.path_deflexions[index + i - floor(len(factors) / 2)] += factor * deflexion / 20
            if self.path_deflexions[index + i - floor(len(factors) / 2)] > 0.9:
                self.path_deflexions[index + i - floor(len(factors) / 2)] = 0.9
            if self.path_deflexions[index + i - floor(len(factors) / 2)] < 0.1:
                self.path_deflexions[index + i - floor(len(factors) / 2)] = 0.1

        for j in range(len(self.path)):
            self.path[j] = self.path_deflexions[j] * self.outer_road[j] + (1 - self.path_deflexions[j]) * self.inner_road[j]
            self.path_for_drawing[j] = self.path_deflexions[j] * self.outer_road[j] + (1 - self.path_deflexions[j]) * self.inner_road[j]

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

        for index in range(len(self.outer_road_for_drawing) - 1, -1, -1):
            try:
                self.road_chunks[index].polygon = Polygon([self.inner_road_for_drawing[index - 1], self.outer_road_for_drawing[index - 1], self.outer_road_for_drawing[index], self.inner_road_for_drawing[index]])
            except:
                self.road_chunks.append(
                    RoadChunk(self.inner_road_for_drawing[index - 1], self.outer_road_for_drawing[index - 1],
                     self.outer_road_for_drawing[index], self.inner_road_for_drawing[index]))

        for chunk in self.road_chunks:
            if chunk.polygon.contains(Point(1366/2, 768/2)):
                chunk.is_active = True
            if chunk.is_active:
                polygon = chunk.polygon.exterior.xy
                polygon = [(x, y) for x, y in zip(polygon[0], polygon[1])]
                pygame.draw.polygon(screen, (0, 35, 0), polygon)

        pygame.draw.polygon(screen, (0, 255, 0), self.path_for_drawing, 2)
        pygame.draw.polygon(screen, (255, 0, 0), self.inner_road_for_drawing, 2)
        pygame.draw.polygon(screen, (255, 0, 0), self.outer_road_for_drawing, 2)
