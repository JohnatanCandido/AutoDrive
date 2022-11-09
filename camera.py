import pygame

from car import Car
from pygame.math import Vector2


car_img = pygame.image.load('car.png')


class Camera:
    def __init__(self, car: Car):
        self.car = car
        self.display = pygame.display.set_mode((1000, 600))

    def blit_car(self):
        rotated = pygame.transform.rotate(car_img, self.car.angle)
        rect = rotated.get_rect()
        self.display.blit(rotated, self.car.initial_position - (rect.width / 2, rect.height / 2))

    def blit(self, img, x, y):
        self.display.blit(img, self.get_corrected_coordinates(x, y))

    def get_corrected_coordinates(self, x, y):
        x = x - self.car.position.x + self.car.initial_position.x
        y = y - self.car.position.y + self.car.initial_position.y
        return x, y

    def draw_line(self, color, initial_x, initial_y, end_x, end_y):
        pygame.draw.line(self.display,
                         color,
                         self.get_corrected_coordinates(initial_x, initial_y),
                         self.get_corrected_coordinates(end_x, end_y))
