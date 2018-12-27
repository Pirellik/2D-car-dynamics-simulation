import pygame


class CarDataDisplay:
    def __init__(self, car):
        self.car = car
        pygame.font.init()

    def display_data(self, screen, position=(0, 0), font='Verdana', size=20):
        font_color = (0, 0, 0)
        font = pygame.font.SysFont(font, size)
        vel_long = font.render('Long velocity: ' + str(round(self.car.velocity.x * 3.6, 2)), False, font_color)
        vel_lat = font.render("Lat velocity: " + str(round(self.car.velocity.y * 3.6, 2)), False, font_color)
        rpm = font.render('Engine RPM: ' + str(round(self.car.wheel_rpm * self.car.diff_ratio * self.car.gears[self.car.gear], 2)),
                          False, font_color)
        gear = font.render('Gear: ' + str(self.car.gear), False, font_color)

        screen.blit(vel_long, position)
        screen.blit(vel_lat, (position[0], position[1] + (size * 5 / 4)))
        screen.blit(rpm, (position[0], position[1] + 2 * (size * 5 / 4)))
        screen.blit(gear, (position[0], position[1] + 3 * (size * 5/4)))
