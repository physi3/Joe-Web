import requests
import json

def reverse_geocode(latitude, longitude):
    response = requests.get(
        "https://nominatim.openstreetmap.org/reverse",
        params={
            "lat": latitude,
            "lon": longitude,
            "format": "jsonv2",
            "addressdetails": 1,
        },
        headers={
            "User-Agent": "JoeMarriageSite/1.0 (josephmarriage@gmail.com)"
        },
        timeout=5,
    )

    response.raise_for_status()
    return response.json()

def dms_to_decimal(dms, ref):
    degrees, minutes, seconds = dms

    decimal = (
        float(degrees)
        + float(minutes) / 60
        + float(seconds) / 3600
    )

    if ref in ['S', 'W']:
        decimal *= -1

    return decimal

def nominatim_to_readable(nominatim_response):
    address = nominatim_response.get("address", {})

    country = address.get("country", "")

    if country == "United Kingdom":
        country = "UK"
    if country == "United States":
        country = "USA"

    name = nominatim_response.get("name", "")

    if name == "":
        name = address.get("road", address.get("neighbourhood", address.get("suburb", "")))

    city = address.get("village", address.get("town", address.get("city", "")))

    return {
        "name": name,
        "city": city,
        "country": country,
    }

def readable_from_decimal(latitude, longitude):
    nominatim_response = reverse_geocode(latitude, longitude)

    return nominatim_to_readable(nominatim_response)