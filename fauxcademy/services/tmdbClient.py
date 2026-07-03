from tmdbv3api import TMDb, Movie

from django.conf import settings

_client = None


BASE_IMAGE_URL = "https://image.tmdb.org/t/p/"
size = "w500"

def Client():
    global _client
    if _client is None:
        _client = TMDb()
        _client.api_key = "ba28fa72da38f40b03d5aad5d0b4040f"
        _client.language = settings.LANGUAGE_CODE
    return _client

def MovieClient():
    Client()
    return Movie()

def PosterURL(path, size="w500"):
    if not path:
        return None
    client = Client()
    return f"{BASE_IMAGE_URL}{size}{path}"