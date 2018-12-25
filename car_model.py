from pygame.math import Vector2
from math import tan, radians, degrees, pi
import numpy as np


class Car:
    def __init__(self, x, y, angle=0.0, length=5):
        self.position = Vector2(x, y)
        self.front_center = Vector2(0, 0)
        self.velocity = Vector2(0.0, 0.0)
        self.angle = angle
        self.length = length
        self.width = 2
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
        self.gears = {0: 0, 1: 3, 2: 2, 3: 1.5, 4: 1.25, 5: 1, 6: 0.75, -1: -2.9}
        self.diff_ratio = 3.42
        self.n = 0.8  # power transfer efficiency
        self.wheel_radius = 0.35
        self.mass = 1300
        self.rear_wheels_mass = 100
        self.c_drag = 0.4257

    def get_driver_input(self, throttle, gear,  brakes, steering_angle,):
        self.throttle = abs(throttle)

        if brakes > 0:
            self.brakes = brakes
        else:
            self.brakes = 0
        self.gear = gear
        self.steering = steering_angle

    def update(self, dt):

        drive_force = self.engine.get_torque() * self.diff_ratio * \
                      self.gears[self.gear] * (self.n / self.wheel_radius) * self.throttle
        braking = self.brake_deceleration * self.brakes
        #print(self.velocity.length())
        drag_force = - self.c_drag * self.velocity.x * self.velocity.x
        rolling_resistance = - 12.8 * self.velocity.x
        #print(self.velocity.length() * 3.6)

        long_force = drive_force + drag_force + rolling_resistance
        if self.velocity.x > 0:
            long_force -= braking
        elif self.velocity.x < 0:
            long_force += braking
        #print(long_force)

        #print(long_force)
        self.acceleration = long_force / self.mass
        self.wheel_rpm = self.velocity.length() / self.wheel_radius * 30 / pi

        max_speed_side = 40

        self.velocity += Vector2(self.acceleration * dt, 0)

        if abs(self.velocity.y) > 0.01:
            mi1 = 9.9
            F = mi1 * (self.mass / 2) * 9.81
            a = F / self.mass
            #print(self.velocity.y)
            if a * dt > abs(self.velocity.y):
                self.velocity.y = 0
            else:
                self.velocity.y -= np.sign(self.velocity.y)*a*dt

        if self.steering:
            turning_radius = self.length / tan(radians(self.steering))
            angular_velocity = self.velocity.x / turning_radius

            F_centrifugal = (self.mass*self.velocity.x*self.velocity.x) / abs(turning_radius) #odsrodkowa
            #print(F_od)
            mi_front_side = 0.9
            mi_back_side = 0.4
            F_max_front = mi_front_side * (self.mass / 2) * 9.81
            #print(F_max1)
            F_max_back = mi_back_side * (self.mass / 2) * 9.81
            F_back = 0
            F_front = 0
            if F_centrifugal > F_max_front:
                #print(F_od, F_max1)
                F_front = F_centrifugal/2 - F_max_front

            if F_centrifugal > F_max_back:
                F_back = F_centrifugal/2 - F_max_back


            inertia = (1/12)*self.mass*(self.length ** 2 + self.width ** 2)
            torque = F_back*self.length/4 #- F_front*self.length/2
            omega = torque/inertia
            angular_velocity -= np.sign(self.steering) * omega * dt
            #print(F_back, F_front, torque, omega)


            F = min(F_back, F_front)
            a = F/self.mass
            if abs(self.velocity.y + np.sign(self.steering)*a*dt) < max_speed_side:
                self.velocity.y += np.sign(self.steering)*a*dt
            else:
                pass#self.velocity.y = max_speed_side

        else:
            angular_velocity = 0

        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += degrees(angular_velocity) * dt


class Engine:
    def __init__(self, car):
        self.car = car

        self.rpm_lut = np.array([1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000])
        self.torque_lut = np.array([180, 350, 550, 850, 1000, 1000, 900, 450, 0])

    def get_torque(self):
        wheels_rpm = self.car.wheel_rpm
        rpm = wheels_rpm * self.car.diff_ratio * self.car.gears[self.car.gear]
        if rpm < 1000:
            rpm = 1000
        torque = np.interp(rpm, self.rpm_lut, self.torque_lut)
        return torque * self.car.throttle
