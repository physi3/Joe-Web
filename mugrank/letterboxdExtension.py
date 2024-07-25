import requests
import regex as re
import json
from bs4 import BeautifulSoup

class LetterboxdList:
    def __init__(self, slugs, id = None, name = None):
        self.slugs = list(slugs)
        self.id = id
        self.name = name
        self.movies = []

    def GetMovies(self, cache = True):
        movies = []
        if self.MoviesValid():
            movies = self.movies
        else:
            def MovieGenerator():
                for movie in map(LetterboxdMovie.FromSlug, self.slugs):
                    yield movie
                    if cache:
                        self.movies.append(movie)
            movies = MovieGenerator()
        return movies

    def MoviesValid(self):
        movieSlugs = set([x.slug for x in self.movies])
        return movieSlugs == set(self.slugs)
    
    def FindDifference(self, slugs):
        mySlugs = set(self.slugs)
        theirSlugs = set(slugs)
        return (mySlugs - theirSlugs, theirSlugs - mySlugs)

    @classmethod
    def FromLID(cls, lid):
        return cls.FromURL(f"https://boxd.it/{lid}")

    @classmethod
    def FromURL(cls, url):
        return cls(*cls.GetListData(url))

    @classmethod
    def GetListData(cls, listURL, slugsOnly = False, page = 1):
        letterboxdResponse = requests.get(f"{listURL}/page/{page}/")
        letterboxdSoup = BeautifulSoup(letterboxdResponse.content, 'html.parser')

        listID = listTitle = None

        if not slugsOnly:
            titleElement = letterboxdSoup.find('div', class_='list-title-intro')
            if (titleElement):
                listTitle = titleElement.find('h1', class_='title-1').text

            urlElement = letterboxdSoup.find('div', class_='urlgroup')
            if (urlElement):
                listID = urlElement.find('input')['value'].split("/")[-1]

        filmElements = letterboxdSoup.find_all('li', class_='poster-container')

        def GetSlugGenerator():
            for filmElement in filmElements:
                filmSlug = filmElement.find('div', class_='film-poster')['data-film-slug']
                yield filmSlug
            
            paginationElement = letterboxdSoup.find('div', class_='pagination')

            if (paginationElement != None and filmElements):
                slugs = cls.GetListData(listURL, True, page + 1)[0]
                for film in slugs:
                    yield film

        return (GetSlugGenerator(), listID, listTitle)

class LetterboxdMovie:
    def __init__(self, slug, name, poster):
        self.slug = slug
        self.name = name
        self.poster = LetterboxdPoster(poster)
    
    @classmethod
    def FromJSON(cls, json):
        return cls(json["@id"].split("/")[-2], json["name"], json["image"])
    
    @classmethod
    def FromSlug(cls, slug):
        return cls.FromURL(f"https://letterboxd.com/film/{slug}/")

    @classmethod
    def FromURL(cls, url):
        letterboxd_response = requests.get(url)

        # Then, extract the CDATA string
        cdata_regex = r'(?s)<!\[CDATA\[(.*?)\]\]>'
        cdata_string = re.findall(cdata_regex, letterboxd_response.text)[0]

        # Next, remove comment tags and extract JSON data
        json_regex = r'(?s)\*\/(.*?)\/\*'
        json_match = re.findall(json_regex, cdata_string)[0]

        # Parse the extracted JSON string
        parsed_json = json.loads(json_match)

        return cls.FromJSON(parsed_json)

class LetterboxdPoster:
    def __init__(self, url):
        self.formatURL = self.TrimURL(url)
        self.widths = [100, 200, 230, 400, 500, 600, 1000, 2000]
    
    def GetImage(self, width):
        return requests.get(self.GetURL(width)).content

    def GetURL(self, width = 1000):
        width = self.widths[-1] if width == -1 else width
        #if width not in self.widths:
        #    raise ValueError("Given width is invalid.")
        return self.formatURL.format(width = width, height = width * 1.5)

    @staticmethod
    def TrimURL(url):
        durl = url[:-len(url.split("?")[-1])-1].split("-")
        durl[-2] = "{height:.0f}"
        durl[-4] = "{width:.0f}"
        return "-".join(durl)
