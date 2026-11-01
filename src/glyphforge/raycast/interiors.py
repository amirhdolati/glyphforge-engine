"""Small furnished 3D rooms viewed through street-level glass."""

from functools import lru_cache
import math


def intersect(origin, direction, bounds):
    near, far, face = -math.inf, math.inf, 0
    for axis in range(3):
        lo, hi = bounds[axis], bounds[axis + 3]
        if abs(direction[axis]) < 1e-9:
            if not lo <= origin[axis] <= hi:
                return None
            continue
        a = (lo - origin[axis]) / direction[axis]
        b = (hi - origin[axis]) / direction[axis]
        if a > b:
            a, b = b, a
        if a > near:
            near, face = a, axis
        far = min(far, b)
        if near > far:
            return None
    return (near, face) if near > 1e-5 else None


@lru_cache(maxsize=512)
def furniture(sign, width, depth):
    boxes = []

    def box(x, y, z, w, d, h, color):
        boxes.append(((x, y, z, x + w, y + d, z + h), color))

    wood = (151, 91, 48)
    seat = (77, 109, 102)
    adult = sign in ("BAR", "LOUNGE", "18+")
    if adult:
        # Mature lounge dressing: velvet booths, a back bar and a small
        # abstract stage silhouette. The room reads as nightlife without
        # depicting explicit sexual activity.
        box(width * 0.08, depth - 0.8, 0, width * 0.84, 0.55, 1.0, (91, 43, 58))
        box(width * 0.13, depth - 0.97, 1.0, width * 0.74, 0.12, 0.08, (247, 112, 153))
        for x in (width * 0.22, width * 0.52, width * 0.8):
            box(x - 0.18, depth * 0.42, 0, 0.36, 0.55, 0.62, (97, 43, 67))
            box(x - 0.28, depth * 0.34, 0.58, 0.56, 0.16, 0.1, (226, 104, 145))
        box(width * 0.38, 0.55, 0, width * 0.24, 0.12, 0.12, (231, 104, 139))
        box(width * 0.48, 0.55, 0.12, 0.05, 0.05, 1.2, (204, 74, 118))
        box(width * 0.34, 0.55, 1.3, width * 0.32, 0.06, 0.06, (255, 178, 194))
        for x in (width * 0.16, width * 0.35, width * 0.65, width * 0.84):
            box(x - 0.03, depth * 0.38, 1.78, 0.06, 0.06, 0.5, (255, 181, 130))
        return tuple(boxes)
    if sign in ("BOOKS", "VINYL", "FLORA"):
        for x in (width * 0.18, width * 0.55):
            box(x, depth - 0.45, 0, width * 0.22, 0.3, 1.85, (80, 55, 37))
            for z in (0.35, 0.8, 1.25):
                for j in range(4):
                    box(
                        x + j * width * 0.05,
                        depth - 0.52,
                        z,
                        width * 0.035,
                        0.12,
                        0.3,
                        ((173, 73, 57), (177, 159, 80), (85, 142, 119), (97, 114, 167))[
                            j
                        ],
                    )
    else:
        box(width * 0.12, depth - 0.85, 0, width * 0.76, 0.55, 0.95, wood)
        box(width * 0.1, depth - 0.9, 0.95, width * 0.8, 0.65, 0.1, (222, 180, 111))
        for x in (width * 0.26, width * 0.7):
            box(x - 0.4, depth * 0.4, 0.72, 0.8, 0.65, 0.1, (218, 170, 105))
            box(x - 0.06, depth * 0.4 + 0.25, 0, 0.12, 0.12, 0.72, wood)
            box(x - 0.32, depth * 0.4 - 0.45, 0.38, 0.55, 0.4, 0.1, seat)
            box(x - 0.32, depth * 0.4 - 0.48, 0.4, 0.55, 0.07, 0.52, seat)
            box(x - 0.3, depth * 0.4 - 0.42, 0, 0.07, 0.07, 0.38, wood)
            box(x + 0.15, depth * 0.4 - 0.42, 0, 0.07, 0.07, 0.38, wood)
        if sign in ("BAR", "LOUNGE", "18+", "JAZZ"):
            for j in range(6):
                box(
                    width * (0.18 + j * 0.1),
                    depth - 0.55,
                    1.08,
                    0.12,
                    0.15,
                    0.3,
                    (96, 166, 133) if j % 2 else (192, 115, 75),
                )
    for x in (width * 0.3, width * 0.7):
        box(x - 0.025, depth * 0.5, 2.0, 0.05, 0.05, 0.65, (67, 52, 37))
        box(x - 0.22, depth * 0.5 - 0.16, 1.94, 0.44, 0.34, 0.14, (255, 218, 141))
    return tuple(boxes)


def room_pixel(sign, width, depth, u, z, direction):
    """Trace beyond the pane; walls and furniture occlude one another."""
    origin = (u, 0, z)
    # Exit planes of the room (the front opening is not a wall).
    hits = []
    for axis, plane in ((0, 0), (0, width), (1, depth), (2, 0), (2, 2.7)):
        d = direction[axis]
        if abs(d) < 1e-9:
            continue
        t = (plane - origin[axis]) / d
        if t <= 1e-5:
            continue
        point = tuple(origin[i] + direction[i] * t for i in range(3))
        if (
            -1e-6 <= point[0] <= width + 1e-6
            and -1e-6 <= point[1] <= depth + 1e-6
            and -1e-6 <= point[2] <= 2.700001
        ):
            hits.append((t, axis, point))
    if not hits:
        return " ", (174, 148, 111), (60, 48, 39)
    distance, axis, point = min(hits)
    if axis == 2 and point[2] < 0.1:
        tile = (int(point[0] * 2) + int(point[1] * 2)) % 2
        bg = (88, 68, 47) if tile else (112, 88, 61)
        ch = "." if tile else " "
        fg = (155, 125, 86)
        if sign in ("BAR", "LOUNGE", "18+"):
            bg = (84, 36, 58) if tile else (112, 45, 65)
            fg = (203, 84, 126)
    elif axis == 2:
        ch = " "
        fg = (194, 172, 128)
        bg = (100, 86, 62)
    else:
        ch = " "
        fg = (207, 172, 119)
        bg = (134, 104, 74) if axis == 1 else (96, 75, 58)
        if sign in ("BAR", "LOUNGE", "18+"):
            fg = (232, 125, 158)
            bg = (91, 37, 61) if axis == 1 else (55, 29, 52)
        if 1.25 < point[2] < 1.85 and abs(point[0] - width * 0.5) < width * 0.16:
            ch = "=" if point[2] < 1.35 or point[2] > 1.75 else "*"
            fg = (224, 182, 99)
            bg = (45, 72, 69)
    for bounds, color in furniture(sign, width, depth):
        hit = intersect(origin, direction, bounds)
        if hit and hit[0] < distance:
            distance, side = hit
            factor = (0.72, 0.87, 1.0)[side]
            bg = tuple(int(v * factor) for v in color)
            fg = tuple(min(255, int(v * 1.25)) for v in color)
            if sign in ("BAR", "LOUNGE", "18+"):
                ch = "=" if side == 2 else "O"
            elif sign in ("BOOKS", "VINYL", "FLORA"):
                ch = "#" if side == 2 else "|"
            elif sign in ("RAMEN", "CAFE", "BAKERY"):
                ch = "o" if side == 2 else "T"
            elif sign == "JAZZ":
                ch = "~" if side == 2 else "o"
            else:
                ch = "-" if side == 2 else "|"
    return ch, fg, bg
