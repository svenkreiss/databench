"""Creates an SVG of the Databench logo. Optionally also a png."""

import os
import random
import svgwrite

DATA = [
    [0, 1, 1, 1, 1, 0, 1, 1],
    [1, 1, 0, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 0, 1, 1],
    [1, 1, 0, 1, 0, 1, 1, 0],
    [0, 1, 1, 1, 1, 0, 1, 1],
    [1, 0, 1, 0, 1, 1, 0, 1],
]


def simple(svg_document, x, y, v):
    if v == 1:
        svg_document.add(svg_document.rect(insert=(x*16, y*16),
                                           size=("16px", "16px"),
                                           # rx="2px",
                                           stroke_width="1",
                                           stroke="rgb(100,100,100)",
                                           fill="rgb(100,100,100)"))


def smaller(svg_document, x, y, v):
    # from center
    distance2 = (x-3.5)**2 + (y-3.5)**2
    max_distance2 = 2 * 4**2

    if v == 1:
        size = 16.0*(1.0 - distance2/max_distance2)
        number_of_cubes = int(16**2 / (size**2))
        for i in xrange(number_of_cubes):
            xi = x*16 + 1 + random.random()*(14.0-size)
            yi = y*16 + 1 + random.random()*(14.0-size)
            sizepx = str(size)+"px"
            svg_document.add(svg_document.rect(insert=(xi, yi),
                                               size=(sizepx, sizepx),
                                               rx="2px",
                                               stroke_width="1",
                                               stroke="black",
                                               fill="black"))


def main(fn):
    svg_document = svgwrite.Drawing(filename="logo.svg",
                                    size=("128px", "128px"))
    for y, r in enumerate(DATA):
        for x, v in enumerate(r):
            fn(svg_document, x, y, v)
    print(svg_document.tostring())
    svg_document.save()

    # create a png
    # os.system('svg2png logo.svg --width=128 --height=128')


if __name__ == "__main__":
    random.seed(42)
    # main(simple)
    main(smaller)
