import pygame as pg
from models import City, Wilderness, Field

TILE_SIDE_LEN = 50

class Viewport:
    def __init__(self):
        self.surface = pg.display.set_mode((900, 600), pg.RESIZABLE)
        pg.display.set_caption("Hunger Cycle")
        self.rect = self.surface.get_rect()
        self.offset = pg.Vector2()
        self.background = self.surface.copy()

    def render_background(self, tiles):
        self.background = pg.Surface((self.rect.width, self.rect.height))

        for y in range(len(tiles)):
            for x in range(len(tiles[y])):
                pg.draw.rect(
                    self.background,
                    get_color(tiles[y][x]),
                    (
                        x * TILE_SIDE_LEN - self.offset.x,
                        y * TILE_SIDE_LEN - self.offset.y,
                        TILE_SIDE_LEN,
                        TILE_SIDE_LEN
                    )
                )

    def set_center(self, pos):
        self.offset = (pg.Vector2(pos) * TILE_SIDE_LEN +
            pg.Vector2(TILE_SIDE_LEN, TILE_SIDE_LEN) / 2 -
            pg.Vector2(self.rect.width, self.rect.height) / 2)

    def resize(self):
        self.surface = pg.display.get_surface()
        self.rect = self.surface.get_rect()

    def clear(self):
        self.surface.blit(self.background)


class Highlighter(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pg.Surface([TILE_SIDE_LEN, TILE_SIDE_LEN], pg.SRCALPHA)
        self.rect = self.image.get_rect()
        pg.draw.rect(self.image, "white", self.rect, TILE_SIDE_LEN // 20)
        self.deselect()

    def select(self, pos):
        self.rect.topleft = pos

    def deselect(self):
        self.rect.bottomright = 0, 0


# Helper function for Viewport.renderbackground
# Given a tile, returns the color of that tile
def get_color(tile):
    return "darkgreen" if type(tile) is Wilderness else \
        "goldenrod" if type(tile) is Field else \
            "brown" if type(tile) is City else "green"

# Given a position in the world list and the center offset, returns the point of the topleft corner of the corresponding
# tile on the screen
def world_to_screen(pos, offset):
    return pg.Vector2(pos) * TILE_SIDE_LEN - offset

# Given a point on the screen and the center offset, returns the position in the world list of the corresponding tile
# that contains that point
def screen_to_world(point, offset):
    vec = (pg.Vector2(point) + offset) // TILE_SIDE_LEN
    return int(vec.x), int(vec.y)
