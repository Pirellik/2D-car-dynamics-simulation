import xml.etree.ElementTree as ET
import pygame
import numpy as np


CIRCLE_TAG_NAME = '{http://www.w3.org/2000/svg}circle'


class Road:
    def __init__(self, car, road_file_path='track2.svg'):
        self.car = car
        tree = self.read_svg_file(road_file_path)

        style_red = "fill:#000000;stroke:none"
        style_black = "fill:#ff0000;stroke:none"

        self.track_points_right = self.get_all_points(tree, style_red)
        self.track_points_left = self.get_all_points(tree, style_black)
        self.track_points_right1 = self.get_all_points(tree, style_red)
        self.track_points_left1 = self.get_all_points(tree, style_black)

    @staticmethod
    def circle_to_point(circle):
        const = 6
        return float(circle.attrib['cx']) * const, float(circle.attrib['cy']) * const

    @staticmethod
    def read_svg_file(svg_path):
        return ET.parse(svg_path)

    def get_all_points(self, tree, style):
        circles = []
        for circle in tree.iter(CIRCLE_TAG_NAME):
            if circle.attrib['style'] == style:
                circles.append(self.circle_to_point(circle))

        return circles

    def draw(self, screen):
        for ind, point in enumerate(self.track_points_right):
            self.track_points_right1[ind] = list(np.array(point) - np.array([self.car.position.x, self.car.position.y]) * 10 + [680 + 130, 380 + 30])
        for ind, point in enumerate(self.track_points_left):
            self.track_points_left1[ind] = list(np.array(point) - np.array([self.car.position.x, self.car.position.y]) * 10 + [680 + 130, 380 + 30])

        pygame.draw.polygon(screen, (0, 255, 0), self.track_points_left1, 2)
        pygame.draw.polygon(screen, (255, 255, 0), self.track_points_right1, 2)
