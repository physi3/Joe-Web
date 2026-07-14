from tmdbv3api import Person, TMDb, Movie

from django.conf import settings
from django.templatetags.static import static

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

def PersonClient():
    Client()
    return Person()

def PosterURL(path, size="w500", type="movie"):
    if not path:
        match type:
            case "movie":
                return static("fauxcademy/images/movie_generic.jpg")
            case "person":
                return static("fauxcademy/images/person_generic.jpg")
            case _:
                raise ValueError("Invalid type argument")
    client = Client()
    return f"{BASE_IMAGE_URL}{size}{path}"