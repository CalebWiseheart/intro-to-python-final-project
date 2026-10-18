import random

class City:
    def __init__(self):
        self.population = 128

    def update(self):
        pass

class Wilderness:
    def __init__(self):
        pass

    def update(self):
        pass

class Field:
    def __init__(self):
        pass

    def update(self):
        pass

def spawn_world(side_len):
    return [[
        City() if (x, y) == (side_len // 2, side_len // 2) else
        Wilderness() if random.random() > .2 else
        None for x in range(side_len)
    ] for y in range(side_len)]
