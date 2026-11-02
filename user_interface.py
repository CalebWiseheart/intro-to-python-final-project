import pygame as pg

from models import Task


class UIElement(pg.sprite.Sprite):
    def __init__(self, attr, pos):
        super().__init__()

        self.attr = attr
        self.tile_pos = pos

    def anchor(self, rect):
        setattr(self.rect, self.attr, (self.tile_pos[0] * rect.width, self.tile_pos[1] * rect.height))

    def as_relative(self, point):
        x, y = point
        x -= self.rect.x
        y -= self.rect.y
        return x, y

    def click(self, mouse):
        x, y = self.as_relative(mouse)


class Menu(UIElement):
    def __init__(self, size, elements):
        super().__init__("topleft", (0, 0))

        self.elements = pg.sprite.Group(elements)
        self.image = pg.Surface(size)
        self.rect = self.image.get_rect()
        self.render()

    def render(self):
        self.image = pg.Surface(self.rect.size)
        self.image.fill("black")
        draw_border(self.image, 10)
        for element in self.elements.sprites():
            element.anchor(self.rect)
            self.image.blit(element.image, element.rect)

    def spawn(self, group, rect, attr, pos):
        self.attr = attr
        self.tile_pos = pos
        self.anchor(rect)
        self.add(group)

    def click(self, mouse):
        rel_mouse = self.as_relative(mouse)
        for element in self.elements.sprites():
            if element.rect.collidepoint(rel_mouse):
                element.click(rel_mouse)

    def update(self):
        self.elements.update()
        self.render()


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


class Select(UIElement):
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

    def click(self, mouse):
        if not self.on:
            self.on = True
            self.image.fill("gray", special_flags=pg.BLEND_RGBA_MULT)
        else:
            self.on = False
            self.image = self.src_image.copy()


class WildernessMenu(Menu):
    def __init__(self):
        self.city = None
        self.task_pos = None
        self.task = None
        self.counter = Switch((20, 40), "midright", (.9, .3))
        self.to_plain = Select("Burn Down", "midleft", (.15, .6))

        super().__init__((250, 375), [
            Text("Wilderness", "center", (.5, .15)),
            Text("Hunters: ", "midleft", (.1, .3)),
            Text("Last Yield: ", "midleft", (.1, .4)),
            self.counter,
            Info(self.counter, "count", "midright", (.8, .3)),
            self.to_plain
        ])

    def set_task(self, city, pos, tile):
        self.city = city
        self.task_pos = pos
        last_task = self.city.get_task(self.task_pos)
        self.task = last_task if last_task is not None else Task.collect(0, tile)
        self.counter.count = self.task.workers

    def close(self):
        if self.task is not None and self.task.workers > 0:
            self.city.add_task(self.task_pos, self.task)
            self.task = None
        elif self.city is not None:
            self.city.remove_task(self.task_pos)
        self.kill()

    def update(self):
        self.elements.update()
        self.render()

        if self.task is not None and not self.to_plain.on:
            self.task.workers = self.counter.count
        elif self.task is not None and self.task.type == "collect":
            self.task = Task.build_plain(self.task.tile, self.task.pos)

class PlainMenu(Menu):
    def __init__(self):
        super().__init__((200, 200), [
            Text("Plains", "center", (.5, .25)),
            Select("Till", "center", (.5, .50)),
            Select("Settle", "center", (.5, .75))
        ])


class FieldMenu(Menu):
    def __init__(self):
        super().__init__((250, 375), [
            Text("Field", "center", (.5, .15)),
            Text("Farmers: ", "midleft", (.1, .3)),
            Text("Last Yield: ", "midleft", (.1, .4))
        ])


def draw_border(image, width):
    rect = image.get_rect()
    pg.draw.rect(image, "white", (
        rect.width * .05,
        rect.height * .05,
        rect.width * .9,
        rect.height * .9
    ), width)
