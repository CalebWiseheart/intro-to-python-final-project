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


    def connect_city(self, city):
        pass

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

    def construct_tiles(self, labor):
        while labor.construction:
            (x, y), build_type = labor.construction.pop()

            if build_type == "build plain":
                self.tiles[y][x] = None
            elif build_type == "build field":
                self.tiles[y][x] = Field()
            else:
                settlement = City()
                self.connect_city(settlement)
                self.tiles[y][x] = settlement

            labor.remove_task((x, y))

    def update(self):
        for row in self.tiles:
            for tile in row:
                if type(tile) is not City and tile is not None:
                    tile.update()

        self.population = 0
        for city in self.city_graph:
            city.update()
            self.construct_tiles(city.labor)
            self.population += city.population


class Labor:
    def __init__(self):
        self.tasks = {}
        self.construction = []

        self.available = 0
        self.hunters = 0
        self.farmers = 0

    def get_task(self, pos):
        if pos in self.tasks:
            return self.tasks[pos]
        else:
            return None

    def get_hunger(self):
        return self.hunters * 6 + self.farmers * 5 + self.available * 4

    def add_task(self, pos, task):
        self.available -= task.workers

        is_collect = task.type == "collect"
        if is_collect and type(task.tile) is Wilderness:
            self.hunters += task.workers
        elif is_collect:
            self.farmers += task.workers

        self.tasks[pos] = task

    def remove_task(self, pos):
        if pos in self.tasks:
            task = self.tasks[pos]
            self.available += task.workers

            is_collect = task.type == "collect"
            if is_collect and type(task.tile) is Wilderness:
                self.hunters -= task.workers
            elif is_collect:
                self.farmers -= task.workers

            del self.tasks[pos]

    def complete_tasks(self):
        resources = 0

        for pos in self.tasks.keys():
            task = self.tasks[pos]
            if task.type == "collect":
                resources += task.tile.collect(task.workers)
            else:
                self.construction.append((pos, task.type))
        return resources


class City:
    def __init__(self):
        self.population = 32
        self.morale = .1
        self.fullness = 0
        self.food_supply = 0

        self.labor = Labor()

    def update(self):
        self.food_supply += self.labor.complete_tasks()

        starvation = max(self.population - self.food_supply, 0)
        disease = 0
        natural = 0
        decrease = starvation + disease + natural

        hunger = self.labor.get_hunger()
        fullness = min(self.food_supply / hunger if not starvation else 0, 1)

        self.morale += delta_morale(fullness - self.fullness, decrease / self.population)

        self.food_supply -= min(hunger, self.food_supply)

        increase = round(self.population * fullness * self.morale)
        self.population += increase - decrease


def delta_morale(delta_full, mortal):
    # delta_full: [-1, 1] mortal: [0, 1]
    return delta_full if delta_full >=0 else delta_full / 4 - mortal  # [-1.25, 1]


@dataclass
class Task:
    workers: int
    tile: object
    type: str

    @staticmethod
    def collect(tile, workers=0):
        return Task(workers, tile, "collect")

    @staticmethod
    def build_plain(tile):
        return Task(128, tile, "build plain")

    @staticmethod
    def build_field(tile):
        return Task(64, tile, "build field")

    @staticmethod
    def build_city(tile):
        return Task(64, tile, "build city")


class Resource:
    def __init__(self, cap):
        self.carry_cap = cap
        self.resources = cap
        self.produced = 0

    def collect(self, workers):
        return self.produced

    def update(self):
        self.resources += self.resources * (1 - self.resources / self.carry_cap)


class Wilderness(Resource):
    def __init__(self):
        super().__init__(10000)

    def collect(self, workers):
        self.produced = round(1.5 * workers if workers <= 64 else -1 * (workers - 64) + 6)
        return self.produced


class Field(Resource):
    def __init__(self):
        super().__init__(100000)

    def collect(self, workers):
        return self.produced
