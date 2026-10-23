import pygame as pg
from visuals import Viewport, Highlighter, screen_to_world, world_to_screen
from user_interface import Menu, Text, Switch, Button
from models import spawn_world

FRAMERATE = 60

def render_next():
    image = pg.Surface((50, 50), pg.SRCALPHA)
    pg.draw.polygon(image, "white", [(0, 0), (30, 25), (0, 50)])
    pg.draw.rect(image, "white", (35, 0, 15, 50))
    return image

def main():
    pg.init()

    viewport = Viewport()
    world = spawn_world(32)

    selected_city = (16, 16)

    viewport.set_center(selected_city)
    viewport.render_background(world)

    highlighter = Highlighter()

    tile_info = Menu((250, 250 * 1.5), [
        Text("Menu", "center", (.5, .2)),
        Text("Workers: ", "midleft", (.1, .3)),
        Text("Yield: ", "midleft", (.1, .4)),
        Switch((20, 40), "midright", (.9, .3))
    ])
    button = Button(render_next(), "topright", (.99, .01))
    button.anchor(viewport.rect)
    ui = pg.sprite.Group(button)

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
            elif event.type == pg.MOUSEBUTTONDOWN:
                mouse = pg.mouse.get_pos()
                # if mouse collides with ui send message to menu
                # else find tile and spawn info menu
                tile_pos = screen_to_world(mouse, viewport.offset)
                highlighter.select(world_to_screen(tile_pos, viewport.offset))
                tile_info.spawn(ui, "topright", (
                    highlighter.rect.x - 20,
                    highlighter.rect.y - tile_info.rect.height * .25
                ))

        viewport.clear()
        viewport.surface.blit(highlighter.image, highlighter.rect)
        ui.draw(viewport.surface)
        pg.display.flip()
        clock.tick(FRAMERATE)

    pg.quit()

if __name__ == "__main__":
    main()
