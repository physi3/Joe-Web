import requests
from bs4 import BeautifulSoup
import tmdbsimple as tmdb
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Replace with your TMDB API key
tmdb.API_KEY = os.getenv('TMDB_KEY')

def LetterboxdListToTMDBList(listURL, withLetterboxdSlugs = False, listNameFirst = False, page = 1):
    letterboxdResponse = requests.get(f"{listURL}/page/{page}/")
    letterboxdSoup = BeautifulSoup(letterboxdResponse.content, 'html.parser')

    if (listNameFirst):
        titleElement = letterboxdSoup.find('div', class_='list-title-intro')
        if (titleElement):
            yield titleElement.find('h1', class_='title-1').text
        else:
            yield None

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

            if len(filmsWithName) != 0 and (abs(releaseYear - int(filmsWithName[0]['release_date'][:4])) >= 3):
                continue  

        if len(filmsWithName) == 0:
            continue
        elif (withLetterboxdSlugs):
            yield (filmsWithName[0], filmSlug)
        else:
            yield filmsWithName[0]
    
    if (IsPaginated(letterboxdSoup) and filmElements):
        for film in LetterboxdListToTMDBList(listURL, withLetterboxdSlugs, False, page + 1):
            yield film

def IsPaginated(letterboxdSoup):
    paginationElement = letterboxdSoup.find('div', class_='pagination')
    return paginationElement != None

def GetLetterboxdFilmYear(letterboxdSlug):
    letterboxdResponse = requests.get(f"https://letterboxd.com/film/{letterboxdSlug}")
    letterboxdSoup = BeautifulSoup(letterboxdResponse.content, 'html.parser')
    yearElement = letterboxdSoup.find('small', class_='number')
        
    if yearElement:
        return yearElement.text.strip()

def GetTMDBPoster(tmdbFilm, size="original"):
    sizes = ['w92', 'w154', 'w185', 'w342', 'w500', 'w780', 'original']
    if (size not in sizes):
        raise ValueError(f"Invalid size specified. Valid sizes are: {', '.join(sizes)}")
    return f"image.tmdb.org/t/p/{size}{tmdbFilm['poster_path']}"
