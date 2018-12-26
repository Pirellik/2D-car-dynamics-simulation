import xml.etree.ElementTree as ET
import pygame
import numpy as np
from math import sqrt, sin, cos, e, floor
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point, LineString
import copy


CIRCLE_TAG_NAME = '{http://www.w3.org/2000/svg}circle'


def generate_list_of_factors(size, deviation):
    list_of_factors = []
    for index in range(size):
        list_of_factors.append(e**(- (index - floor(size / 2)) ** 2 / (2 * deviation ** 2)))
    return list_of_factors


class TrackChunk:
    def __init__(self, point_1=(0, 0), point_2=(0, 0), point_3=(0, 0), point_4=(0, 0)):
        self.polygon = Polygon([point_1, point_2, point_3, point_4])
        self.is_active = False


class Track:
    def __init__(self, track_file_path='track3.svg', resize_factor=2.5, width=65):
        tree = self.read_svg_file(track_file_path)
        self.width = width

        self.track_points = [(resize_factor * x, resize_factor * y) for x, y in self.get_all_points(tree)]
        self.track_polygon = Polygon(self.track_points)
        self.path = []

        self.inner_edge = []
        self.outer_edge = []

        for index in range(len(self.track_points) - 1):
            a1 = self.track_points[index + 1][1] - self.track_points[index][1]
            b1 = self.track_points[index + 1][0] - self.track_points[index][0]
            if abs(b1) == 0:
                vector = np.array((self.width, 0))
                continue
            elif abs(a1) == 0:
                vector = np.array((0, self.width))
                continue
            else:
                a = b1 / a1
                x = self.width / sqrt(1 + a ** 2)
                vector = np.array((x, - a * x))
            if self.track_polygon.contains(Point(self.track_points[index] + vector)):
                self.inner_edge.append(self.track_points[index] + vector + [1366/2, 768/2])
                self.outer_edge.append(self.track_points[index] - vector + [1366/2, 768/2])
            else:
                self.inner_edge.append(self.track_points[index] - vector + [1366/2, 768/2])
                self.outer_edge.append(self.track_points[index] + vector + [1366/2, 768/2])

            self.path.append((np.array(self.inner_edge[- 1]) + np.array(self.outer_edge[- 1])) / 2)

        a1 = self.track_points[0][1] - self.track_points[-1][1]
        b1 = self.track_points[0][0] - self.track_points[-1][0]

        if abs(b1) == 0:
            vector = np.array((self.width, 0))
        elif abs(a1) == 0:
            vector = np.array((0, self.width))
        else:
            a = b1 / a1
            x = self.width / sqrt(1 + a ** 2)
            vector = np.array((x, - a * x))
        if self.track_polygon.contains(Point(self.track_points[-1] + vector)):
            self.inner_edge.append(self.track_points[-1] + vector + [1366/2, 768/2])
            self.outer_edge.append(self.track_points[-1] - vector + [1366/2, 768/2])
        else:
            self.inner_edge.append(self.track_points[-1] - vector + [1366/2, 768/2])
            self.outer_edge.append(self.track_points[-1] + vector + [1366/2, 768/2])

        self.path.append((np.array(self.inner_edge[- 1]) + np.array(self.outer_edge[- 1])) / 2)
        self.path_deformations = [0.5 for _ in range(len(self.path))]
        self.track_chunks = []
        for index in range(len(self.outer_edge) - 1, -1, -1):
                self.track_chunks.append(TrackChunk(self.inner_edge[index - 1], self.outer_edge[index - 1],
                                                    self.outer_edge[index], self.inner_edge[index]))
        self.track_chunks = list(reversed(self.track_chunks))
        self.track_chunks[0].is_active = True

    def apply_deformations(self, deformations):
        if len(deformations) != len(self.path_deformations):
            print("Wrong solution vector length.")
            return
        self.path_deformations = deformations
        for j in range(len(self.path)):
            self.path[j] = self.path_deformations[j] * self.outer_edge[j] + (1 - self.path_deformations[j]) * self.inner_edge[j]

    def modify_path(self, index, deformation, number_of_neighbours, deviation):
        if index + number_of_neighbours / 2 > len(self.path) - 1:
            index = index - len(self.path) - 1
        factors = generate_list_of_factors(number_of_neighbours, deviation)
        for i, factor in enumerate(factors):
            self.path_deformations[index + i - floor(len(factors) / 2)] += factor * deformation / 20
            if self.path_deformations[index + i - floor(len(factors) / 2)] > 0.9:
                self.path_deformations[index + i - floor(len(factors) / 2)] = 0.9
            if self.path_deformations[index + i - floor(len(factors) / 2)] < 0.1:
                self.path_deformations[index + i - floor(len(factors) / 2)] = 0.1

        for j in range(len(self.path)):
            self.path[j] = self.path_deformations[j] * self.outer_edge[j] + (1 - self.path_deformations[j]) * self.inner_edge[j]

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

    def check_car_position(self, trace):
        indexes = []
        trace_linestring = LineString(trace)
        for chunk in self.track_chunks:
            if not chunk.is_active:
                if chunk.polygon.intersects(trace_linestring):
                    chunk.is_active = True

            if chunk.is_active:
                indexes.append(self.track_chunks.index(chunk))

        return indexes


class TrackDrawer:
    def __init__(self, track):
        self.track = track
        self.path_for_drawing = copy.copy(self.track.path)
        self.inner_edge_for_drawing = copy.copy(self.track.inner_edge)
        self.outer_edge_for_drawing = copy.copy(self.track.outer_edge)

    def draw(self, screen, car_position, trace):
        for ind, point in enumerate(self.track.path):
            self.path_for_drawing[ind] = np.array(point) - np.array([car_position.x, car_position.y])
        for ind, point in enumerate(self.track.inner_edge):
            self.inner_edge_for_drawing[ind] = np.array(point) - np.array([car_position.x, car_position.y])
        for ind, point in enumerate(self.track.outer_edge):
            self.outer_edge_for_drawing[ind] = np.array(point) - np.array([car_position.x, car_position.y])

        chunk_indexes = self.track.check_car_position(trace)
        chunk_xy = {}
        for index in chunk_indexes:
            chunk_xy[index] = self.track.track_chunks[index].polygon.exterior.xy
            chunk_xy[index] = [np.array((x, y)) for x, y in zip(chunk_xy[index][0], chunk_xy[index][1])]
            for ind, point in enumerate(chunk_xy[index]):
                chunk_xy[index][ind] = point - np.array([car_position.x, car_position.y])
            pygame.draw.polygon(screen, (20, 70, 20), chunk_xy[index])


        pygame.draw.lines(screen, (0, 0, 255), False, [(x - car_position.x, y - car_position.y) for x, y in trace], 2)
        pygame.draw.polygon(screen, (0, 255, 0), self.path_for_drawing, 2)
        pygame.draw.polygon(screen, (255, 0, 0), self.inner_edge_for_drawing, 2)
        pygame.draw.polygon(screen, (255, 0, 0), self.outer_edge_for_drawing, 2)
