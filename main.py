import pygame as pg
from visuals import Viewport, Highlighter
from user_interface import Menu, Text, Info, Switch, Button, Select
from models import World, City, Wilderness, Field

FRAMERATE = 60

def render_next():
    image = pg.Surface((50, 50), pg.SRCALPHA)
    pg.draw.polygon(image, "white", [(0, 0), (30, 25), (0, 50)])
    pg.draw.rect(image, "white", (35, 0, 15, 50))
    return image

def anchor_all(layers, rect):
    for element in layers.sprites():
        element.anchor(rect)

def main():
    pg.init()

    viewport = Viewport()
    world = World()
    world.spawn(32)

    viewport.set_center(world.current_city)
    viewport.render_background(world.tiles)

    highlighter = Highlighter()

    counter = Switch((20, 40), "midright", (.9, .3))

    wilderness_menu = Menu((250, 375), [
        Text("Wilderness", "center", (.5, .2)),
        Text("Hunter Gatherers: ", "midleft", (.1, .3)),
        Text("Last Yield: ", "midleft", (.1, .4)),
        counter,
        Info(counter, "count", "midright", (.8, .3)),
        Select("Option", "center", (.5, .8))
    ])

    plain_menu = Menu((250, 375), [])

    field_menu = Menu((250, 375), [])

    button = Button(render_next(), world.update, "topright", (.99, .01))
    population = Info(world, "population", "center", (.5, .05), True)
    ui = pg.sprite.LayeredUpdates(button, population)
    anchor_all(ui, viewport.rect)

    running = True
    clock = pg.Clock()

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.WINDOWRESIZED:
                viewport.resize()
                viewport.set_center((16, 16))
                viewport.render_background(world)
                anchor_all(ui, viewport.rect)
                highlighter.reselect(viewport)
            elif event.type == pg.MOUSEBUTTONDOWN:
                mouse = pg.mouse.get_pos()
                interaction = ui.get_sprites_at(mouse)
                if interaction:
                    element = interaction[0]
                    element.click(mouse)
                else:
                    tile_pos = viewport.screen_to_world(mouse)
                    highlighter.select(tile_pos, viewport)
                    tile = world.get_tile(tile_pos)

                    if type(tile) is Wilderness:
                        wilderness_menu.spawn(ui, viewport.rect,"topright", viewport.normalize_point((
                            highlighter.rect.x - 25,
                            highlighter.rect.y - wilderness_menu.rect.height * .25
                        )))
                    elif type(tile) is Field:
                        pass
                    elif type(tile) is City:
                        pass
                    else:
                        pass

        ui.update()
        if population.reanchor:
            population.reanchor = False
            population.anchor(viewport.rect)
        viewport.clear()
        viewport.surface.blit(highlighter.image, highlighter.rect)
        ui.draw(viewport.surface)
        pg.display.flip()
        clock.tick(FRAMERATE)

    pg.quit()

if __name__ == "__main__":
    main()
