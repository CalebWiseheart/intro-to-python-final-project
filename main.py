import pygame as pg
from visuals import Viewport
from models import spawn_world

FRAMERATE = 60

def main():
    pg.init()

    viewport = Viewport()
    world = spawn_world(32)

    viewport.set_center((16, 16))
    viewport.render_background(world)

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
                pass

        viewport.clear()
        pg.display.flip()
        clock.tick(FRAMERATE)

    pg.quit()

if __name__ == "__main__":
    main()
