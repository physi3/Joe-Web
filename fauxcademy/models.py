from .services.tmdbClient import MovieClient, PosterURL

from django.db import models
from django.contrib.auth.models import User
from django.db.models.functions import Lower
from django.core.exceptions import ValidationError

# Create your models here.
class Awards(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    class Meta:
        constraints = [
            models.UniqueConstraint(Lower("name"), "owner", name="unique_award_owner_name"),
        ]
    
    def clean(self):
        if self.owner and self.name:
            qs = Awards.objects.filter(owner=self.owner, name__iexact=self.name)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({'name': 'You already have an award with this name.'})

class EligibleFilm(models.Model):
    tmdb_id = models.IntegerField()
    awards = models.ForeignKey(Awards, on_delete=models.CASCADE)
    
    cache_LOD = models.IntegerField(default=0, help_text="Cache Level of Detail: 0 = no cache, 1 = title only, 2 = basic info")

    cached_title = models.CharField(max_length=200, blank=True)

    cached_tagline = models.CharField(max_length=200, blank=True)
    cached_overview = models.TextField(blank=True)
    cached_poster_path = models.CharField(max_length=200, blank=True)
    cached_release_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Film {self.cached_title} for Award {self.awards.name}"

    def RefreshCache(self, LOD = 2):
        tmdbMovie = self.tmdbMovie()

        if LOD >= 1:
            self.cached_title = tmdbMovie.get("title", self.cached_title)
        if LOD >= 2:
            self.cached_tagline = tmdbMovie.get("tagline", self.cached_tagline)
            self.cached_overview = tmdbMovie.get("overview", self.cached_overview)
            self.cached_poster_path = tmdbMovie.get("poster_path", self.cached_poster_path)
            self.cached_release_date = tmdbMovie.get("release_date", self.cached_release_date)

        self.cache_LOD = LOD
        self.save()

    def GetCTX(self, LOD = 2):
        if self.cache_LOD < LOD:
            self.RefreshCache(LOD)

        ctx = {
            "tmdb_id": self.tmdb_id,
            "title": self.cached_title,
            "tagline": self.cached_tagline,
            "overview": self.cached_overview,
            "poster_url": PosterURL(self.cached_poster_path),
            "release_date": self.cached_release_date,
        }

        return ctx

    def tmdbMovie(self):
        movie_client = MovieClient()
        return movie_client.details(self.tmdb_id)