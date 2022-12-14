import pygame
from math import sin, cos, radians, sqrt, atan2, degrees

from car import Car
from camera import Camera
from track import tracks


pygame.init()

BLACK = (0, 0, 0)

car_img = pygame.image.load('car.png')
car_img.set_colorkey((0, 0, 0))
background = tracks[0].background
track = tracks[0]
checkpoints = tracks[0].get_checkpoints()

clock = pygame.time.Clock()


def get_euclidian_dist(car: Car, x, y):
    return sqrt((car.position.x - x) ** 2 + (car.position.y - y) ** 2)


def main_loop(chosen_track):
    global background, track, checkpoints
    track = chosen_track
    checkpoints = track.get_checkpoints()
    background = pygame.image.load(track.background)
    car = Car(car_img.get_width(), car_img.get_height(), track.initial_position, track.initial_angle)
    camera = Camera(car, car_img)

    while True:
        dt = clock.get_time() / 1000

        move_car(car, dt)

        camera.blit(background, 0, 0)
        camera.blit_car()
        get_sensors(car, camera)
        draw_checkpoint_line(camera, car, checkpoints[0])
        camera.draw_hud()

        pygame.display.update()
        clock.tick(45)
        process_input(car)


def move_car(car: Car, dt):
    global checkpoints

    car.move(dt)
    if get_euclidian_dist(car, checkpoints[0][0], checkpoints[0][1]) < 100:
        checkpoints.pop(0)
        if not checkpoints:
            car.reset()
            checkpoints = track.get_checkpoints()
    for point in car.get_sides():
        x = int(point[0])
        y = int(point[1])
        if background.get_at((x, y))[0] != 0:
            car.reset()
            checkpoints = track.get_checkpoints()


def get_sensors(car: Car, camera: Camera):
    x, y = car.get_front_left()
    s1 = get_sensor(x, y, car.get_correct_angle() - 90)
    s2 = get_sensor(x, y, car.get_correct_angle() - 135)
    s3 = get_sensor(x, y, car.get_correct_angle() - 180)
    draw_sensors(x, y, [s1, s2, s3], camera)

    x, y = car.get_front_right()
    s4 = get_sensor(x, y, car.get_correct_angle() - 90)
    s5 = get_sensor(x, y, car.get_correct_angle() - 45)
    s6 = get_sensor(x, y, car.get_correct_angle())
    draw_sensors(x, y, [s4, s5, s6], camera)


def get_sensor(start_x, start_y, angle):
    max_depth = 1000
    for depth in range(max_depth):
        target_x = int(start_x - sin(radians(angle)) * depth)
        target_y = int(start_y + cos(radians(angle)) * depth)

        try:
            if background.get_at((target_x, target_y))[0] != 0 or depth == max_depth-1:
                return target_x, target_y
        except IndexError:
            return target_x, target_y


def draw_sensors(initial_x, initial_y, sensors, camera: Camera):
    for sensor in sensors:
        camera.draw_line((255, 255, 0), initial_x, initial_y, sensor[0], sensor[1])


def draw_checkpoint_line(camera: Camera, car: Car, checkpoint):
    camera.draw_line((255, 0, 0), car.position.x, car.position.y, checkpoint[0], checkpoint[1])


def process_input(car: Car):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        check_acceleration(event, car)
        check_steering(event, car)


def get_angle_from_next_checkpoint(car: Car, checkpoint):
    dy = checkpoint[1] - car.position.y
    dx = checkpoint[0] - car.position.x

    line_angle = degrees(atan2(dy, dx))

    difference = abs(car.get_pov_angle() - line_angle)

    return min(difference, 360 - difference)


def check_acceleration(event, car: Car):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_w:
            car.press_accelerate()
        if event.key == pygame.K_s:
            car.press_brake()
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_w:
            car.release_accelerate()
        if event.key == pygame.K_s:
            car.release_brake()


def check_steering(event, car: Car):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_a:
            car.steer_left()
        if event.key == pygame.K_d:
            car.steer_right()
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_d:
            car.steer_left()
        if event.key == pygame.K_a:
            car.steer_right()


if __name__ == '__main__':
    main_loop(tracks[0])

pygame.quit()
quit()
