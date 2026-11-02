import random
import math
from dataclasses import dataclass


# Represents the underlying backend world state containing the games nonvisible objects; through a 2D list of tiles, a
# graph of adjacent cities, the total city population, and the position of the currently selected city; with methods for
# getting tiles within the world, getting a reference to the currently selected city, spawning the initial world state,
# and for updating the world once the button is pressed
class World:
    def __init__(self):
        self.tiles = []
        self.city_graph = {}
        self.population = 0
        self.current_pos = None

    # Given a position in the world returns the tile at that position
    def get_tile(self, pos) -> City | Wilderness | Field | None:
        x, y = pos
        return self.tiles[y][x]

    # Returns a reference to the city at current pos
    def get_city(self) -> City:
        x, y = self.current_pos
        return self.tiles[y][x]

    # Given the side length of the world, fills its tiles list randomly with wilderness and plains tiles up to the side
    # length with one city tile in the center, then sets the current pos to the starting city, adds the starting city to
    # the city graph, and sets the total population to the starting cities population
    def spawn(self, side_len):
        self.tiles = [[
            City() if (x, y) == (side_len // 2, side_len // 2) else
            Wilderness() if random.random() > .2 else
            None for x in range(side_len)
        ] for y in range(side_len)]

        self.current_pos = (side_len // 2, side_len // 2)
        self.city_graph = {self.get_tile(self.current_pos): []}
        self.population = self.get_city().population

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
        self.population = 32
        self.morale = 50
        self.food_supply = 0
        self.tasks = {}
        self.hunters = 0
        self.farmers = 0

    def get_task(self, pos):
        if pos in self.tasks:
            return self.tasks[pos]
        else:
            return None

    def add_task(self, pos, task):
        self.tasks[pos] = task

    def remove_task(self, pos):
        if pos in self.tasks:
            del self.tasks[pos]

    def complete_tasks(self):
        for pos in self.tasks.keys():
            task = self.tasks[pos]
            if task.type == "collect":
                self.food_supply += task.tile.collect(task.workers)
            else:
                del self.tasks[pos]

    def update(self):
        self.complete_tasks()
        decrease = 0

        if self.population > self.food_supply:
            decrease += self.population - self.food_supply
            self.food_supply = 0
            growth = .1
        else:
            demand = (self.hunters * 6 + self.farmers * 5 + (self.population - self.hunters - self.farmers) * 4)
            fullness = self.food_supply / demand
            growth = .5 + (3 - .5) * fullness if fullness < 1 else 1
            self.food_supply -= min(demand, self.food_supply)

        increase = round(self.population * growth)
        decrease = round(decrease)
        self.population += increase - decrease


@dataclass
class Task:
    workers: int
    tile: object
    type: str

    @staticmethod
    def collect(tile):
        return Task(0, tile, "collect")

    @staticmethod
    def build_plain(tile):
        return Task(128, tile, "build plain")

    @staticmethod
    def build_field(tile):
        return Task(64, tile, "build field")

    @staticmethod
    def build_city(tile):
        return Task(64, tile, "build city")

class Wilderness:
    def __init__(self):
        self.resources = 1000

    def collect(self, workers):
        taken = workers * 2
        self.resources -= taken
        return taken

    def update(self):
        self.resources += self.resources * (1 - self.resources / 1000)


class Field:
    def __init__(self):
        pass

    def update(self):
        pass
