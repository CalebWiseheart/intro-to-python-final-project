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
        self.text = str(getattr(self.obj, self.name))

        super().__init__(self.text, attr, pos, header)

    def update(self):
        data = str(getattr(self.obj, self.name))
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
    def __init__(self, size, attr, pos):
        super().__init__(attr, pos)
        self.count = 0
        self.image = pg.Surface((size[0], size[1]))
        self.rect = pg.Rect(0, 0, size[0], size[1])
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
        if mouse[0] < self.rect.centerx:
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
    def __init__(self, city, pos, tile):
        self.city = city
        self.pos = pos
        self.tile = tile
        last_task = self.city.get_task(self.pos)
        self.task = last_task if last_task is not None else Task.collect(tile)

    def send(self):
        if self.task.workers > 0:
            self.city.add_task(self.pos, self.task)
        else:
            self.city.remove_task(self.pos)


class TileMenu(Menu):
    def __init__(self, size, elements):
        super().__init__(size, elements)
        self.task_maker = None

    # Given the current city, the position of the selected tile, and a reference to the tile; sets its task maker to a
    # new task maker constructed using the city, position, and tile
    def set_task(self, city, pos, tile):
        self.task_maker = TaskMaker(city, pos, tile)

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
class WildernessMenu(Menu):
    def __init__(self):
        self.task_maker = None
        self.counter = Switch((20, 40), "midright", (.9, .3))
        self.to_plain = Option("Burn Down", "midleft", (.15, .6))

        super().__init__((250, 375), [
            Text("Wilderness", "center", (.5, .15)),
            Text("Hunters: ", "midleft", (.1, .3)),
            Text("Last Yield: ", "midleft", (.1, .4)),
            self.counter,
            Info(self.counter, "count", "midright", (.8, .3)),
            self.to_plain
        ])

    # Given the current city, the position of the selected tile, and a reference to the tile; sets its task maker to a
    # new task maker constructed using the city, position, and tile, then sets its counters count to the tasks workers
    def set_task(self, city, pos, tile):
        self.task_maker = TaskMaker(city, pos, tile)
        self.counter.count = self.task_maker.task.workers

    def update(self):
        self.elements.update()
        self.render()

        if self.task_maker is not None:
            if not self.to_plain.on and self.task_maker.task.type != "collect":
                self.task_maker.task = Task.collect(self.task_maker.task.tile, self.task_maker.task.workers)
            if not self.to_plain.on and self.task_maker.task.workers != self.counter.count:
                self.task_maker.task.workers = self.counter.count
            elif self.to_plain.on and self.task_maker.task.type == "collect":
                self.task_maker.task = Task.build_plain(self.task_maker.tile)
                self.counter.count = self.task_maker.task.workers

class PlainMenu(Menu):
    def __init__(self):
        self.task = None
        self.to_field = Option("Till", "center", (.5, .50))
        self.to_city = Option("Settle", "center", (.5, .75))
        self.to_field.alts.append(self.to_city)
        self.to_city.alts.append(self.to_field)
        super().__init__((200, 200), [
            Text("Plains", "center", (.5, .25)),
            self.to_field,
            self.to_city
        ])

    def set_task(self):
        pass

class FieldMenu(Menu):
    def __init__(self):
        super().__init__((250, 375), [
            Text("Field", "center", (.5, .15)),
            Text("Farmers: ", "midleft", (.1, .3)),
            Text("Last Yield: ", "midleft", (.1, .4))
        ])

    def update(self):
        pass
