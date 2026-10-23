from dataclasses import dataclass
import pygame as pg


class Menu(pg.sprite.Sprite):
    def __init__(self, size, elements):
        super().__init__()

        self.elements = pg.sprite.Group(elements)
        self.image = None
        self.rect = pg.Rect(0, 0, size[0], size[1])
        self.render()

    def render(self):
        self.image = pg.Surface(self.rect.size)
        self.image.fill("black")
        pg.draw.rect(self.image, "white", (
            self.rect.width * .05,
            self.rect.height * .05,
            self.rect.width * .9,
            self.rect.height * .9
        ), 10)

        for element in self.elements.sprites():
            element.anchor(self.rect)
            self.image.blit(element.image, element.rect)

    def spawn(self, group, attr, pos):
        setattr(self.rect, attr, pos)
        self.add(group)

    def update(self):
        pass

class UIElement(pg.sprite.Sprite):
    def __init__(self, attr, pos):
        super().__init__()

        self.attr = attr
        self.pos = pos

    def anchor(self, rect):
        setattr(self.rect, self.attr, (self.pos[0] * rect.width, self.pos[1] * rect.height))

class Text(UIElement):
    def __init__(self, text, attr, pos):
        super().__init__(attr, pos)

        self.font = pg.font.SysFont("", 24)
        self.image = self.font.render(text, True, "white")
        self.rect = self.image.get_rect()

class Info(Text):
    def __init__(self, attr, pos):
        super().__init__("", attr, pos)


class Button(UIElement):
    def __init__(self, image, attr, pos):
        super().__init__(attr, pos)

        self.image = image
        self.rect = self.image.get_rect()

    def update(self):
        pass

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




