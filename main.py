import pygame as pg
from visuals import Viewport, Highlighter
from user_interface import WildernessMenu, PlainMenu, FieldMenu, Button, Info
from models import World, City, Wilderness, Field

FRAMERATE = 60

def render_button():
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

    viewport.set_center(world.current_pos)
    viewport.render_background(world.tiles)

    highlighter = Highlighter()

    wilderness_menu = WildernessMenu()
    plain_menu = PlainMenu()
    field_menu = FieldMenu()

    def update_and_refresh():
        wilderness_menu.close()
        plain_menu.close()
        field_menu.close()
        world.update()
        viewport.render_background(world.tiles)

    button = Button(render_button(), update_and_refresh, "topright", (.99, .01))
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

                    if mouse[0] < viewport.rect.width // 2:
                        spawn_attr = "topright"
                        spawn_pos = viewport.normalize_point((
                            highlighter.rect.x - 25,
                            highlighter.rect.y - 25
                        ))
                    else:
                        spawn_attr = "topleft"
                        spawn_pos = viewport.normalize_point((
                            highlighter.rect.topright[0] + 25,
                            highlighter.rect.topright[1] - 25
                        ))

                    if type(tile) is Wilderness:
                        wilderness_menu.close()
                        wilderness_menu.spawn(ui, viewport.rect, spawn_attr, spawn_pos)
                        wilderness_menu.set_task(world.get_city(), tile_pos, tile)
                        field_menu.close()
                        plain_menu.close()
                    elif type(tile) is Field:
                        field_menu.spawn(ui, viewport.rect, spawn_attr, spawn_pos)
                        wilderness_menu.close()
                        plain_menu.close()
                    elif type(tile) is City:
                        pass
                    else:
                        plain_menu.spawn(ui, viewport.rect, spawn_attr, spawn_pos)
                        plain_menu.set_task(world.get_city(), tile_pos, tile)
                        wilderness_menu.close()
                        field_menu.close()

        ui.update()
        anchor_all(ui, viewport.rect)
        viewport.clear()
        viewport.surface.blit(highlighter.image, highlighter.rect)
        ui.draw(viewport.surface)
        pg.display.flip()
        clock.tick(FRAMERATE)

    pg.quit()

if __name__ == "__main__":
    main()
