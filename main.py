import pygame as pg
from visuals import Viewport, Highlighter, screen_to_world, world_to_screen
from models import spawn_world

FRAMERATE = 60

def main():
    pg.init()

    viewport = Viewport()
    world = spawn_world(32)

    selected_city = (16, 16)

    viewport.set_center(selected_city)
    viewport.render_background(world)

    highlighter = Highlighter()

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
                tile_pos = screen_to_world(mouse, viewport.offset)
                highlighter.select(world_to_screen(tile_pos, viewport.offset))

        viewport.clear()
        viewport.surface.blit(highlighter.image, highlighter.rect)
        pg.display.flip()
        clock.tick(FRAMERATE)

    pg.quit()

if __name__ == "__main__":
    main()
