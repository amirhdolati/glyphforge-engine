"""Variable-height grid ray caster, extracted from Glyph City."""

import math
from .materials import (
    FOV,
    FAR,
    EYE,
    TAU,
    LOD_KINDS,
    LOD_ART,
    LOD_ENTER_HEIGHT,
    LOD_ENTER_DISTANCE,
    LOD_EXIT_HEIGHT,
    LOD_EXIT_DISTANCE,
    WETNESS_MASK,
    REFLECTION_MASK,
    mix,
    scale,
    grain,
    cell,
    reflection_tick,
    reflection_noise,
    fog_factor,
    shadow_band,
    local_light,
    window_interior,
)
from .sprites import ART
from .interiors import room_pixel


class Renderer:
    def __init__(self, cols, rows, aspect=0.5, sprite_art=None):
        if (
            not isinstance(cols, int)
            or not isinstance(rows, int)
            or cols < 1
            or rows < 1
        ):
            raise ValueError("Resolution must contain positive integers")
        if not math.isfinite(aspect) or aspect <= 0:
            raise ValueError("Cell aspect must be positive and finite")
        self.cols, self.rows = cols, rows
        self.sprite_art = {**ART, **(sprite_art or {})}
        self.aspect = aspect
        self.fx = cols / (2 * math.tan(FOV / 2))
        self.fy = self.fx * aspect
        self.camera_x = [(c + 0.5 - cols / 2) / self.fx for c in range(cols)]
        # Keyed by the stable Prop object identity.  A renderer is recreated
        # on resize, which also clears this frame-local hysteresis state.
        self._sprite_lod = {}

    def sprite_lod(self, prop, distance):
        """Return 0 for compact distant decoration art, 1 for full art.

        The decision uses projected height and distance in world space.  The
        separate enter/exit thresholds keep a prop from changing glyph shape
        when camera motion leaves it near a single threshold.
        """
        if prop.kind not in LOD_KINDS:
            return 1
        _, _, full_height = self.sprite_art[prop.kind]
        projected_height = full_height * self.fy / max(distance, 0.35)
        previous = self._sprite_lod.get(id(prop), 1)
        if previous:
            level = (
                0
                if (projected_height < LOD_EXIT_HEIGHT or distance > LOD_EXIT_DISTANCE)
                else 1
            )
        else:
            level = (
                1
                if (
                    projected_height >= LOD_ENTER_HEIGHT
                    and distance < LOD_ENTER_DISTANCE
                )
                else 0
            )
        self._sprite_lod[id(prop)] = level
        return level

    def render(self, world):
        if not 1 <= world.camera_fov < 179:
            raise ValueError("camera_fov must be in [1, 179) degrees")
        if not (0 <= world.x < world.city.width and 0 <= world.y < world.city.height):
            raise ValueError("Camera must be inside the scene grid")
        self.world = world
        self.city = city = world.city
        cols, rows = self.cols, self.rows
        fov = math.radians(getattr(world, "camera_fov", math.degrees(FOV)))
        self.fx = cols / (2 * math.tan(fov / 2))
        self.fy = self.fx * self.aspect if hasattr(self, "aspect") else self.fx * 0.5
        self.camera_x = [(c + 0.5 - cols / 2) / self.fx for c in range(cols)]
        elevation = math.sin((world.clock - 6) / 24 * TAU)
        self.day = day = max(0, min(1, (elevation + 0.12) * 1.65))
        contrast = max(0.5, min(2.0, float(getattr(world, "night_contrast", 1.0))))
        self.night = max(0.0, min(1.0, 0.5 + (1 - day - 0.5) * contrast))
        self.sunset = max(0, 1 - abs(elevation) / 0.4) * (1 - world.cloud * 0.6)
        self.fog = mix((12, 23, 40), (105, 142, 162), day)
        self.fog = mix(self.fog, (161, 102, 107), self.sunset * 0.5)
        self.fog = mix(self.fog, (95, 117, 130), world.cloud * 0.35)
        # Keep weather atmosphere while preserving silhouettes and window edges.
        self.visibility = (
            52 if world.weather == 3 else 62 if world.weather == 2 else FAR
        )
        eye = getattr(world, "eye_height", EYE) + world.bob
        self.eye = eye
        self.horizon = horizon = (
            rows * 0.47 + world.pitch * rows + world.bob * self.fy * 0.16
        )
        ca, sa = math.cos(world.angle), math.sin(world.angle)
        rays = [(ca - sa * x, sa + ca * x) for x in self.camera_x]
        self.buffer = buf = [
            [(" ", (0, 0, 0), (0, 0, 0)) for _ in range(cols)] for _ in range(rows)
        ]
        self.depth = depths = [[FAR * 2] * cols for _ in range(rows)]
        self.surface = [[-1] * cols for _ in range(rows)]
        ground_tiles = [[None] * cols for _ in range(rows)]
        ground_coords = [[None] * cols for _ in range(rows)]
        reflection_depth = [[FAR * 2] * cols for _ in range(rows)]
        reflection_tick_value = reflection_tick(world.time)
        top = mix((4, 8, 22), (38, 83, 124), day)
        low = mix((14, 25, 43), (157, 185, 185), day)
        low = mix(low, (231, 143, 115), self.sunset * 0.8)
        top, low = (
            mix(top, self.fog, world.cloud * 0.45),
            mix(low, self.fog, world.cloud * 0.5),
        )
        flash = 0.0
        if world.weather == 2 and getattr(world, "storm_flash_enabled", True):
            pulse = math.sin(world.time * 1.71 + 13.0) ** 28
            flash = max(0.0, (pulse - 0.72) / 0.28)
            if flash:
                top = mix(top, (185, 198, 204), flash * 0.32)
                low = mix(low, (210, 205, 191), flash * 0.24)
        for r in range(rows):
            if r + 0.5 < horizon:
                ratio = max(0, min(1, (r + 0.5) / max(1, horizon)))
                bg = mix(top, low, ratio)
                for c in range(cols):
                    az = world.angle + math.atan(self.camera_x[c])
                    cloud = math.sin(
                        az * 5 + world.time * 0.008 + ratio * 6
                    ) + 0.5 * math.sin(az * 13 - ratio * 11 + world.time * 0.015)
                    ch, fg, cbg = " ", scale(bg, 1.2), bg
                    if 0.17 < ratio < 0.76 and cloud > 1.1 - world.cloud * 0.75:
                        ch = "~" if cloud > 1.15 else "."
                        fg = mix(bg, (206, 199, 186), 0.22 + 0.28 * day)
                        cbg = mix(bg, fg, 0.15)
                    elif self.night > 0.6 and world.cloud < 0.5:
                        star = grain(
                            int((az % TAU) * 135), int(ratio * 65), self.city.seed
                        )
                        if star % 127 == 0:
                            ch, fg = ("+" if star % 5 == 0 else "."), (179, 198, 222)
                    buf[r][c] = cell(ch, fg, cbg)
            else:
                dist = eye * self.fy / max(0.1, r + 0.5 - horizon)
                for c, (dx, dy) in enumerate(rays):
                    wx, wy = world.x + dx * dist, world.y + dy * dist
                    buf[r][c] = self._ground(wx, wy, dist, r, c)
                    ground_coords[r][c] = (wx, wy)
                    ix, iy = math.floor(wx), math.floor(wy)
                    if 0 <= ix < self.city.width and 0 <= iy < self.city.height:
                        ground_tiles[r][c] = city.tiles[iy][ix]
                    depths[r][c] = dist
        self._celestial(elevation)
        for c, (dx, dy) in enumerate(rays):
            hits = self._cast(world.x, world.y, dx, dy)
            # Visit near surfaces first; shade distant cells only if visible.
            for dist, side, bid, hx, hy in hits:
                b = city.buildings[bid]
                top_r = max(0, math.floor(horizon - (b.height - eye) * self.fy / dist))
                bottom_r = min(rows - 1, math.ceil(horizon + eye * self.fy / dist))
                if side == 0:
                    u = hy - b.y0 if dx > 0 else b.y1 - hy
                    span = b.y1 - b.y0
                else:
                    u = b.x1 - hx if dy > 0 else hx - b.x0
                    span = b.x1 - b.x0
                for r in range(top_r, bottom_r + 1):
                    z = eye + (horizon - r - 0.5) * dist / self.fy
                    if not 0 <= z <= b.height or dist > depths[r][c] + 0.02:
                        continue
                    bay = u % 1.65
                    level = z % 2.8
                    if (
                        int(z / 2.8) == 0
                        and 0.18 < bay < 1.48
                        and 0.62 < level < 1.78
                        and 0.22 < u < span - 0.22
                    ):
                        normal = abs(dx if side == 0 else dy)
                        tangent = (
                            (dy if dx > 0 else -dy)
                            if side == 0
                            else (-dx if dy > 0 else dx)
                        )
                        depth = min(4.5, (b.x1 - b.x0) if side == 0 else (b.y1 - b.y0))
                        ch, fg, bg, emits = self._shop_glass(
                            b,
                            u,
                            z,
                            span,
                            depth,
                            (tangent, normal, (z - eye) / dist),
                            dist,
                        )
                    else:
                        ch, fg, bg, emits = self._facade(
                            b, u, z, span, side, dist, hx, hy
                        )
                    buf[r][c] = cell(ch, fg, bg)
                    depths[r][c] = dist
                    self.surface[r][c] = bid
                    # The projected reflection lands on the ground cell below
                    # this wall pixel. Gate it by that ground material so a
                    # bright window cannot paint a reflection over grass.
                    rr = round(horizon + (z + eye) * self.fy / dist)
                    if emits and world.wet > 0.05 and 0 <= rr < rows:
                        tile = ground_tiles[rr][c]
                        strength = REFLECTION_MASK.get(tile, 0.0)
                        coords = ground_coords[rr][c]
                        if strength and coords is not None:
                            rx, ry = coords
                            if (
                                self.surface[rr][c] < 0
                                and dist < reflection_depth[rr][c]
                                and reflection_noise(
                                    rx, ry, city.seed, reflection_tick_value
                                )
                                % 5
                                != 0
                            ):
                                oldch, oldfg, oldbg = buf[rr][c]
                                alpha = world.wet * strength * (0.15 + 0.3 * self.night)
                                buf[rr][c] = cell(
                                    "|" if (rr + c) % 3 else ":",
                                    mix(oldfg, fg, alpha),
                                    mix(oldbg, fg, alpha * 0.45),
                                )
                                reflection_depth[rr][c] = dist
        self._signs(ca, sa)
        for prop in sorted(
            city.props, key=lambda p: -((p.x - world.x) ** 2 + (p.y - world.y) ** 2)
        ):
            self._sprite(prop, ca, sa)
        self._weather()
        return buf

    def _cast(self, x, y, dx, dy):
        mx, my = math.floor(x), math.floor(y)
        sx, sy = (1 if dx >= 0 else -1), (1 if dy >= 0 else -1)
        ddx, ddy = abs(1 / dx) if dx else 1e20, abs(1 / dy) if dy else 1e20
        tx = ((mx + 1 - x) if sx > 0 else (x - mx)) * ddx
        ty = ((my + 1 - y) if sy > 0 else (y - my)) * ddy
        seen, hits = set(), []
        for _ in range(self.city.width + self.city.height + 2):
            if tx < ty:
                dist, side = tx, 0
                tx += ddx
                mx += sx
            else:
                dist, side = ty, 1
                ty += ddy
                my += sy
            if (
                dist > FAR
                or not 0 <= mx < self.city.width
                or not 0 <= my < self.city.height
            ):
                break
            bid = self.city.walls[my][mx]
            if bid >= 0 and bid not in seen:
                seen.add(bid)
                hits.append((max(0.05, dist), side, bid, x + dx * dist, y + dy * dist))
        return hits

    def _ground(self, x, y, dist, r, c):
        day, night, w = self.day, self.night, self.world
        ix, iy = math.floor(x), math.floor(y)
        if (
            not 0 <= ix < self.city.width
            or not 0 <= iy < self.city.height
            or dist > FAR
        ):
            return cell(".", scale(self.fog, 0.9), scale(self.fog, 0.7))
        tile = self.city.tiles[iy][ix]
        h = grain(int(x * 9), int(y * 9), self.city.seed)
        light = local_light(self.city.glow[iy][ix], night, w.lantern and dist < 9)
        bases = {
            "r": (46, 55, 64),
            "p": (98, 97, 91),
            "g": (40, 82, 62),
            "b": (111, 94, 75),
            "w": (29, 74, 92),
        }
        base = bases[tile]
        if tile == "w":
            ripple = math.sin(x * 3 + y * 2 + w.time * 1.6)
            bg = mix(scale(base, 0.28 + 0.72 * day), self.fog, 0.18)
            fg = mix(bg, (141, 184, 184), 0.24 + 0.22 * max(0, ripple))
            ch = "~" if ripple > 0.2 else "-"
            if night > 0.5 and h % 9 < 2:
                fg = mix(fg, (226, 168, 106), 0.5)
        else:
            shade = shadow_band(x, y, self.city.seed)
            bg = scale(base, (0.27 + 0.60 * day) * shade)
            fg = scale(base, (0.58 + 0.58 * day) * shade)
            ch = "." if h % 7 == 0 else " "
            if tile == "g":
                ch = (",", "'", ".", ";")[h % 4] if h % 3 else " "
                fg = scale((74, 131, 83), 0.3 + 0.65 * day)
            elif tile in ("p", "b"):
                if x % 1 < 0.075 or y % 1 < 0.075:
                    ch = ":" if tile == "p" else "="
                elif h % 11 == 0:
                    ch = "."
            elif tile == "r":
                ax = abs(x % 24 - 12)
                ay = abs(y % 24 - 12)
                if ax < 0.09 and int(y / 1.7) % 3 < 2 and ay > 3:
                    ch = "|"
                    fg = scale((230, 190, 111), 0.5 + 0.5 * day)
                elif ay < 0.09 and int(x / 1.7) % 3 < 2 and ax > 3:
                    ch = "-"
                    fg = scale((230, 190, 111), 0.5 + 0.5 * day)
                elif (
                    (3.0 < ay < 4.1 and ax < 2.1) or (3.0 < ax < 4.1 and ay < 2.1)
                ) and h % 3:
                    ch = "="
                    fg = scale((187, 188, 168), 0.35 + 0.65 * day)
            if light:
                bg = mix(bg, (134, 97, 55), min(0.86, light * 0.78))
                fg = mix(fg, (246, 194, 112), min(0.92, light * 0.92))
            wetness = WETNESS_MASK.get(tile, 0.0)
            if w.wet > 0.03 and wetness:
                wet = w.wet * wetness
                bg = mix(bg, scale(bg, 0.62), wet)
                if h % 17 < 3:
                    ch = "-" if h % 2 else "."
                    fg = mix(fg, self.fog, wet * 0.6)
            if w.lantern and dist < 9:
                beam = max(0, 1 - dist / 9) * max(
                    0, 1 - abs(c - self.cols / 2) / (self.cols * 0.38)
                )
                fg = mix(fg, (234, 205, 140), beam * 0.6)
                bg = mix(bg, (115, 93, 49), beam * 0.35)
        fog = fog_factor(dist, self.visibility)
        return cell(ch, mix(fg, self.fog, fog * 0.72), mix(bg, self.fog, fog * 0.52))

    def _shop_glass(self, b, u, z, span, depth, direction, dist):
        panes = max(1, round(span / 3))
        pane = span / panes
        seam = min(u % pane, pane - u % pane)
        if seam < 0.035 or z < 0.29 or z > 2.055:
            return ("|" if seam < 0.035 else "-", (139, 165, 167), (25, 36, 41), False)
        ch, fg, bg = room_pixel(b.sign, span, depth, u, z, direction)
        length = math.hypot(direction[0], direction[1])
        grazing = 1 - direction[1] / max(length, 1e-6)
        reflection = 0.045 + 0.23 * grazing**3
        fg = mix(fg, (131, 174, 191), reflection)
        bg = mix(bg, self.fog, reflection)
        # A narrow continuous streak leaves most of the view transparent.
        if abs((u / pane) % 1 - (0.2 + z * 0.08)) < 0.012:
            fg = mix(fg, (203, 225, 230), 0.32)
            bg = mix(bg, (144, 185, 195), 0.12)
        fog = fog_factor(dist, self.visibility) * 0.35
        return ch, mix(fg, self.fog, fog), mix(bg, self.fog, fog), True

    def _facade(self, b, u, z, span, side, dist, hx=None, hy=None):
        day, night = self.day, self.night
        shade = (0.50 + 0.60 * day) * (1 if side else 0.86)
        shade *= shadow_band(b.x0 + u, b.y0 + z, b.seed)
        if self.world.lantern:
            shade += max(0, 1 - dist / 9) * 0.38
        base = mix(b.color, (224, 153, 101), self.sunset * 0.2)
        fg, bg = scale(base, shade), scale(base, shade * (0.30 + 0.08 * day))
        bay = u % 1.65
        story = int(z / 2.8)
        level = z % 2.8
        emits = False
        if b.height - z < 0.23:
            ch = "="
            fg = scale(base, shade * 1.35)
        elif level < 0.13:
            ch = "-"
            fg = scale(base, shade * 1.2)
        elif story == 0 and 2.15 < z < 2.5 and abs(u - span / 2) < len(b.sign) * 0.26:
            ch = "-"
            fg = scale(b.neon, 0.5)
            bg = scale(b.neon, 0.14)
            emits = True
        elif 0.18 < bay < 1.48 and 0.48 < level < 2.24:
            lit = (grain(int(u / 1.65), story, b.seed) % 100) < (18 + night * 68)
            # Thick mullions make each pane read as glass instead of one
            # continuous colored wall when a facade is close to the camera.
            edge = bay < 0.36 or bay > 1.30 or level < 0.82 or level > 1.98
            if edge:
                ch = "|" if 0.82 < level < 1.98 else "-"
                fg = scale(base, shade * 0.82)
                bg = scale((24, 29, 38), 0.8)
            elif lit:
                glow = mix((255, 190, 92), b.neon, 0.2)
                glass = mix((20, 27, 38), glow, 0.26 + 0.12 * night)
                fg = scale(glow, 0.9 + 0.3 * night)
                bg = scale(glass, 0.78)
                ch, interior = window_interior(
                    b.sign, b.seed, int(u / 1.65), story, level
                )
                # The colored background is the room behind the glass; the
                # bright glyph is furniture or a person silhouette inside it.
                bg = mix(bg, scale(interior, 0.20 + 0.12 * night), 0.32)
                fg = mix(fg, interior, 0.60 + 0.28 * night)
                if grain(int(u * 11), int(z * 11), b.seed) % 13 == 0:
                    ch = '"'
                    fg = mix(fg, (210, 230, 238), 0.72)
                emits = True
            else:
                ch = ":" if int(level * 8) % 4 else "-"
                fg = mix((49, 89, 119), self.fog, 0.25)
                bg = scale(fg, 0.25)
        elif story == 0 and abs(u - span / 2) < 0.42 and z < 1.9:
            ch = "|" if abs(u - span / 2) > 0.3 else "."
            fg = scale(b.neon, 0.45)
            bg = (14, 18, 24)
        else:
            ch = ":" if (int(z * 5) + int(u * 6)) % 5 == 0 else "."
            if dist > 28:
                ch = ":" if side else "."
        if hx is not None and hy is not None and not emits:
            ix, iy = math.floor(hx), math.floor(hy)
            if 0 <= ix < self.city.width and 0 <= iy < self.city.height:
                # Street lamps graze only the lower facade. The source stays
                # in world space, so camera motion cannot make it shimmer.
                bounce = local_light(self.city.glow[iy][ix], night) * math.exp(
                    -max(0, z) / 6
                )
                fg = mix(fg, (230, 166, 99), min(0.44, bounce * 0.34))
                bg = mix(bg, (105, 68, 43), min(0.31, bounce * 0.22))
        fog = fog_factor(dist, self.visibility, 0.72)
        if emits:
            # Lit windows are the focal points of the facade. Keep their
            # glass and interior silhouettes legible through rain and mist.
            fog *= 0.22 if dist < 24 else 0.38
        return ch, mix(fg, self.fog, fog), mix(bg, self.fog, fog * 0.62), emits

    def _signs(self, ca, sa):
        for bid, b in enumerate(self.city.buildings):
            faces = []
            w = self.world
            if w.x < b.x0:
                faces.append((b.x0, (b.y0 + b.y1) / 2, b.y1 - b.y0))
            elif w.x > b.x1:
                faces.append((b.x1, (b.y0 + b.y1) / 2, b.y1 - b.y0))
            if w.y < b.y0:
                faces.append(((b.x0 + b.x1) / 2, b.y0, b.x1 - b.x0))
            elif w.y > b.y1:
                faces.append(((b.x0 + b.x1) / 2, b.y1, b.x1 - b.x0))
            for x, y, span in faces:
                dx, dy = x - w.x, y - w.y
                z = dx * ca + dy * sa
                if z < 1 or z > 32 or span * self.fx / z < len(b.sign) + 2:
                    continue
                cx = round(self.cols / 2 + (-dx * sa + dy * ca) * self.fx / z)
                r = round(self.horizon - (2.32 - self.eye) * self.fy / z - 0.5)
                if not 0 <= r < self.rows:
                    continue
                for i, ch in enumerate(b.sign):
                    c = cx - len(b.sign) // 2 + i
                    if 0 <= c < self.cols and self.surface[r][c] == bid:
                        self.buffer[r][c] = cell(ch, b.neon, scale(b.neon, 0.13))

    def _celestial(self, elevation):
        w = self.world
        # Celestial bodies keep a world bearing as the player turns.
        sun_az = -(w.clock - 6) / 12 * math.pi
        moon = self.day < 0.2
        az = sun_az + (math.pi if moon else 0)
        delta = (az - w.angle + math.pi) % TAU - math.pi
        if abs(delta) > math.radians(w.camera_fov) / 2 + 0.1 or w.cloud > 0.65:
            return
        x = round(self.cols / 2 + math.tan(delta) * self.fx)
        height = abs(elevation) if moon else max(0, elevation)
        y = round(self.horizon - height * self.rows * 0.9 - 3)
        art = (" .-. ", "(   )", " `-' ") if moon else (" \\|/ ", "- @ -", " /|\\ ")
        color = (188, 206, 222) if moon else (255, 219, 143)
        for ar, line in enumerate(art):
            for ac, ch in enumerate(line):
                xx, yy = x + ac - 2, y + ar - 1
                if ch != " " and 0 <= xx < self.cols and 0 <= yy < self.rows:
                    self.buffer[yy][xx] = cell(ch, color, self.buffer[yy][xx][2])

    def _sprite(self, p, ca, sa):
        if not (0 <= p.x < self.city.width and 0 <= p.y < self.city.height):
            return
        if p.kind == "boat" and self.city.tiles[int(p.y)][int(p.x)] == "b":
            return
        dx, dy = p.x - self.world.x, p.y - self.world.y
        z = dx * ca + dy * sa
        if z < 0.35 or z > 48:
            return
        lateral = -dx * sa + dy * ca
        lod = self.sprite_lod(p, z)
        art, width, height = LOD_ART[p.kind] if lod == 0 else self.sprite_art[p.kind]
        if p.kind == "person":
            pose = int(self.world.time * 3 + p.phase) % 2
            if p.umbrella:
                art = (" .---. ", "/_____\\", "   o   ", "  /|\\  ", "  / \\  ")
                width = 0.95
                height = 2.05
            elif p.activity == "walking":
                art = (" o ", "/|\\", " | ", "/ |" if pose else "| \\")
            elif p.activity in ("reading", "sorting books"):
                art = (" o ", "[=]", " | ", "/ \\")
            elif p.activity == "playing music":
                art = (" o ", "/|D", " | ", "/ \\")
            elif p.activity == "taking photos":
                art = (" o ", "[o]", " | ", "/ \\")
            elif p.activity == "tending flowers":
                art = ("   ", " o_", "/|/", "/ \\")
                height = 1.2
        aw = max(map(len, art))
        ah = len(art)
        sx = self.cols / 2 + lateral * self.fx / z
        bottom = self.horizon + self.eye * self.fy / z
        pw, ph = width * self.fx / z, height * self.fy / z
        left, top = sx - pw / 2, bottom - ph
        if left >= self.cols or left + pw < 0:
            return
        for r in range(max(0, math.floor(top)), min(self.rows, math.ceil(bottom))):
            ar = min(ah - 1, max(0, int((r + 0.5 - top) / ph * ah)))
            for c in range(
                max(0, math.floor(left)), min(self.cols, math.ceil(left + pw))
            ):
                ac = min(aw - 1, max(0, int((c + 0.5 - left) / pw * aw)))
                ch = art[ar][ac] if ac < len(art[ar]) else " "
                if ch == " " or z > self.depth[r][c] + 0.05:
                    continue
                color = p.color
                if p.kind == "tree":
                    color = (96, 148, 104) if ar < 4 else (137, 105, 74)
                elif p.kind == "lamp":
                    color = (255, 209, 123) if ar < 3 else (114, 127, 139)
                elif p.kind == "fountain":
                    color = (128, 196, 215) if ar < 5 else (136, 147, 155)
                elif p.kind == "bench":
                    color = (175, 124, 81)
                elif p.kind == "rail":
                    color = (111, 135, 148)
                elif p.kind == "flowers":
                    color = (230, 139, 163) if ar < 2 else (150, 125, 103)
                elif p.kind == "person" and ar == 0:
                    color = (219, 179, 145)
                luminous = (p.kind == "lamp" and ar < 3) or (
                    p.kind == "car" and ch == "o"
                )
                factor = 1 if luminous else 0.4 + 0.6 * self.day
                color = mix(
                    scale(color, factor),
                    self.fog,
                    min(0.75, z / self.visibility) * 0.55,
                )
                bg = self.buffer[r][c][2]
                self.buffer[r][c] = cell(ch, color, mix(bg, (10, 17, 25), 0.6))
                self.depth[r][c] = z
        if (
            getattr(self.world, "show_names", False)
            and getattr(p, "name", "")
            and ph >= 2
        ):
            label = (p.name + " / " + p.activity)[:32] if z < 12 else p.name[:12]
            label_y = max(0, min(self.rows - 1, math.floor(top) - 1))
            label_x = round(sx - len(label) / 2)
            for index, char in enumerate(label):
                xx = label_x + index
                if 0 <= xx < self.cols and self.depth[label_y][xx] >= z - 0.1:
                    self.buffer[label_y][xx] = cell(char, (218, 232, 221), (17, 29, 34))
            if p.dialogue and z < 18 and label_y > 0:
                speech = '"' + p.dialogue + '"'
                speech = speech[: self.cols - 2]
                start = max(
                    0, min(self.cols - len(speech), round(sx - len(speech) / 2))
                )
                for index, char in enumerate(speech):
                    if self.depth[label_y - 1][start + index] >= z - 0.1:
                        self.buffer[label_y - 1][start + index] = cell(
                            char, (245, 211, 158), (17, 29, 34)
                        )
        if p.kind == "lamp" and self.night > 0.3:
            cx, cy = round(sx), round(top + ph * 0.2)
            for oy, ox in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                xx, yy = cx + ox, cy + oy
                if (
                    0 <= xx < self.cols
                    and 0 <= yy < self.rows
                    and self.depth[yy][xx] >= z - 0.1
                ):
                    ch, fg, bg = self.buffer[yy][xx]
                    self.buffer[yy][xx] = cell(
                        ch,
                        mix(fg, (246, 193, 111), 0.22),
                        mix(bg, (181, 121, 59), 0.18 * self.night),
                    )

    def _weather(self):
        w = self.world
        if w.rain > 0.02:
            count = int(self.cols * self.rows * w.rain * 0.06)
            tick = w.time * (21 + 8 * w.rain)
            for i in range(count):
                x = int((i * 73.13 - tick * 0.33) % self.cols)
                y = int((i * 37.79 + tick * (1 + (i % 3) * 0.25)) % self.rows)
                ch, fg, bg = self.buffer[y][x]
                self.buffer[y][x] = cell(
                    "/" if w.weather == 2 else "|", mix(fg, (151, 181, 204), 0.6), bg
                )
                if y > self.horizon + 2 and i % 7 == 0:
                    self.buffer[y][x] = cell(".", (121, 163, 183), bg)
        if w.weather == 2 and w.storm_flash_enabled and w.time % 19 < 0.12:
            for r, row in enumerate(self.buffer):
                for c, (ch, fg, bg) in enumerate(row):
                    self.buffer[r][c] = cell(
                        ch, mix(fg, (213, 223, 240), 0.5), mix(bg, (125, 145, 170), 0.3)
                    )
