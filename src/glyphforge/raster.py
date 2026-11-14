"""Convert RGB rasters to monochrome character frames."""

ASCII_RAMP = " .,:;-~=+*oO#%@"
_ASCII_GLYPHS = tuple(
    ASCII_RAMP[round((level / 255) ** 0.65 * (len(ASCII_RAMP) - 1))]
    for level in range(256)
)
_FOREGROUND = (255, 255, 255)
_BACKGROUND = (0, 0, 0)


def sample_axis(source, cells):
    """Return two sample centers per output cell, at 25% and 75%."""
    return [
        ((4 * i + 1) * source // (4 * cells), (4 * i + 3) * source // (4 * cells))
        for i in range(cells)
    ]


def raster_to_ascii(pixels, source_width, source_height, *, columns, rows):
    """Convert row-major packed 0xRRGGBB pixels to a GlyphForge cell frame.

    Higher bits are ignored so a 32-bit framebuffer can be passed directly.
    Choose output dimensions to suit the terminal font's cell aspect ratio.
    """
    if min(source_width, source_height, columns, rows) <= 0:
        raise ValueError("Raster and frame dimensions must be positive")
    if len(pixels) != source_width * source_height:
        raise ValueError("Pixel count does not match the raster dimensions")

    xs = sample_axis(source_width, columns)
    frame = []
    for upper, lower in sample_axis(source_height, rows):
        top, bottom = upper * source_width, lower * source_width
        row = []
        for left, right in xs:
            samples = (
                pixels[top + left],
                pixels[top + right],
                pixels[bottom + left],
                pixels[bottom + right],
            )
            r = sum((pixel >> 16) & 255 for pixel in samples) // 4
            g = sum((pixel >> 8) & 255 for pixel in samples) // 4
            b = sum(pixel & 255 for pixel in samples) // 4
            luminance = (54 * r + 183 * g + 19 * b) >> 8
            row.append((_ASCII_GLYPHS[luminance], _FOREGROUND, _BACKGROUND))
        frame.append(row)
    return frame
