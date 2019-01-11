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

        # Indicators

        track_path_length = LineString(self.track.path).length / 10  # length of path loaded from solution
        regulation_quality_indicator_square = 0  # integral of squared error values
        regulation_quality_indicator_abs = 0  # integral of abs values
        max_line_error = 0  # error in m
        average_slip = 0  # average of abs lateral speed in m / s
        slip_indicator = 0  # integral of squared speed in m / s^2
        max_speed_long = 0  # m / s^2
        max_speed_lat = 0  # m / s^2
        average_speed_long = 0  # average speed longitudinal in m
        average_rpm = 0
        max_rpm = 0
        number_of_iterations = 0  # helper variable for computing averages


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

            # Update solution indicators

            number_of_iterations += 1
            average_rpm = average_rpm * (number_of_iterations - 1) / number_of_iterations + car.rpm / number_of_iterations
            average_speed_long = average_speed_long * (number_of_iterations - 1) / number_of_iterations + car.velocity.x / number_of_iterations
            average_slip = average_slip * (number_of_iterations - 1) / number_of_iterations + abs(car.velocity.y) / number_of_iterations

            regulation_quality_indicator_square += (input_provider.line_error / 10) ** 2
            regulation_quality_indicator_abs += abs(input_provider.line_error / 10)
            if abs(input_provider.line_error) / 10 > max_line_error:
                max_line_error = abs(input_provider.line_error) / 10
            slip_indicator += car.velocity.y ** 2
            if car.velocity.x > max_speed_long:
                max_speed_long = car.velocity.x
            if abs(car.velocity.y) > max_speed_lat:
                max_speed_lat = abs(car.velocity.y)
            if car.rpm > max_rpm:
                max_rpm = car.rpm

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
            return time, (track_path_length, average_rpm, average_speed_long, average_slip,
                          regulation_quality_indicator_abs, regulation_quality_indicator_square,
                          max_line_error, slip_indicator, max_speed_long, max_speed_lat, max_rpm)
        else:
            return 99999, (track_path_length, average_rpm, average_speed_long, average_slip,
                          regulation_quality_indicator_abs, regulation_quality_indicator_square,
                          max_line_error, slip_indicator, max_speed_long, max_speed_lat, max_rpm)
