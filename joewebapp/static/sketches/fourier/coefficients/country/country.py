import geopandas as gpd
from .. import fourier
from pathlib import Path
import numpy as np

def DefineBorder(border_file_path, discrete=False):
    geo_file = gpd.read_file(border_file_path)
    geo_file.to_crs("EPSG:3857", inplace=True)
    multi_shape = geo_file.geometry[0]
    largest_polygon = max(multi_shape.geoms, key=lambda p: p.area).exterior

    minB, maxB = largest_polygon.bounds[0:2], largest_polygon.bounds[2:4]
    center = ((minB[0] + maxB[0]) / 2, (minB[1] + maxB[1]) / 2)
    longest_side = max(maxB[0] - minB[0], maxB[1] - minB[1])

    def scale_and_center(coords):
        scaled_coords = []
        for x, y in coords:
            scaled_x = (x - center[0]) / longest_side * 2
            scaled_y = (y - center[1]) / longest_side * 2
            scaled_coords.append((scaled_x, scaled_y))
        return scaled_coords

    scaled_coords = scale_and_center(list(largest_polygon.coords))

    if discrete:
        return np.array([x + 1j * y for x, y in scaled_coords])

    def border_func(t):
        n = len(scaled_coords)
        index = (t * n) % n
        lowerIndex = int(index)
        upperIndex = (lowerIndex + 1) % n
        weight = index - lowerIndex
        x = (1 - weight) * scaled_coords[lowerIndex][0] + weight * scaled_coords[upperIndex][0]
        y = (1 - weight) * scaled_coords[lowerIndex][1] + weight * scaled_coords[upperIndex][1]

        return x + 1j * y

    return border_func

def save(name, borderfile, filename='coefficients.json'):
    file_path = Path(__file__).parent / 'borders' / borderfile
    #fourier.save_coefficients(DefineBorder(file_path), 100, name, filename)
    fourier.save_coefficients_discrete(DefineBorder(file_path, discrete=True), name, filename)