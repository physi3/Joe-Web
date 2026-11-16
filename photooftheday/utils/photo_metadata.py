from datetime import datetime

from PIL import ExifTags

from .geocoding import dms_to_decimal, readable_from_decimal


DATE_TAGS = ("DateTimeOriginal", "DateTimeDigitized", "DateTime")


def _text(value):
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    return str(value) if value is not None else ""


def _parse_capture_datetime(value):
    value = _text(value).strip()
    if not value:
        return None
    # EXIF's standard format is YYYY:MM:DD HH:MM:SS. Some phones append a
    # timezone, which is not needed for the date-only PhotoSubmission field.
    value = value.split("+", 1)[0].strip()
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y:%m:%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _gps_value(gps, name, default=None):
    value = gps.get(name, default)
    return _text(value).upper() if name.endswith("Ref") else value


def read_photo_metadata(image):
    """Read capture date and GPS metadata from an open Pillow image.

    Reverse geocoding is best-effort: an image remains usable when the
    geocoder is unavailable, but the returned warning tells the upload UI why
    the location is not shown.
    """
    exif = image.getexif()
    pretty_exif = {ExifTags.TAGS.get(key, key): value for key, value in exif.items()}

    captured_at = None
    for tag in DATE_TAGS:
        captured_at = _parse_capture_datetime(pretty_exif.get(tag))
        if captured_at:
            break

    latitude = longitude = None
    location = None
    warnings = []

    try:
        gps_info = exif.get_ifd(0x8825)
        gps = {ExifTags.GPSTAGS.get(key, key): value for key, value in gps_info.items()}
        if gps.get("GPSLatitude") and gps.get("GPSLongitude"):
            latitude = dms_to_decimal(gps["GPSLatitude"], _text(gps.get("GPSLatitudeRef", "N")))
            longitude = dms_to_decimal(gps["GPSLongitude"], _text(gps.get("GPSLongitudeRef", "E")))
            if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                latitude = longitude = None
    except Exception:
        latitude = longitude = None

    if latitude is None or longitude is None:
        warnings.append("No GPS location found")
    else:
        try:
            location = readable_from_decimal(latitude, longitude)
        except Exception:
            warnings.append("Location lookup failed")

    if captured_at is None:
        warnings.append("No capture date found")

    return {
        "date": captured_at.date().isoformat() if captured_at else "",
        "time": captured_at.strftime("%H:%M") if captured_at else "",
        "latitude": round(latitude, 6) if latitude is not None else "",
        "longitude": round(longitude, 6) if longitude is not None else "",
        "location": location,
        "warnings": warnings,
    }
