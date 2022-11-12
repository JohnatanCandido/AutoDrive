from pygame.math import Vector2


class Track:
    def __init__(self, background, initial_position, initial_angle, checkpoints):
        self.background = background
        self.initial_position = initial_position
        self.initial_angle = initial_angle
        self.checkpoints = checkpoints

    def get_checkpoints(self):
        return [c for c in self.checkpoints]


tracks = [
    Track('track_1.png', Vector2(450, 300), 0, [(1365, 1280),
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
                                                (300, 2900)]),
    Track('track_2.png', Vector2(6740, 3020), 180, [(6170, 2545),
                                                    (7045, 490),
                                                    (6050, 1945),
                                                    (4610, 1205),
                                                    (5090, 600),
                                                    (5590, 1125),
                                                    (5880, 400),
                                                    (3680, 345),
                                                    (4220, 2160),
                                                    (5425, 2800),
                                                    (3533, 2485),
                                                    (2960, 400),
                                                    (2390, 2490),
                                                    (2180, 360),
                                                    (500, 430),
                                                    (660, 1360),
                                                    (1740, 1090),
                                                    (1570, 1613),
                                                    (420, 1945),
                                                    (1700, 2650),
                                                    (300, 3060)])
]
