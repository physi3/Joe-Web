import requests
from bs4 import BeautifulSoup
import tmdbsimple as tmdb

# Replace with your TMDB API key
tmdb.API_KEY = 'ba28fa72da38f40b03d5aad5d0b4040f'

def LetterboxdListToTMDBList(listURL, withLetterboxdSlugs = False, listNameFirst = False):
    letterboxdResponse = requests.get(listURL)
    letterboxdSoup = BeautifulSoup(letterboxdResponse.content, 'html.parser')

    if (listNameFirst):
        titleElement = letterboxdSoup.find('div', class_='list-title-intro')
        yield titleElement.find('h1', class_='title-1').text

    filmElements = letterboxdSoup.find_all('li', class_='poster-container')
    for filmElement in filmElements:
        filmName = filmElement.find('img', class_='image')['alt']
        filmSlug = filmElement.find('div', class_='film-poster')['data-film-slug']

        filmSearch = tmdb.Search().movie(query=filmName)
        filmsWithName = [film for film in filmSearch['results'] if film['title'] == filmName]

        #for TMDBFilm in filmsWithName:
        #    print(f"{TMDBFilm['title']} ({TMDBFilm['release_date']}) - {TMDBFilm['overview']}")

        if (len(filmsWithName) > 1):
            releaseYear = int(GetLetterboxdFilmYear(filmSlug))

            filmsWithName = [film for film in filmsWithName if film['release_date']]
            filmsWithName = sorted(filmsWithName, key = lambda film: abs(releaseYear - int(film['release_date'][:4])))

        if (withLetterboxdSlugs):
            yield (filmsWithName[0], filmSlug)
        else:
            yield filmsWithName[0]
        

def GetLetterboxdFilmYear(letterboxdSlug):
    letterboxdResponse = requests.get(f"https://letterboxd.com/film/{letterboxdSlug}")
    letterboxdSoup = BeautifulSoup(letterboxdResponse.content, 'html.parser')
    yearElement = letterboxdSoup.find('small', class_='number')
        
    if yearElement:
        return yearElement.text.strip()

def GetTMDBPoster(tmdbFilm, size="original"):
    sizes = ['w92', 'w154', 'w185', 'w342', 'w500', 'w780', 'original']
    if (size not in sizes):
        raise Exception("Size given is not valid")
    return f"image.tmdb.org/t/p/{size}{tmdbFilm['poster_path']}"