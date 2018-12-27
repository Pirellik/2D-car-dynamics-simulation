from track import *
from car_model import Car
from input_providers import *
from pygame.math import Vector2

class Simulator:
    def __init__(self, track_path, timeout=30):
        self.track = Track(track_path)
        self.timeout = timeout

    def run(self, dt, solution, car=None):
        if car is None:
            car = Car(1366 / 20, 768 / 20)

        car.position.x, car.position.y = self.track.path[0][0] / 10 - 1366 / 20, self.track.path[0][1] / 10 - 768 / 20
        self.track.apply_deformations(list(solution.Deformation))
        input_provider = AutonomousDriver(solution)
        time = 0
        trace = [(car.position.x * 10 + 1366 / 2, car.position.y * 10 + 768 / 2) for _ in range(3)]

        while True:
            time += dt
            if time > self.timeout:
                break

            # User input
            indexes = self.track.check_car_position(trace)
            input_provider.index = indexes[-1]

            car_input = input_provider.get_input()
            car.get_driver_input(car_input[0], car_input[1], car_input[2], car_input[3])
            car.update(dt)

            vector = Vector2(40, 0).rotate(-car.angle)
            vector = np.array((vector.x + 1366 / 2, vector.y + 768 / 2))
            front_center = Point(np.array((car.position.x * 10, car.position.y * 10)) + vector)
            if Polygon(self.track.path).contains(front_center):
                input_provider.line_error = - LineString(self.track.path).distance(front_center)
            else:
                input_provider.line_error = LineString(self.track.path).distance(front_center)

            trace.pop(2)
            trace.insert(0, (car.position.x * 10 + 1366 / 2, car.position.y * 10 + 768 / 2))

            if input_provider.index == len(self.track.track_chunks) - 1:
                break

        finished = True
        for chunk in self.track.track_chunks:
            if not chunk.is_active:
                finished = False
                break

        for index in range(1, len(self.track.track_chunks)):
            self.track.track_chunks[index].is_active = False
        if finished and time < self.timeout:
            return time
        else:
            return 99999
