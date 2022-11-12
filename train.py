import os
import pygame

from stable_baselines3 import PPO

from auto_drive_env import AutoDrive
from track import tracks


pygame.init()

PPO_Path = os.path.join('Saved Models', 'PPO_Auto_Drive_3')
LOG_DIR = os.path.join('Logs', 'PPO_AUTO_DRIVE_3')


def train():
    env = AutoDrive(False, tracks[1])
    try:
        # Loads the model from the informed path
        model = PPO.load(PPO_Path, env=env)
    except FileNotFoundError:
        model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=LOG_DIR)

    for epoch in range(20):
        model.learn(total_timesteps=100000, reset_num_timesteps=False, tb_log_name='PPO')
        path = os.path.join('Saved Models', f'PPO_Auto_Drive_{epoch}')
        model.save(path)


def test():
    env = AutoDrive(True, tracks[1])
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
