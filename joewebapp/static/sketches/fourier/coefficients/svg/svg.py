from svgpathtools import svg2paths
from pathlib import Path
from .. import fourier

def svgFunc(svgPath):
    paths, attributes = svg2paths(svgPath)

    path = paths[0]
    xmin, xmax, ymin, ymax = path.bbox()

    def point(t):
        p = path.point(t).conjugate()
        p -= complex(xmin, ymin)
        p -= complex((xmax - xmin) / 2, -(ymax - ymin) / 2)
        longest = max(xmax - xmin, ymax - ymin)
        p /= longest * 0.5

        return p

    return point

def save():
    treblePath = Path(__file__).parent / 'svgs' / 'treble.svg'

    fourier.save_coefficients_continuous(svgFunc(treblePath), 100, "treble", "coefficients.json", include_constant=False)
