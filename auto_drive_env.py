from gym import Env
from gym.spaces import Box, MultiDiscrete

from stable_baselines3 import PPO

import numpy as np
import pygame
import os

from car import Car
from camera import Camera
from track import tracks
from math import sin, cos, radians, sqrt, atan2, degrees
from random import randint
from PIL import Image

PPO_Path = os.path.join('Saved Models', 'PPO_Auto_Drive_0')

clock = pygame.time.Clock()


class GameOverException(Exception):
    pass


class AutoDrive(Env):
    def __init__(self, render=False, track=None):
        self.tracks = tracks
        self.track = track if track is not None else tracks[randint(0, len(tracks)-1)]
        self.background_img = pygame.image.load(self.track.background)
        self.background = np.asarray(Image.open(self.track.background))

        car_img = pygame.image.load('car.png')
        car_img.set_colorkey((0, 0, 0))
        self.car = Car(car_img.get_width(),
                       car_img.get_height(),
                       self.track.initial_position,
                       self.track.initial_angle)
        self.max_depth = 3000

        self.action_space = MultiDiscrete([3, 3])
        self.observation_space = Box(low=0, high=1, shape=(8,), dtype=float)

        self.checkpoints = self.track.get_checkpoints()

        if render:
            self.camera = Camera(self.car, car_img)

    def step(self, action):
        info = {}
        state = None

        try:
            dt = 0.022
            initial_distance = self.get_distance_from_checkpoint()

            self.process_input(action)
            self.move_car(dt)
            done = False
            checkpoints_updated = self.update_checkpoints()
            if not self.checkpoints:
                done = True
                reward = 10
            else:
                state = self.get_readings()
                new_distance = self.get_distance_from_checkpoint()
                if checkpoints_updated:
                    reward = 5
                else:
                    reward = ((initial_distance - new_distance) / initial_distance)\
                             + ((self.car.velocity.x / self.car.max_velocity) / 2)
        except GameOverException:
            reward = -10
            done = True

        return np.asarray(state), reward, done, info

    def update_checkpoints(self):
        if self.get_distance_from_checkpoint() < 150:
            self.checkpoints.pop(0)
            return True
        return False

    def get_distance_from_checkpoint(self):
        return self.get_euclidian_dist(self.checkpoints[0])

    def process_input(self, action):
        self.check_acceleration(action[0]-1)
        self.check_steering(action[1]-1)

    def check_acceleration(self, action):
        self.car.release_accelerate()
        self.car.release_brake()
        if action < 0:
            self.car.press_accelerate()
        elif action > 0:
            self.car.press_brake()

    def check_steering(self, action):
        self.car.reset_steering()
        if action < 0:
            self.car.steer_right()
        elif action > 0:
            self.car.steer_left()

    def move_car(self, dt):
        self.car.move(dt)
        for point in self.car.get_sides():
            x = int(point[0])
            y = int(point[1])
            if self.background[y][x][0] != 0:
                self.reset()
                raise GameOverException

    def get_readings(self):
        x, y = self.car.get_front_left()
        s1 = self.get_sensor_reading(x, y, self.car.get_correct_angle() - 90) / self.max_depth
        s2 = self.get_sensor_reading(x, y, self.car.get_correct_angle() - 135) / self.max_depth
        s3 = self.get_sensor_reading(x, y, self.car.get_correct_angle() - 180) / self.max_depth

        x, y = self.car.get_front_right()
        s4 = self.get_sensor_reading(x, y, self.car.get_correct_angle() - 90) / self.max_depth
        s5 = self.get_sensor_reading(x, y, self.car.get_correct_angle() - 45) / self.max_depth
        s6 = self.get_sensor_reading(x, y, self.car.get_correct_angle()) / self.max_depth

        speed = self.car.velocity.x / self.car.max_velocity
        checkpoint_angle = self.get_angle_from_next_checkpoint() / 180

        return [s1, s2, s3, s4, s5, s6, speed, checkpoint_angle]

    def get_angle_from_next_checkpoint(self):
        checkpoint = self.checkpoints[0]
        dy = checkpoint[1] - self.car.position.y
        dx = checkpoint[0] - self.car.position.x

        line_angle = degrees(atan2(dy, dx))
        difference = abs(self.car.get_pov_angle() - line_angle)

        return min(difference, 360 - difference)

    def get_sensor_reading(self, start_x, start_y, angle):
        return self.get_euclidian_dist(self.get_sensor_position(start_x, start_y, angle))

    def get_sensor_position(self, start_x, start_y, angle):
        for depth in range(self.max_depth):
            target_x = int(start_x - sin(radians(angle)) * depth)
            target_y = int(start_y + cos(radians(angle)) * depth)

            try:
                if self.background[target_y][target_x][0] != 0 or depth == self.max_depth-1:
                    return target_x, target_y
            except IndexError:
                return target_x, target_y

    def get_euclidian_dist(self, coord):
        return sqrt((self.car.position.x - coord[0]) ** 2 + (self.car.position.y - coord[1]) ** 2)

    def reset(self):
        self.car.reset()
        self.checkpoints = self.track.get_checkpoints()
        return np.asarray(self.get_readings())

    def render(self, mode="human"):
        if self.camera is not None:
            self.camera.blit(self.background_img, 0, 0)
            self.camera.blit_car()
            self.camera.draw_hud()
            self.draw_sensors()
            if self.checkpoints:
                self.camera.draw_line((255, 0, 0),
                                      self.car.position.x,
                                      self.car.position.y,
                                      self.checkpoints[0][0],
                                      self.checkpoints[0][1])

    def draw_sensors(self):
        x, y = self.car.get_front_left()
        s1 = self.get_sensor_position(x, y, self.car.get_correct_angle() - 90)
        s2 = self.get_sensor_position(x, y, self.car.get_correct_angle() - 135)
        s3 = self.get_sensor_position(x, y, self.car.get_correct_angle() - 180)
        self.camera.draw_line((255, 255, 0), x, y, s1[0], s1[1])
        self.camera.draw_line((255, 255, 0), x, y, s2[0], s2[1])
        self.camera.draw_line((255, 255, 0), x, y, s3[0], s3[1])
        self.camera.draw_circle((255, 255, 0), (s1[0], s1[1]), 3)
        self.camera.draw_circle((255, 255, 0), (s2[0], s2[1]), 3)
        self.camera.draw_circle((255, 255, 0), (s3[0], s3[1]), 3)

        x, y = self.car.get_front_right()
        s4 = self.get_sensor_position(x, y, self.car.get_correct_angle() - 90)
        s5 = self.get_sensor_position(x, y, self.car.get_correct_angle() - 45)
        s6 = self.get_sensor_position(x, y, self.car.get_correct_angle())
        self.camera.draw_line((255, 255, 0), x, y, s4[0], s4[1])
        self.camera.draw_line((255, 255, 0), x, y, s5[0], s5[1])
        self.camera.draw_line((255, 255, 0), x, y, s6[0], s6[1])
        self.camera.draw_circle((255, 255, 0), (s4[0], s4[1]), 3)
        self.camera.draw_circle((255, 255, 0), (s5[0], s5[1]), 3)
        self.camera.draw_circle((255, 255, 0), (s6[0], s6[1]), 3)
