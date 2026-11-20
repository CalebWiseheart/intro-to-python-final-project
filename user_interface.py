import pygame as pg
from models import Task

# Base class representing a sprite that can be interacted with by the user through the mouse to set options with a
# nonfixed position; through a position normalized between 0 and 1 on an arbitrary parent rect, and the attribute of its
# sprites rect associated with that position; with methods for anchoring the sprites rect to a parent rect, and
# converting a point relative to the parent rect to a point relative to itself
class UIElement(pg.sprite.Sprite):
    def __init__(self, attr, pos):
        super().__init__()

        self.anchor_at = attr
        self.anchor_to = pos

    # Given a parent rect, sets the anchor at attribute of its rect to the anchor to position denormalized within the
    # parent rect; so that if anchor to is (0, 0) anchor at will be set to the top left corner, and if it is (1, 1) it
    # will be set to the bottom right corner
    def anchor(self, rect):
        setattr(self.rect, self.anchor_at, (self.anchor_to[0] * rect.width, self.anchor_to[1] * rect.height))

    # Given a point its last anchored rect, returns that point converted to be relative to its own rects topleft corner
    def as_relative(self, point):
        x, y = point
        x -= self.rect.x
        y -= self.rect.y
        return x, y

    # Template method to be called when the mouse interacts with the element
    def click(self, mouse):
        x, y = self.as_relative(mouse)


class Text(UIElement):
    def __init__(self, text, attr, pos, header=False):
        super().__init__(attr, pos)

        if header:
            self.font = pg.font.SysFont("", 48, True)
        else:
            self.font = pg.font.SysFont("", 24)
        self.image = self.font.render(text, True, "white")
        self.rect = self.image.get_rect()

    def render(self, text):
        self.image = self.font.render(text, True, "white")
        self.rect = self.image.get_rect()


class Info(Text):
    def __init__(self, obj, name, attr, pos,  header=False):
        self.obj = obj
        self.name = name
        self.text = str(getattr(self.obj, self.name)) if self.obj else "0"

        super().__init__(self.text, attr, pos, header)

    def update(self):
        data = str(getattr(self.obj, self.name)) if self.obj else "0"
        if data != self.text:
            self.text = data
            self.render(self.text)


class Button(UIElement):
    def __init__(self, image, onclick, attr, pos):
        super().__init__(attr, pos)

        self.src_image = image
        self.image = self.src_image.copy()
        self.rect = self.image.get_rect()
        self.state = "normal"
        self.clicked = False
        self.onclick = onclick

    def click(self, mouse):
        self.clicked = True
        self.image.fill("gray", special_flags=pg.BLEND_RGBA_MULT)

    def update(self):
        if self.clicked and not pg.mouse.get_pressed()[0]:
            self.clicked = False
            self.image = self.src_image.copy()
            self.onclick()


class Switch(UIElement):
    def __init__(self, attr, pos):
        super().__init__(attr, pos)
        self.count = 0
        self.image = pg.Surface((20, 40))
        self.rect = self.image.get_rect()
        self.render()

    def render(self):
        pg.draw.rect(self.image, "white",
                     (0, 0, self.rect.width, self.rect.height // 2), 2)
        pg.draw.rect(self.image, "white",
                     (0, self.rect.height // 2, self.rect.width, self.rect.height // 2), 2)
        pg.draw.polygon(self.image, "white", [
            (self.rect.width // 3, self.rect.height // 3),
            (self.rect.width * 2 // 3, self.rect.height // 3),
            (self.rect.width // 2, self.rect.height // 6)
        ])
        pg.draw.polygon(self.image, "white", [
            (self.rect.width // 3, self.rect.height * 2 // 3),
            (self.rect.width * 2 // 3, self.rect.height * 2 // 3),
            (self.rect.width // 2, self.rect.height * 5 // 6)
        ])

    def click(self, mouse):
        if mouse[1] < self.rect.centery:
            self.count += 16
        else:
            self.count = self.count - 16 if self.count > 0 else 0


class Option(UIElement):
    def __init__(self, text, attr, pos):
        super().__init__(attr, pos)

        self.font = pg.font.SysFont("", 24)
        text_image = self.font.render(text, True, "white")
        text_rect = text_image.get_rect()

        self.src_image = pg.Surface(text_rect.inflate(25, 25).size)
        self.rect = self.src_image.get_rect()

        self.src_image.fill("black")
        pg.draw.rect(self.src_image, "white", self.rect, 2)
        text_rect.center = self.rect.center
        self.src_image.blit(text_image, text_rect)

        self.image = self.src_image.copy()

        self.on = False
        self.alts = []

    def toggle_on(self):
        self.on = True
        self.image.fill("gray", special_flags=pg.BLEND_RGBA_MULT)

    def toggle_off(self):
        self.on = False
        self.image = self.src_image.copy()

    def click(self, mouse):
        if not self.on:
            self.toggle_on()
            for option in self.alts:
                option.toggle_off()
        else:
            self.toggle_off()


# Represents a UI element that contains and manages other UI Elements to create a menu through a group of UI elements
# with methods for drawing the menu with all of its elements anchored, and for notifying its elements when they are
# clicked, and for spawning the menu on screen
class Menu(UIElement):
    def __init__(self, size, elements):
        super().__init__("topleft", (0, 0))

        self.elements = pg.sprite.Group(elements)
        self.image = pg.Surface(size)
        self.rect = self.image.get_rect()
        self.render()

    # Draws a black background with a white border on its image, then iterates over each element and anchors it to its
    # rect and draws it to its images
    def render(self):
        self.image = pg.Surface(self.rect.size)
        self.image.fill("black")
        rect = self.image.get_rect()
        pg.draw.rect(self.image, "white", (
            rect.width * .05,
            rect.height * .05,
            rect.width * .9,
            rect.height * .9
        ), 10)

        for element in self.elements.sprites():
            element.anchor(self.rect)
            self.image.blit(element.image, element.rect)

    # Given a group of UI elements, a rect to be anchored to, and the attribute and position to anchor; sets its
    # anchor at and anchor to attributes, then anchors itself to the rect, and then adds itself to the group
    def spawn(self, group, rect, attr, pos):
        self.anchor_at = attr
        self.anchor_to = pos
        self.anchor(rect)
        self.add(group)

    # Template method for cleanup before removing itself from its groups
    def close(self):
        self.kill()

    # Given the position of the mouse assuming the mouse has been clicked; converts the position to be relative to
    # itself and then iterates over its elements and if the mouse is over an element click is called on that element
    # with the relative position
    def click(self, mouse):
        rel_mouse = self.as_relative(mouse)
        for element in self.elements.sprites():
            if element.rect.collidepoint(rel_mouse):
                element.click(rel_mouse)

    def update(self):
        self.elements.update()
        self.render()

class TaskMaker:
    def __init__(self, labor, pos, tile):
        self.labor = labor
        self.pos = pos
        self.tile = tile
        last_task = self.labor.get_task(self.pos)
        self.task = last_task if last_task is not None else Task.collect(tile)

    def send(self):
        if self.task.workers > 0:
            self.labor.add_task(self.pos, self.task)
        else:
            self.labor.remove_task(self.pos)


class TileMenu(Menu):
    def __init__(self, size, elements):
        super().__init__(size, elements)
        self.task_maker = None

    # Given the current city, the position of the selected tile, and a reference to the tile; sets its task maker to a
    # new task maker constructed using the city, position, and tile
    def set_task(self, labor, pos, tile):
        self.task_maker = TaskMaker(labor, pos, tile)

    # Updates the task within the city if the task has workers, if else ensures the task is removed from the city, and
    # then removes itself from all of its groups
    def close(self):
        if self.task_maker is not None:
            self.task_maker.send()
            self.task_maker = None
        self.kill()


# Subclass of Menu that represents a menu for a managing a task on a wilderness tile; through a reference to the current
# city, the task to give to the city, the position of the tasks tile, and hard coded ui elements; with methods for
# setting the task, city, and pos after spawning the menu, and for managing the task as the game updates, and for giving
# the city the task before removing itself from its groups
class WildernessMenu(TileMenu):
    def __init__(self):
        self.counter = Switch("midright", (.9, .3))
        self.to_plain = Option("Burn Down", "midleft", (.15, .6))
        self.last_yield = Info(None, "produced", "midright", (.8, .4))

        super().__init__((250, 375), [
            Text("Wilderness", "center", (.5, .15)),
            Text("Hunters: ", "midleft", (.1, .3)),
            Text("Last Yield: ", "midleft", (.1, .4)),
            self.counter,
            Info(self.counter, "count", "midright", (.8, .3)),
            self.last_yield,
            self.to_plain
        ])

    # Given the current city, the position of the selected tile, and a reference to the tile; sets its task maker to a
    # new task maker constructed using the city, position, and tile, then sets its counters count to the tasks workers
    def set_task(self, labor, pos, tile):
        self.task_maker = TaskMaker(labor, pos, tile)
        self.last_yield.obj = tile
        self.counter.count = self.task_maker.task.workers

    def update(self):
        self.elements.update()
        self.render()

        if self.task_maker is not None:  # denest the check for to_plain.on
            if not self.to_plain.on and self.task_maker.task.type != "collect":
                self.task_maker.task = Task.collect(self.task_maker.task.tile, self.task_maker.task.workers)
            if not self.to_plain.on and self.task_maker.task.workers != self.counter.count:
                self.task_maker.task.workers = self.counter.count
            elif self.to_plain.on and self.task_maker.task.type == "collect":
                self.task_maker.task = Task.build_plain(self.task_maker.tile)
                self.counter.count = self.task_maker.task.workers
            elif self.to_plain.on:
                self.counter.count = self.task_maker.task.workers


class FieldMenu(TileMenu):
    def __init__(self):
        self.counter = Switch("midright", (.9, .3))
        super().__init__((250, 375), [
            Text("Field", "center", (.5, .15)),
            self.counter,
            Info(self.counter, "count", "midright", (.8, .3)),
            Text("Farmers: ", "midleft", (.1, .3)),
            Text("Last Yield: ", "midleft", (.1, .4))
        ])

    def update(self):
        self.elements.update()
        self.render()

        if self.task_maker is not None and self.task_maker.task.workers != self.counter.count:
            self.task_maker.task.workers = self.counter.count


class PlainMenu(TileMenu):
    def __init__(self):
        self.workers = Info(None, "available", "center", (.5, .35))
        self.to_field = Option("Till", "center", (.5, .50))
        self.to_city = Option("Settle", "center", (.5, .75))
        self.to_field.alts.append(self.to_city)
        self.to_city.alts.append(self.to_field)
        super().__init__((200, 200), [
            Text("Plains", "center", (.5, .25)),
            self.workers,
            self.to_field,
            self.to_city
        ])

    def set_task(self, labor, pos, tile):
        self.task_maker = TaskMaker(labor, pos, tile)
        self.workers.obj = self.task_maker.task
        if self.task_maker.task.type == "build field":
            self.to_field.toggle_on()
        elif self.task_maker.task.type == "build city":
            self.to_city.toggle_on()
        else:
            self.to_field.toggle_off()
            self.to_city.toggle_off()

    def update(self):
        self.elements.update()
        self.render()

        if self.task_maker is not None:
            if self.to_field.on and self.task_maker.task.type != "build field":
                self.task_maker.task = Task.build_field(self.task_maker.task.tile)
            elif self.to_city.on and self.task_maker.task.type != "build city":
                self.task_maker.task = Task.build_city(self.task_maker.task.tile)
            elif not self.to_field.on and not self.to_city.on and self.task_maker.task.workers != 0:
                self.task_maker.task = Task.collect(self.task_maker.task.tile)


class CityMenu(Menu):
    def __init__(self, city):
        self.population = Info(city, "population", "midright", (.9, .3))
        self.free_workers = Info(city.labor, "available", "midright", (.9, .4))
        self.fullness = Info(city, "fullness", "midright", (.9, .5))
        self.morale = Info(city, "morale", "midright", (.9, .6))
        self.surplus = Info(city, "food_supply", "midright", (.9, .7))

        super().__init__((250, 375), [
            Text("City Info", "center", (.5, .15)),
            Text("Population:", "midleft", (.1, .3)),
            Text("Free Workers:", "midleft", (.1, .4)),
            Text("Fullness:", "midleft", (.1, .5)),
            Text("Morale:", "midleft", (.1, .6)),
            Text("Surplus:", "midleft", (.1, .7)),
            self.population,
            self.free_workers,
            self.fullness,
            self.morale,
            self.surplus
        ])

    def set_city(self, city):
        self.population.obj = city
        self.free_workers.obj = city.labor
        self.fullness.obj = city
