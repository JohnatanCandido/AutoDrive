from gym import Env
from gym.spaces import Box, MultiDiscrete

from stable_baselines3 import PPO

import numpy as np
import pygame
import os

from car import Car
from camera import Camera
from math import sin, cos, radians, sqrt
from PIL import Image

PPO_Path = os.path.join('Saved Models', 'PPO_Auto_Drive')

pygame.init()
clock = pygame.time.Clock()


class GameOverException(Exception):
    pass


def get_checkpoints():
    return [
        (1365, 1280),
        (2300, 1320),
        (2600, 385),
        (3320, 450),
        (4200, 2060),
        (4900, 1670),
        (4950, 580),
        (6170, 1130),
        (6850, 2800),
        (3100, 2470),
        (2270, 2020),
        (2050, 2960),
        (300, 2900),
    ]


class AutoDrive(Env):
    def __init__(self, render=False):
        self.car_img = pygame.image.load('car.png')
        self.background_img = pygame.image.load('track_1.png')
        self.background = np.asarray(Image.open('track_1.png'))
        self.car = Car(self.car_img.get_width(), self.car_img.get_height())
        self.max_depth = 1000

        self.action_space = MultiDiscrete([3, 3])
        self.observation_space = Box(low=0, high=self.max_depth, shape=(7,), dtype=float)

        self.checkpoints = get_checkpoints()

        if render:
            self.camera = Camera(self.car)

    def step(self, action):
        info = {}
        state = [0, 0, 0, 0, 0, 0]

        try:
            dt = 0.022
            initial_distance = self.get_euclidian_dist(self.checkpoints[0][0], self.checkpoints[0][1])

            self.process_input(action)
            self.move_car(dt)
            state = self.get_readings()
            done = not self.checkpoints
            if not done:
                checkpoints_updated = self.update_checkpoints()
                new_distance = self.get_euclidian_dist(self.checkpoints[0][0], self.checkpoints[0][1])
                if checkpoints_updated:
                    reward = 2
                else:
                    reward = (initial_distance - new_distance) / initial_distance\
                             + ((self.car.velocity.x / self.car.max_velocity) / 2)
            else:
                reward = 5
        except GameOverException:
            reward = -1
            done = True

        return np.asarray(state), reward, done, info

    def update_checkpoints(self):
        if self.get_euclidian_dist(self.checkpoints[0][0], self.checkpoints[0][1]) < 100:
            self.checkpoints.pop(0)
            return True
        return False

    def process_input(self, action):
        self.check_acceleration(action[0]-1)
        self.check_steering(action[1]-1)

    def check_acceleration(self, action):
        if action < 0:
            self.car.press_accelerate()
            self.car.release_brake()
        elif action > 0:
            self.car.release_accelerate()
            self.car.press_brake()
        else:
            self.car.release_accelerate()
            self.car.release_brake()

    def check_steering(self, action):
        if action < 0:
            self.car.reset_steering()
            self.car.steer_right()
        elif action > 0:
            self.car.reset_steering()
            self.car.steer_left()
        else:
            self.car.reset_steering()

    def move_car(self, dt):
        self.car.move(dt)
        for point in self.car.get_sides():
            x = int(point[0])
            y = int(point[1])
            if self.background[y][x][0] != 0:
                self.car.reset()
                raise GameOverException

    def get_readings(self):
        x, y = self.car.get_front_left()
        s1 = self.get_sensor(x, y, self.car.get_correct_angle() - 90)
        s2 = self.get_sensor(x, y, self.car.get_correct_angle() - 135)
        s3 = self.get_sensor(x, y, self.car.get_correct_angle() - 180)

        x, y = self.car.get_front_right()
        s4 = self.get_sensor(x, y, self.car.get_correct_angle() - 90)
        s5 = self.get_sensor(x, y, self.car.get_correct_angle() - 45)
        s6 = self.get_sensor(x, y, self.car.get_correct_angle())

        return [s1, s2, s3, s4, s5, s6, self.car.velocity.x]

    def get_sensor(self, start_x, start_y, angle):
        for depth in range(self.max_depth):
            target_x = int(start_x - sin(radians(angle)) * depth)
            target_y = int(start_y + cos(radians(angle)) * depth)

            try:
                if self.background[target_y][target_x][0] != 0 or depth == self.max_depth-1:
                    return self.get_euclidian_dist(target_x, target_y)
            except IndexError:
                return self.get_euclidian_dist(target_x, target_y)

    def get_euclidian_dist(self, x, y):
        return sqrt((self.car.position.x - x) ** 2 + (self.car.position.y - y) ** 2)

    def reset(self):
        self.car.reset()
        self.checkpoints = get_checkpoints()
        return np.asarray(self.get_readings())

    def render(self, mode="human"):
        if self.camera is not None:
            self.camera.blit(self.background_img, 0, 0)
            self.camera.blit_car()
            self.camera.draw_line((255, 0, 0),
                                  self.car.position.x,
                                  self.car.position.y,
                                  self.checkpoints[0][0],
                                  self.checkpoints[0][1])


def train():
    env = AutoDrive()
    try:
        # Loads the model from the informed path
        model = PPO.load(PPO_Path, env=env)
    except FileNotFoundError:
        model = PPO('MlpPolicy', env, verbose=1)

    model.learn(total_timesteps=100000)
    model.save(PPO_Path)


def test():
    env = AutoDrive(True)
    model = PPO.load(PPO_Path, env=env)

    for episode in range(1, 20):
        obs = env.reset()
        done = False
        score = 0

        while not done:
            action, _ = model.predict(obs)
            obs, reward, done, info = env.step(action)
            score += reward

            env.render()
            pygame.display.update()
        print(f'Episode {episode} Score {score}')


if __name__ == '__main__':
    # train()
    test()

pygame.quit()
quit()
