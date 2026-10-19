from dataclasses import dataclass

import pygame as pg


class Menu(pg.sprite.Sprite):
    def __init__(self, elements):
        super().__init__()

        self.elements = pg.sprite.Group(elements)
        self.normalized_rect = pg.FRect()

        self.image = None
        self.rect = pg.Rect(0, 0, 60, 90)

    def render(self):
        # fit element rects onto rect satisfying anchor
        pass

    def update(self):
        pass

@dataclass
class MenuAnchor:
    attr: str
    pos: tuple

class Text(pg.sprite.Sprite):
    def __init__(self, text, attr, pos):
        super().__init__()

        self.font = pg.font.SysFont("", 12)
        self.image = self.font.render(text, True, "white")
        self.rect = self.image.get_rect()

        self.anchor = MenuAnchor(attr, pos)
