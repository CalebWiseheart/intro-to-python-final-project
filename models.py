import random

class World:
    def __init__(self):
        self.tiles = []
        self.city_graph = {}
        self.population = 0
        self.current_city = None

    def get_tile(self, pos) -> object:
        x, y = pos
        return self.tiles[y][x]

    def spawn(self, side_len):
        self.tiles = [[
            City() if (x, y) == (side_len // 2, side_len // 2) else
            Wilderness() if random.random() > .2 else
            None for x in range(side_len)
        ] for y in range(side_len)]

        self.current_city = (side_len // 2, side_len // 2)
        self.city_graph = {self.get_tile(self.current_city): []}
        self.population = self.get_tile(self.current_city).population

    def update(self):
        for row in self.tiles:
            for tile in row:
                if type(tile) is not City and tile is not None:
                    tile.update()

        self.population = 0
        for city in self.city_graph:
            city.update()
            self.population += city.population


class City:
    def __init__(self):
        self.population = 128
        self.age = [self.population]
        self.food_supply = 0

    def update(self):
        growth = .5
        fertility = round(self.population * growth)
        mortality = round(self.population * .1)
        delta = fertility - mortality
        self.population += delta


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
