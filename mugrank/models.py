from pyexpat import model
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from . import letterboxdExtension as Letterboxd

class List(models.Model):
    name = models.CharField(max_length=100)
    showStats = models.BooleanField(default=True)
    filmList = models.BooleanField(default=False)

    def display_name(self):
        return f"{self.name}{' (🎥)' if (self.filmList) else ''}"

    def __str__(self):
        return self.name

    def update(self):
        return (0, 0)

class FilmList(List):
    letterboxdLID = models.CharField(max_length=100, default="")

    def update(self):
        filmMugs = FilmMug.objects.filter(list=self)
        slugs = [m.letterboxd_slug for m in filmMugs]
        slugsToAdd, slugsToRemove = Letterboxd.LetterboxdList.FromLID(self.letterboxdLID).FindDifference(slugs)
        
        for slug in slugsToRemove:
            filmMugs.get(letterboxd_slug=slug).delete()

        filmsToAddList = Letterboxd.LetterboxdList(slugsToAdd)

        for film in filmsToAddList.GetMovies():
            mug = FilmMug(
                name = film.name,
                list = self,
                letterboxd_slug = film.slug,
                poster_format_str = film.poster.formatURL
            )
            mug.save()
        
        return (len(slugsToAdd), len(slugsToRemove))

class Mug(models.Model):
    K = 32

    name = models.CharField(max_length=100, blank=True)
    image_path = models.CharField(max_length=100, blank=True)
    elo = models.IntegerField(default=1000)
    list = models.ForeignKey(List, on_delete=models.CASCADE)

    def expectedScore(self, enemy):
        return 1 / (1 + 10**((enemy.elo - self.elo)/400))
    
    def updateRatings(self, score, other):
        self.elo += round(self.K * (score - self.expectedScore(other)))

    def large_image_url(self):
        return f'{settings.MEDIA_URL}mugimages/{self.image_path}'

    def small_image_url(self):
        return f'{settings.MEDIA_URL}mugimages/{self.image_path}'
    
    def __str__(self):
        return self.name

class FilmMug(Mug):
    poster_format_str = models.CharField(max_length=100)
    letterboxd_slug = models.CharField(max_length=100, blank=True)

    def large_image_url(self):
        width = 1000
        return self.poster_format_str.format(width = width, height = width * 1.5)
    
    def small_image_url(self):
        width = 230
        return self.poster_format_str.format(width = width, height = width * 1.5)


class ListUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list = models.ForeignKey(List, on_delete=models.CASCADE)

    def findMugsToRate(self):
        mugs = Mug.objects.filter(list__exact=self.list)
        for mugOne in mugs.order_by('?'):
            for mugTwo in mugs.order_by('?'):
                if mugOne.id == mugTwo.id:
                    continue
                ratings = MugRankRecord.objects.filter(user__exact=self.user)
                if (ratings.filter(mug_one__exact=mugOne).filter(mug_two__exact=mugTwo).exists()
                    or ratings.filter(mug_one__exact=mugTwo).filter(mug_two__exact=mugOne).exists()):
                    continue
                return (mugOne, mugTwo)
        
        # Rated all mugs

        for mugOne in mugs.order_by('?'):
            for mugTwo in mugs.order_by('?'):
                if mugOne.id != mugTwo.id:
                    return (mugOne, mugTwo)

    def getContributions(self):
        recordsQuery = MugRankRecord.objects.filter(user__exact=self.user).filter(mug_one__list__exact=self.list)
        return recordsQuery.count()


    def __str__(self):
        return f"{self.list}.{self.user}"

class MugRankRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mug_one = models.ForeignKey(Mug, on_delete=models.CASCADE, related_name="mug_one")
    mug_two = models.ForeignKey(Mug, on_delete=models.CASCADE, related_name="mug_two")
    one_won = models.BooleanField()
