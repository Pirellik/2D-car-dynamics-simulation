from pygame.math import Vector2
from math import tan, radians, degrees, pi
import numpy as np


class Car:
    def __init__(self, x, y, angle=0.0, length=5):
        self.position = Vector2(x, y)
        self.velocity = Vector2(0.0, 0.0)
        self.angle = angle
        self.length = length
        self.brake_deceleration = 10
        self.free_deceleration = 2

        self.acceleration = 0.0
        self.steering = 0.0
        self.gear = 0
        self.throttle = 0
        self.brakes = 0
        self.wheel_rpm = 0

        # Parts:
        self.engine = Engine(self)

        # Characteristics:
        self.gears = {0: 0, 1: 2.66, 2: 1.78, 3: 1.3, 4: 1.0, 5: 0.74, 6: 0.5, -1: -2.9}
        self.diff_ratio = 3.42
        self.n = 0.8  # power transfer efficiency
        self.wheel_radius = 0.35
        self.mass = 1300
        self.rear_wheels_mass = 100
        self.c_drag = 0.4257

    def get_driver_input(self, throttle, gear, steering_angle):
        if throttle > 0:
            self.throttle = throttle
        else:
            self.throttle = 0
        self.gear = gear
        self.steering = steering_angle

    def update(self, dt):

        drive_force = self.engine.get_torque() * self.diff_ratio * \
                      self.gears[self.gear] * self.n / self.wheel_radius
        #print(self.velocity.length())
        drag_force = - self.c_drag * self.velocity.length() * self.velocity.length()
        rolling_resistance = - 12.8 * self.velocity.length()
        print(self.velocity.length() * 10/3.6)

        long_force = drive_force + drag_force + rolling_resistance
        #print(long_force)
        self.acceleration = long_force / self.mass
        self.wheel_rpm = self.velocity.length() / self.wheel_radius * 30 / pi

        self.velocity += Vector2(self.acceleration * dt, 0)

        if self.steering:
            turning_radius = self.length / tan(radians(self.steering))
            angular_velocity = self.velocity.x / turning_radius
        else:
            angular_velocity = 0

        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += degrees(angular_velocity) * dt


class Engine:
    def __init__(self, car):
        self.car = car

        self.rpm_lut = np.array([1000, 2000, 3000, 4000, 4500, 5000, 6000])
        self.torque_lut = np.array([290, 325, 340, 350, 360, 345, 285])

    def get_torque(self):
        wheels_rpm = self.car.wheel_rpm
        rpm = wheels_rpm * self.car.diff_ratio * self.car.gears[self.car.gear]
        if rpm < 1000:
            rpm = 1000
        torque = np.interp(rpm, self.rpm_lut, self.torque_lut)
        return torque * self.car.throttle
