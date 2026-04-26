import numpy as np
from scipy import integrate
import json

def fourier_coefficient(func, k, limit = 100_000):
    def integrand(t):
        return func(t) * np.exp(-2j * np.pi * k * t)
    real_result, _ = integrate.quad(lambda t: integrand(t).real, 0, 1, limit=limit)
    imag_result, _ = integrate.quad(lambda t: integrand(t).imag, 0, 1, limit=limit)
    return [real_result, imag_result]

def save_coefficients_discrete(arr, name, filename = 'coefficients.json'):
    if arr[0] == arr[-1]:
        arr = arr[:-1]

    coeffs = np.fft.fft(arr) / len(arr)
    fourier_coefficients = {k: [coeffs[k].real, coeffs[k].imag] for k in range(-len(arr)//2, len(arr)//2)}
    save_coefficients(fourier_coefficients, name, filename)

def save_coefficients(fourier_coefficients, name, filename = 'coefficients.json', include_constant = True):
    if not include_constant:
        fourier_coefficients[0] = [0, 0]
    
    out = {
        "coefficients": fourier_coefficients
        }
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    if data.get(name) is not None:
        print(f"Overwriting existing coefficients for {name}")
        data[name]["coefficients"] = fourier_coefficients
    else:
        data[name] = out

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def save_coefficients_continuous(func, J, name, filename = 'coefficients.json', include_constant = True):
    fourier_coefficients = {k:fourier_coefficient(func, k) for k in range(-J, J+1)}
    save_coefficients(fourier_coefficients, name, filename, include_constant=include_constant)