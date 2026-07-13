from typing import Any, cast

from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import AwardCategory, AwardMembership, Awards, EligibleFilm, UserEligibleFilmStatus, Nomination, NominatedPerson, Ballot
from .services.tmdbClient import MovieClient, PosterURL

import json

def index(request):
    return render(request, "fauxcademy/index.html")

@login_required(login_url='login')
def profile(request, username):
    if request.user.username != username:
        return HttpResponseForbidden("You can only view your own profile.")

    admin_awards = Awards.objects.filter(
        Q(owner=request.user) |
        Q(memberships__user=request.user, memberships__is_admin=True)
    ).distinct()

    participating_awards = Awards.objects.filter(
        memberships__user=request.user,
        memberships__is_admin=False
    ).distinct()

    return render(request, "fauxcademy/profile.html", {
        'admin_awards': admin_awards,
        'participating_awards': participating_awards,
    })

# Create your views here.
@login_required(login_url='login')
@ensure_csrf_cookie
def userList(request, username, listname):
    award = Awards.objects.filter(owner__username=username, slug=listname.lower()).first()

    if not award:
        return render(request, "404.html", status=404)

    if not award.has_access(request.user):
        return HttpResponseForbidden("You do not have permission to view this award.")

    films = EligibleFilm.objects.filter(awards=award)
    filmsCTX = [film.GetCTX() for film in films]

    for i, film in enumerate(films):
        film_status = UserEligibleFilmStatus.objects.filter(user=request.user, eligible_film=film).first()

        if film_status:
            filmsCTX[i]['unwatched'] = not film_status.is_watched
        else:
            filmsCTX[i]['unwatched'] = False  # Default to watched if no status exists

    ctx = {
        "active_page": "user_list",
        "award": award,
        "films": filmsCTX,
        "is_admin": award.is_admin(request.user),
        "members": award.memberships.select_related('user').order_by('-is_admin', 'user__username'),
    }

    return render(request, "fauxcademy/film_list.html", ctx)

@login_required(login_url='login')
@ensure_csrf_cookie
def members(request, username, listname):
    award = Awards.objects.filter(owner__username=username, slug=listname.lower()).first()

    if not award:
        return render(request, "404.html", status=404)

    if not award.has_access(request.user):
        return HttpResponseForbidden("You do not have permission to view this award.")

    ctx = {
        "active_page": "members",
        "award": award,
        "is_owner" : award.owner == request.user,
        "is_admin": award.is_admin(request.user),
        "members": award.memberships.select_related('user').order_by('-is_admin', 'user__username'),
    }

    return render(request, "fauxcademy/members.html", ctx)


@login_required(login_url='login')
@ensure_csrf_cookie
def categories(request, username, listname):
    award = Awards.objects.filter(owner__username=username, slug=listname.lower()).first()

    if not award:
        return render(request, "404.html", status=404)

    if not award.has_access(request.user):
        return HttpResponseForbidden("You do not have permission to view this award.")

    categories = AwardCategory.objects.filter(awards=award).order_by("importance", "name")
    for category in categories:
        setattr(
            category,
            "user_ballot",
            Ballot.objects.filter(
                user=request.user,
                category=category
            ).first()
        )

    ctx = {
        "active_page": "categories",
        "award": award,
        "is_admin": award.is_admin(request.user),
        "categories": categories,
    }

    return render(request, "fauxcademy/categories.html", ctx)


@login_required(login_url='login')
@ensure_csrf_cookie
def category_detail(request, username, listname, slug):
    award = Awards.objects.filter(owner__username=username, slug=listname.lower()).first()

    if not award:
        return render(request, "404.html", status=404)

    if not award.has_access(request.user):
        return HttpResponseForbidden("You do not have permission to view this award.")

    category = AwardCategory.objects.filter(awards=award, slug=slug).first()
    if not category:
        return render(request, "404.html", status=404)

    nominees = Nomination.objects.filter(category=category)
    nomineeCtx = [nominee.GetCTX() for nominee in nominees]

    for i, nominee in enumerate(nominees):
        film_status = UserEligibleFilmStatus.objects.filter(user=request.user, eligible_film=nominee.film).first()

        if film_status:
            nomineeCtx[i]['unwatched'] = not film_status.is_watched
        else:
            nomineeCtx[i]['unwatched'] = False  # Default to watched if no status exists
            
    films = EligibleFilm.objects.filter(awards=award)
    filmsCTX = [film.GetCTX() for film in films]

    ctx = {
        "award": award,
        "category": category,
        "is_admin": award.is_admin(request.user),
        "nominees": nomineeCtx,
        "films" : filmsCTX,
    }

    ballot = Ballot.objects.filter(user=request.user, category=category).first()
    ctx["user_ballot"] = ballot
    
    if ballot:
        ctx.update({
            "first_choice": ballot.first_choice.id if ballot.first_choice else None,
            "second_choice": ballot.second_choice.id if ballot.second_choice else None,
            "third_choice": ballot.third_choice.id if ballot.third_choice else None,
        })
    else:
        ctx.update({
            "first_choice": None,
            "second_choice": None,
            "third_choice": None,
        })

    return render(request, "fauxcademy/category_detail.html", ctx)


def login_view(request):
    next_url = request.GET.get('next', request.POST.get('next', '/'))
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if next_url and next_url != '/':
                return redirect(next_url)
            return redirect('profile', username=user.username)
    else:
        form = AuthenticationForm(request)

    return render(request, 'fauxcademy/login.html', {
        'form': form,
        'next': next_url,
    })


def register_view(request):
    next_url = request.GET.get('next', request.POST.get('next', '/'))
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if next_url and next_url != '/':
                return redirect(next_url)
            return redirect('profile', username=user.username)
    else:
        form = UserCreationForm()

    return render(request, 'fauxcademy/register.html', {
        'form': form,
        'next': next_url,
    })


@login_required(login_url='login')
def inviteUser(request, username, listname):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=405)

    award = Awards.objects.filter(owner__username=username, slug=listname.lower()).first()

    if not award:
        return JsonResponse({"error": "Award not found."}, status=404)

    if not award.has_access(request.user):
        return JsonResponse({"error": "You do not have permission to access this award."}, status=403)

    if not award.is_admin(request.user):
        return JsonResponse({"error": "Only admins can invite members."}, status=403)

    target_username = request.POST.get("username", "").strip()
    if not target_username:
        return JsonResponse({"error": "Username is required."}, status=400)

    target_user = get_user_model().objects.filter(username=target_username).first()
    if not target_user:
        return JsonResponse({"error": "User not found."}, status=404)

    if AwardMembership.objects.filter(award=award, user=target_user).exists():
        return JsonResponse({"error": "User is already a member of this award."}, status=400)

    membership = AwardMembership.objects.create(award=award, user=target_user, is_admin=False)
    membership.save()

    return JsonResponse({"message": "Invitation sent successfully."})


def addFilm(request, username, listname):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required."}, status=401)

        award = Awards.objects.filter(owner__username=username, slug=listname.lower()).first()

        if not award:
            return JsonResponse({"error": "Award not found."}, status=404)

        if not award.has_access(request.user):
            return JsonResponse({"error": "You do not have permission to access this award."}, status=403)

        if not award.is_admin(request.user):
            return JsonResponse({"error": "Only admins can add films."}, status=403)

        data = json.loads(request.body)
        tmdb_id = data.get("tmdb_id")

        if not tmdb_id:
            return JsonResponse({"error": "Missing 'tmdb_id' in request body."}, status=400)

        existing_film = EligibleFilm.objects.filter(tmdb_id=tmdb_id, awards=award)
        if existing_film.exists():
            return JsonResponse({"error": "Film already exists for this award."}, status=400)

        new_film = EligibleFilm(tmdb_id=tmdb_id, awards=award)
        new_film.RefreshCache()
        new_film.save()

        return JsonResponse({"message": "Film added successfully.", "film": new_film.GetCTX()})

    return JsonResponse({"error": "Invalid request method."}, status=405)

def removeFilm(request, username, listname):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required."}, status=401)

        award = Awards.objects.filter(owner__username=username, slug=listname.lower()).first()

        if not award:
            return JsonResponse({"error": "Award not found."}, status=404)

        if not award.has_access(request.user):
            return JsonResponse({"error": "You do not have permission to access this award."}, status=403)

        if not award.is_admin(request.user):
            return JsonResponse({"error": "Only admins can remove films."}, status=403)

        data = json.loads(request.body)
        tmdb_id = data.get("tmdb_id")

        if not tmdb_id:
            return JsonResponse({"error": "Missing 'tmdb_id' in request body."}, status=400)

        existing_film = EligibleFilm.objects.filter(tmdb_id=tmdb_id, awards=award)
        if not existing_film.exists():
            return JsonResponse({"error": "Film not found for this award."}, status=404)

        existing_film.delete()

        return JsonResponse({"message": "Film removed successfully."})

    return JsonResponse({"error": "Invalid request method."}, status=405)

def watchFilm(request, username, listname):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required."}, status=401)

        award = Awards.objects.filter(owner__username=username, slug=listname.lower()).first()

        if not award:
            return JsonResponse({"error": "Award not found."}, status=404)

        if not award.has_access(request.user):
            return JsonResponse({"error": "You do not have permission to access this award."}, status=403)

        data = json.loads(request.body)
        tmdb_id = data.get("tmdb_id")

        if not tmdb_id:
            return JsonResponse({"error": "Missing 'tmdb_id' in request body."}, status=400)

        film = EligibleFilm.objects.filter(tmdb_id=tmdb_id, awards=award).first()
        if not film:
            return JsonResponse({"error": "Film not found for this award."}, status=404)

        watched = data.get("watched", True)

        user_film_status, created = UserEligibleFilmStatus.objects.get_or_create(user=request.user, eligible_film=film)
        user_film_status.is_watched = watched
        user_film_status.save()

        return JsonResponse({"message": f"Film marked as { 'watched' if watched else 'unwatched' } successfully."})

    return JsonResponse({"error": "Invalid request method."}, status=405)

def addNomination(request, username, listname, slug):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=401)

    award = Awards.objects.filter(
        owner__username=username,
        slug=listname.lower()
    ).first()

    if not award:
        return JsonResponse({"error": "Award not found."}, status=404)

    if not award.has_access(request.user):
        return JsonResponse({"error": "You do not have permission to access this award."}, status=403)

    if not award.is_admin(request.user):
        return JsonResponse({"error": "Only admins can add nominations."}, status=403)

    category = AwardCategory.objects.filter(
        awards=award,
        slug=slug.lower()
    ).first()

    if not category:
        return JsonResponse({"error": "Category not found."}, status=404)

    data = json.loads(request.body)

    film_id = data.get("film")
    nominated_person_id = data.get("nominated_person")
    nominated_role = data.get("nominated_role")

    if not film_id:
        return JsonResponse({"error": "Missing 'film' in request body."}, status=400)

    film = EligibleFilm.objects.filter(
        tmdb_id=film_id,
        awards=award
    ).first()

    if not film:
        return JsonResponse({"error": "Film not found."}, status=404)

    nominated_person = None
    if nominated_person_id:
        nominated_person, created = NominatedPerson.objects.get_or_create(
            tmdb_id=nominated_person_id
        )

    nomination = Nomination.objects.create(
        category=category,
        film=film,
        nominated_person=nominated_person,
        nominated_role=nominated_role,
        nominated_by=request.user,
    )

    return JsonResponse({
        "message": "Nomination added successfully.",
        "nomination": nomination.GetCTX()
    })

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
            "poster": PosterURL(movieResult["poster_path"], size="w200", type="movie"),
        }

        movieResults.append(sanitisedResult)

        if movieResults.__len__() >= 5:
            break

    return JsonResponse({"results": movieResults})

def personSearch(request):
    query = request.GET.get("q", "").lower()
    movie_id = request.GET.get("movie_id", "")
    person_type = request.GET.get("type", "cast")

    if not movie_id:
        return JsonResponse({"results": []})

    movieClient = MovieClient()

    credits = movieClient.credits(movie_id)

    people = []

    if person_type == "cast":
        source = credits.get("cast") or []
    else:
        source = credits.get("crew") or []

    for personResult in source:
        personResult = cast(dict[str, Any], personResult)

        name = personResult.get("name", "")

        if query and query not in name.lower():
            continue

        sanitisedResult = {
            "tmdb_id": personResult["id"],
            "name": name,
            "character": personResult.get("character", "") if person_type == "cast" else "",
            "job": personResult.get("job", "") if person_type == "crew" else "",
            "profile": PosterURL(personResult["profile_path"], size="w200", type="person")
        }

        people.append(sanitisedResult)

        if len(people) >= 15:
            break

    return JsonResponse({"results": people})


def castVote(request, username, listname, slug):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=401)

    award = Awards.objects.filter(
        owner__username=username,
        slug=listname.lower()
    ).first()

    if not award:
        return JsonResponse({"error": "Award not found."}, status=404)

    if not award.has_access(request.user):
        return JsonResponse({"error": "You do not have permission to access this award."}, status=403)

    category = AwardCategory.objects.filter(
        awards=award,
        slug=slug.lower()
    ).first()

    if not category:
        return JsonResponse({"error": "Category not found."}, status=404)

    data = json.loads(request.body)

    nomination_id = data.get("nomination")
    place = data.get("place")

    if not nomination_id:
        return JsonResponse({"error": "Missing 'nomination' in request body."}, status=400)

    if place not in ["1", "2", "3"]:
        return JsonResponse({"error": "Invalid voting place."}, status=400)
    place = int(place)

    nomination = Nomination.objects.filter(
        id=nomination_id,
        category=category
    ).first()

    if not nomination:
        return JsonResponse({"error": "Nomination not found."}, status=404)

    ballot, created = Ballot.objects.get_or_create(
        user=request.user,
        category=category
    )

    # Remove this nomination from any existing position
    if ballot.first_choice == nomination:
        ballot.first_choice = None

    if ballot.second_choice == nomination:
        ballot.second_choice = None

    if ballot.third_choice == nomination:
        ballot.third_choice = None


    # Remove whatever was previously in this position
    if place == 1:
        ballot.first_choice = nomination

    elif place == 2:
        ballot.second_choice = nomination

    elif place == 3:
        ballot.third_choice = nomination


    ballot.save()

    return JsonResponse({
        "message": "Vote cast successfully.",
        "ballot": {
            "first": ballot.first_choice.id if ballot.first_choice else None,
            "second": ballot.second_choice.id if ballot.second_choice else None,
            "third": ballot.third_choice.id if ballot.third_choice else None,
        }
    })