"""Two contrasting authored spaces using the grid rendering backend."""

import math
from glyphforge import Building, Renderer, Scene, Sprite, View


def canal(width, height, t):
    scene = Scene(60, 32)
    for y in range(32):
        for x in range(60):
            scene.tiles[y][x] = "w" if 12 <= y <= 20 else "p"
    for i, x in enumerate(range(9, 52, 10)):
        scene.add_building(
            Building(
                x,
                3,
                x + 7,
                10,
                height=6 + i % 3 * 3,
                sign=("CAFE", "BOOKS", "JAZZ")[i % 3],
                neon=(255, 140 + i * 15, 180),
            )
        )
        scene.add_building(Building(x, 23, x + 7, 30, height=8, sign="HOTEL"))
        scene.props.append(Sprite(x, 11, "lamp"))
        scene.add_light(x, 11)
    scene.props.append(Sprite(18, 16, "boat"))
    view = View(scene, x=3, y=16, clock=19.5, time=t, angle=0.04 * math.sin(t), wet=0.9)
    return Renderer(width, height).render(view)


def monoliths(width, height, t):
    scene = Scene(48, 36)
    for y in range(36):
        for x in range(48):
            scene.tiles[y][x] = "g"
    for i in range(7):
        x = 12 + i * 4
        scene.add_building(
            Building(x, 8, x + 2, 11, height=5 + i * 1.7, color=(120, 130, 165), seed=i)
        )
        scene.add_building(
            Building(
                x, 25, x + 2, 28, height=5 + i * 1.7, color=(120, 130, 165), seed=i + 7
            )
        )
    view = View(
        scene,
        x=4,
        y=18,
        clock=5.8,
        weather=3,
        cloud=0.8,
        time=t,
        angle=0.12 * math.sin(t * 0.2),
    )
    return Renderer(width, height).render(view)
