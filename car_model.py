from pygame.math import Vector2
from math import tan, radians, degrees, pi, atan2, sin, cos
import numpy as np


class Car:
    def __init__(self, x, y, angle=0.0, length=5):
        self.position = Vector2(x, y)
        self.velocity = Vector2(0.0, 0.0)
        self.angle = angle
        self.length = length
        self.width = 2
        self.brake_deceleration = 30000
        self.free_deceleration = 2

        self.acceleration = Vector2(0, 0)
        self.steering = 0.0
        self.gear = 0
        self.throttle = 0
        self.brakes = 0
        self.wheel_rpm = 0
        self.rpm = 2000
        self.angular_velocity = 0
        self.force = Vector2(0, 0)

        # Parts:
        self.engine = Engine()

        # Characteristics:
        self.gears = {0: 0, 1: 3, 2: 2, 3: 1.5, 4: 1.25, 5: 1, 6: 0.75, -1: -2.9}
        self.diff_ratio = 3.42
        self.n = 0.8  # power transfer efficiency
        self.wheel_radius = 0.35
        self.mass = 1100
        self.rear_wheels_mass = 100
        self.c_drag = 0.4257
        self.cornering_stiffness_f = -5.0
        self.cornering_stiffness_r = -5.2
        self.max_grip = 2.0

    def get_driver_input(self, throttle, gear, brakes, steering_angle):
        self.brakes = brakes
        self.gear = gear
        self.steering = steering_angle
        self.throttle = abs(throttle)

    def update(self, dt):
        self.rpm = self.wheel_rpm * self.diff_ratio * self.gears[self.gear]

        if self.rpm < 2000:
            self.rpm = 2000

        traction_force = self.engine.get_torque(self.rpm, self.throttle) * self.diff_ratio * \
                         self.gears[self.gear] * (self.n / self.wheel_radius) - \
                         self.brake_deceleration * self.brakes * np.sign(self.velocity.x)

        resistance_force = Vector2(- self.c_drag * self.velocity.x * abs(self.velocity.x) - 12.8 * self.velocity.x,
                                   - self.c_drag * self.velocity.y * abs(self.velocity.y) - 12.8 * self.velocity.y)

        if self.velocity.x > 5.55:
            yawspeed = 2 * self.angular_velocity

            if self.velocity.x == 0:
                rot_angle = 0
                sideslip = 0

            else:
                rot_angle = atan2(yawspeed, self.velocity.x)
                sideslip = atan2(self.velocity.y, self.velocity.x)

            slipanglefront = sideslip + rot_angle - radians(self.steering)
            slipanglerear = sideslip - rot_angle

            flatf = Vector2(0, 0)
            flatr = Vector2(0, 0)

            flatf.x = 0
            flatf.y = self.cornering_stiffness_f * slipanglefront
            flatf.y = min(self.max_grip, flatf.y)
            flatf.y = max(-self.max_grip, flatf.y)
            flatf.y *= self.mass * 4.9

            flatr.x = 0
            flatr.y = self.cornering_stiffness_r * slipanglerear
            flatr.y = min(self.max_grip, flatr.y)
            flatr.y = max(- self.max_grip, flatr.y)
            flatr.y *= self.mass * 4.9

            self.force.x = traction_force + sin(radians(self.steering)) * flatf.x + flatr.x + resistance_force.x
            self.force.y = cos(radians(self.steering)) * flatf.y + flatr.y + resistance_force.y

            torque = 1.5 * (flatf.y - flatr.y)

            self.acceleration = self.force / self.mass
            self.wheel_rpm = self.velocity.x / self.wheel_radius * 30 / pi

            self.velocity += self.acceleration * dt
            self.position += self.velocity.rotate(-self.angle) * dt

            angular_acceleration = torque / 1000
            self.angular_velocity += angular_acceleration * dt
            self.angle += degrees(self.angular_velocity) * dt

        else:
            self.force.x = traction_force + resistance_force.x
            self.force.y = resistance_force.y
            self.acceleration = self.force / self.mass
            self.wheel_rpm = self.velocity.x / self.wheel_radius * 30 / pi

            self.velocity += self.acceleration * dt
            if self.steering:
                turning_radius = self.length / tan(radians(self.steering))
                angular_velocity = self.velocity.x / turning_radius
            else:
                angular_velocity = 0

            self.position += self.velocity.rotate(-self.angle) * dt
            self.angle += degrees(angular_velocity) * dt


class Engine:
    def __init__(self):
        self.rpm_lut = np.array([1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000])
        self.torque_lut = np.array([200, 325, 475, 550, 550, 500, 375, 300, 0])

    def get_torque(self, rpm, throttle):
        if rpm < 1000:
            rpm = 1000
        torque = np.interp(rpm, self.rpm_lut, self.torque_lut)
        return torque * throttle
