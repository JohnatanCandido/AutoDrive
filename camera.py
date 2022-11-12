import pygame
from pygame.math import Vector2

from car import Car


class Camera:
    def __init__(self, car: Car, car_img):
        self.car = car
        self.car_img = car_img
        self.display = pygame.display.set_mode((1000, 600))

    def blit_car(self):
        rotated = pygame.transform.rotate(self.car_img, self.car.angle)
        rect = rotated.get_rect()
        rotated.set_colorkey((0, 0, 0))
        self.display.blit(rotated, Vector2(450, 300) - (rect.width / 2, rect.height / 2))

    def blit(self, img, x, y):
        self.display.blit(img, self.get_corrected_coordinates(x, y))

    def get_corrected_coordinates(self, x, y):
        x = x - self.car.position.x + 450
        y = y - self.car.position.y + 300
        return x, y

    def draw_line(self, color, initial_x, initial_y, end_x, end_y):
        pygame.draw.line(self.display,
                         color,
                         self.get_corrected_coordinates(initial_x, initial_y),
                         self.get_corrected_coordinates(end_x, end_y))

    def draw_hud(self):
        colors = [(150, 150, 150), (100, 100, 100)]

        self.draw_button('W', colors[int(self.car.accelerating)], 60, 490)
        self.draw_button('S', colors[int(self.car.braking)], 60, 540)
        self.draw_button('A', colors[int(self.car.steering > 0)], 10, 540)
        self.draw_button('D', colors[int(self.car.steering < 0)], 110, 540)

        pygame.draw.rect(self.display, colors[0], [170, 540, 155, 50])
        speed = '{: >4}'.format(int(self.car.velocity.x))
        self.draw_text(f'Speed: {speed}', 245, 565)

    def draw_button(self, text, color, x, y):
        pygame.draw.rect(self.display, color, [x, y, 50, 50])
        self.draw_text(text, x + 25, y + 25)

    def draw_text(self, text, x, y):
        large_text = pygame.font.Font('freesansbold.ttf', 25)
        text_surface = large_text.render(text, True, (0, 0, 0))
        txt_surf, text_rect = text_surface, text_surface.get_rect()
        text_rect.center = (x, y)
        self.display.blit(txt_surf, text_rect)

    def draw_circle(self, color, coord, size):
        pygame.draw.circle(self.display, color, self.get_corrected_coordinates(coord[0], coord[1]), size)
