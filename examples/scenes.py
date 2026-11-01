"""Authored demo content, deliberately outside the installed engine."""

from glyphforge import Building, Scene, Sprite, View


def street():
    scene = Scene(64, 40)
    for y in range(scene.height):
        for x in range(scene.width):
            scene.tiles[y][x] = "r" if 16 <= y <= 23 else "p"
    signs = ("BOOKS", "CAFE", "JAZZ", "VINYL", "HOTEL")
    colors = (
        (181, 108, 81),
        (107, 151, 153),
        (123, 134, 160),
        (161, 118, 141),
        (195, 176, 134),
    )
    neons = ((255, 169, 99), (102, 229, 218), (245, 133, 181), (180, 171, 255))
    for i, x in enumerate(range(5, 57, 11)):
        for side, (y0, y1) in enumerate(((4, 14), (26, 36))):
            scene.add_building(
                Building(
                    x,
                    y0,
                    x + 8,
                    y1,
                    5.95 + (i % 3) * 2.8,
                    colors[i % 5],
                    signs[(i + side) % 5],
                    neons[i % 4],
                    i * 17 + side,
                )
            )
        for y in (15, 25):
            scene.props.append(Sprite(x + 4, y, "lamp"))
            scene.add_light(x + 4, y, 7)
    scene.props.extend(
        [
            Sprite(16, 25, "tree"),
            Sprite(29, 15, "bench"),
            Sprite(24, 24.5, "person", activity="walking"),
            Sprite(36, 18, "car"),
        ]
    )
    return View(scene, x=3, y=20, angle=0.06)


def garden():
    scene = Scene(36, 28, seed=21)
    for y in range(scene.height):
        for x in range(scene.width):
            scene.tiles[y][x] = "p" if abs(y - 14) < 3 or abs(x - 18) < 2 else "g"
    for x, y in ((12, 9), (12, 19), (22, 8), (22, 20), (28, 6), (28, 22)):
        scene.props.append(Sprite(x, y, "tree"))
    scene.props.extend(
        [
            Sprite(19, 14, "fountain"),
            Sprite(15, 18, "bench"),
            Sprite(14, 10, "flowers"),
            Sprite(23, 17, "lamp"),
        ]
    )
    scene.add_light(23, 17)
    scene.add_building(Building(29, 9, 34, 19, 8, sign="GARDEN"))
    return View(scene, x=4, y=14, clock=9)
