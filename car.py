from math import sin, cos, radians, degrees, copysign
from pygame.math import Vector2

ACCELERATION = 50


class Car:
    def __init__(self, length, width):
        self.accelerating = False
        self.braking = False

        self.initial_position = Vector2(350, 300)
        self.position = Vector2(350, 300)
        self.velocity = Vector2(0.0, 0.0)
        self.max_velocity = 500

        self.angle = 0
        self.steering = 0.0
        self.max_steering = 30

        self.width = width
        self.length = length

        self.acceleration = 0.0
        self.free_deceleration = 10
        self.max_acceleration = 100
        self.brake_deceleration = 100

    def reset(self):
        self.accelerating = False
        self.braking = False

        self.position.x = self.initial_position.x
        self.position.y = self.initial_position.y
        self.angle = 0

        self.velocity = Vector2(0.0, 0.0)
        self.steering = 0.0
        self.acceleration = 0.0

    def steer_left(self):
        self.steering += self.max_steering
        self.normalize_angle()

    def steer_right(self):
        self.steering -= self.max_steering
        self.normalize_angle()

    def reset_steering(self):
        self.steering = 0.0

    def normalize_angle(self):
        if self.steering > self.max_steering:
            self.steering = self.max_steering
        elif self.steering < -self.max_steering:
            self.steering = -self.max_steering

    def press_accelerate(self):
        self.accelerating = True

    def release_accelerate(self):
        self.accelerating = False

    def press_brake(self):
        self.braking = True

    def release_brake(self):
        self.braking = False

    def move(self, dt):
        self.accelerate(dt)
        self.velocity += (self.acceleration * dt, 0)
        self.velocity.x = max(-self.max_velocity, min(self.velocity.x, self.max_velocity))

        if self.steering:
            turning_radius = self.length / sin(radians(self.steering))
            angular_velocity = self.velocity.x / turning_radius
        else:
            angular_velocity = 0

        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += degrees(angular_velocity) * dt

    def accelerate(self, dt):
        if self.accelerating:
            if self.velocity.x < 0:
                self.acceleration = self.brake_deceleration
            else:
                self.acceleration += ACCELERATION * dt
        elif self.braking:
            if self.velocity.x > 0:
                self.acceleration = -self.brake_deceleration
            else:
                self.acceleration -= ACCELERATION * dt
        else:
            if abs(self.velocity.x) > dt * self.free_deceleration:
                self.acceleration = -copysign(self.free_deceleration, self.velocity.x)
            else:
                if dt != 0:
                    self.acceleration = -self.velocity.x / dt

        self.acceleration = max(-self.max_acceleration, min(self.acceleration, self.max_acceleration))

    def get_front_left(self):
        angle = self.get_correct_angle()

        x = self.position.x + (self.length / 2 * cos(radians(angle))) + (self.width / 2 * sin(radians(angle)))
        y = self.position.y + (self.length / 2 * sin(radians(angle))) - (self.width / 2 * cos(radians(angle)))

        return x, y

    def get_front_right(self):
        angle = self.get_correct_angle()

        x = self.position.x + (self.length / 2 * cos(radians(angle))) - (self.width / 2 * sin(radians(angle)))
        y = self.position.y + (self.length / 2 * sin(radians(angle))) + (self.width / 2 * cos(radians(angle)))

        return x, y

    def get_back_left(self):
        angle = self.get_correct_angle()

        x = self.position.x - (self.length / 2 * cos(radians(angle))) + (self.width / 2 * sin(radians(angle)))
        y = self.position.y - (self.length / 2 * sin(radians(angle))) - (self.width / 2 * cos(radians(angle)))

        return x, y

    def get_back_right(self):
        angle = self.get_correct_angle()

        x = self.position.x - (self.length / 2 * cos(radians(angle))) - (self.width / 2 * sin(radians(angle)))
        y = self.position.y - (self.length / 2 * sin(radians(angle))) + (self.width / 2 * cos(radians(angle)))

        return x, y

    def get_correct_angle(self):
        angle = -self.angle
        while angle > 360:
            angle -= 360
        while angle < -360:
            angle += 360
        return angle

    def get_sides(self):
        return [
            self.get_front_left(),
            self.get_front_right(),
            self.get_back_left(),
            self.get_back_right()
        ]
