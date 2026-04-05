import numpy as np
from scipy import integrate
import json

def fourier_coefficient(func, k, limit = 10_000):
    def integrand(t):
        return func(t) * np.exp(-2j * np.pi * k * t)
    real_result, _ = integrate.quad(lambda t: integrand(t).real, 0, 1, limit=limit)
    imag_result, _ = integrate.quad(lambda t: integrand(t).imag, 0, 1, limit=limit)
    return [real_result, imag_result]


def save_coefficients(func, J, name, filename = 'coefficients.json'):
    fourier_coefficients = {k:fourier_coefficient(func, k) for k in range(-J, J+1)}
    out = {
        "coefficients": fourier_coefficients
        }
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    data[name] = out
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)