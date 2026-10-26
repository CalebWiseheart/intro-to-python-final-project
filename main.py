import pygame as pg
from visuals import Viewport, Highlighter
from user_interface import Menu, Text, Info, Switch, Button
from models import spawn_world

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
    world = spawn_world(32)

    selected_city = (16, 16)

    viewport.set_center(selected_city)
    viewport.render_background(world)

    highlighter = Highlighter()

    wilderness_menu = Menu((250, 375), [
        Text("Wilderness", "center", (.5, .2)),
        Text("Hunter Gatherers: ", "midleft", (.1, .3)),
        Text("Last Yield: ", "midleft", (.1, .4)),
        Switch((20, 40), "midright", (.9, .3)),
        Info("midright", (.8, .3)),
        Button(render_next(), "center", (.5, .9))
    ])

    plain_menu = Menu((250, 375), [])

    field_menu = Menu((250, 375), [])

    button = Button(render_next(), "topright", (.99, .01))
    population = Info("topcenter", (.5, .01))
    ui = pg.sprite.LayeredUpdates(button, )
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
                    # tell element mouse has clicked them

                else:
                    tile_pos = viewport.screen_to_world(mouse)
                    highlighter.select(tile_pos, viewport)
                    wilderness_menu.spawn(ui, viewport.rect,"topright", viewport.normalize_pos((
                        highlighter.rect.x - 25,
                        highlighter.rect.y - wilderness_menu.rect.height * .25
                    )))

        ui.update()
        viewport.clear()
        viewport.surface.blit(highlighter.image, highlighter.rect)
        ui.draw(viewport.surface)
        pg.display.flip()
        clock.tick(FRAMERATE)

    pg.quit()

if __name__ == "__main__":
    main()
