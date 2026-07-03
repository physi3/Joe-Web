from typing import Any, cast

from django.http import JsonResponse
from django.shortcuts import render
from .models import Awards, EligibleFilm
from .services.tmdbClient import MovieClient, PosterURL

import json

# Create your views here.
def userList(request, username, listname):
    award = Awards.objects.filter(owner__username=username, name=listname)

    if not award.exists():
        return render(request, "404.html", status=404)

    ctx = {
        "award": award.first(),
        "films": [film.GetCTX() for film in EligibleFilm.objects.filter(awards=award.first())],
    }

    return render(request, "film_list.html", ctx)

def addFilm(request, username, listname):
    if request.method == "POST":
        award = Awards.objects.filter(owner__username=username, name=listname)

        if not award.exists():
            return JsonResponse({"error": "Award not found."}, status=404)

        data = json.loads(request.body)
        tmdb_id = data.get("tmdb_id")

        if not tmdb_id:
            return JsonResponse({"error": "Missing 'tmdb_id' in request body."}, status=400)

        # Check if the film already exists for this award
        existing_film = EligibleFilm.objects.filter(tmdb_id=tmdb_id, awards=award.first())
        if existing_film.exists():
            return JsonResponse({"error": "Film already exists for this award."}, status=400)

        # Create a new EligibleFilm instance
        new_film = EligibleFilm(tmdb_id=tmdb_id, awards=award.first())
        new_film.RefreshCache()  # Refresh cache to populate cached fields
        new_film.save()

        return JsonResponse({"message": "Film added successfully.", "film": new_film.GetCTX()})

    return JsonResponse({"error": "Invalid request method."}, status=405)

def filmSearch(request):
    query = request.GET.get("q", "")

    movieClient = MovieClient()
    results = movieClient.search(query)

    movieResults = []

    for movieResult in results:
        movieResult = cast(dict[str, Any], movieResult)
        
        sanitisedResult = {
            "tmdb_id": movieResult["id"],
            "title": movieResult["title"],
            "year": movieResult["release_date"].split("-")[0] if movieResult.get("release_date") else "",
            "poster": PosterURL(movieResult["poster_path"], size="w200") if movieResult.get("poster_path") else None,
        }

        movieResults.append(sanitisedResult)

        if movieResults.__len__() >= 5:
            break

    return JsonResponse({"results": movieResults})