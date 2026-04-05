import geopandas as gpd
from .. import fourier
from pathlib import Path

file_path = Path(__file__).parent / 'britain.geojson'
britain = gpd.read_file(file_path)
britain_mainland = max(britain.geometry.iloc[0].geoms, key=lambda geom: len(geom.coords))

minB, maxB = britain_mainland.bounds[0:2], britain_mainland.bounds[2:4]
center = ((minB[0] + maxB[0]) / 2, (minB[1] + maxB[1]) / 2)
longest_side = max(maxB[0] - minB[0], maxB[1] - minB[1])

def scale_and_center(coords):
    scaled_coords = []
    for x, y in coords:
        scaled_x = (x - center[0]) / longest_side * 2
        scaled_y = (y - center[1]) / longest_side * 2
        scaled_coords.append((scaled_x, scaled_y))
    return scaled_coords

scaled_coords = scale_and_center(list(britain_mainland.coords))

def britain_func(t):
    n = len(scaled_coords)
    index = (t * n) % n
    lowerIndex = int(index)
    upperIndex = (lowerIndex + 1) % n
    weight = index - lowerIndex
    x = (1 - weight) * scaled_coords[lowerIndex][0] + weight * scaled_coords[upperIndex][0]
    y = (1 - weight) * scaled_coords[lowerIndex][1] + weight * scaled_coords[upperIndex][1]

    return x + 1j * y

def save(name='britain', filename='coefficients.json'):
    fourier.save_coefficients(britain_func, 100, name, filename)