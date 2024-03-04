from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from mugrank.models import Mug, MugRankRecord, ListUser, List, FilmMug
from .forms import *

from django.shortcuts import redirect

import requests
import hashlib
from os import environ
from . import letterboxdExtension as Letterboxd

def index(request):
    return redirect('profile/')

def expectedScore(request):
    mugOne = Mug.objects.get(id=request.GET.get('mugOne'))
    mugTwo = Mug.objects.get(id=request.GET.get('mugTwo'))

    return JsonResponse({
        'oneScore':mugOne.expectedScore(mugTwo),
        'twoScore':mugTwo.expectedScore(mugOne),
        })

@login_required(login_url="/mugrank/login/")
def showRankPage(request, listID):
    if (request.method == 'POST'):
        mugOne = Mug.objects.get(id=request.POST.get("mugOneID"))
        mugTwo = Mug.objects.get(id=request.POST.get("mugTwoID"))
        winner = int(request.POST.get("winner"))

        mugOne.updateRatings(1 - winner, mugTwo)
        mugTwo.updateRatings(winner, mugOne)

        record = MugRankRecord(
            user = request.user,
            mug_one = mugOne,
            mug_two = mugTwo,
            one_won = 1 - winner,
            )

        record.save()
        mugOne.save()
        mugTwo.save()

    mugList = List.objects.get(pk=listID)
    listuser = ListUser.objects.filter(user__exact=request.user).get(list__id=listID)
    (mugOne, mugTwo) = listuser.findMugsToRate()

    if (mugList.filmList):
        mugOne = mugOne.filmmug
        mugTwo = mugTwo.filmmug

    ctx = {'mugOne':mugOne, 'mugTwo':mugTwo, 'list':mugList, 'listID':listID, 'showStats':List.objects.get(pk=listID).showStats}
    return render(request, "rank.html", ctx)

@login_required(login_url="/mugrank/login/")
def showViewPage(request, listID):
    mugList = List.objects.get(id=listID)
    orderedMugs = Mug.objects.filter(list__exact=mugList).order_by('-elo')

    if (mugList.filmList):
        orderedMugs = [mug.filmmug for mug in orderedMugs]

    return render(request, "view.html", {'listID': listID,'mugList':mugList, 'orderedMugs':orderedMugs})

@login_required(login_url="/mugrank/login/")
def showContributionsPage(request, listID):
    mugList = List.objects.get(id=listID)
    contributors = ListUser.objects.filter(list__exact=mugList)
    contributionsDict = [(user.user, user.getContributions()) for user in contributors]
    contributionsDict.sort(key=lambda x: -x[1])

    return render(request, "contributions.html", {'listID': listID,'contribDict':contributionsDict,'mugList':mugList})

@login_required(login_url="/mugrank/login/")
def profile(request):
    listusers = ListUser.objects.filter(user__exact=request.user)
    muglists = [lu.list for lu in listusers]

    message = request.GET.get("message")
    message = message if message is not None else ""

    return render(request, "profile.html", {'muglists':muglists, 'message':message})

@login_required(login_url="/mugrank/login/")
def createMug(request):
    invalid = False
    successful = False
    successfulMessage = "Valid Mug Created"

    if request.method == "POST":
        form = MugCreateForm(request.POST, request.FILES, requesting_user = request.user)
        if form.is_valid():
            #Process Data
            successful = True

            newMug = Mug(
                name = form.cleaned_data['mug_name'],
                list = form.cleaned_data['list'],
            )

            newMug.save()

            image = form.cleaned_data['image_file']
            ext = image.name.split('.')[-1]
            with open(f'mugrank/static/mugimages/{newMug.id}.{ext}', 'wb+') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            
            newMug.image_path = f'{newMug.id}.{ext}'
            
            newMug.save()
        else:
            invalid = True
            pass
    
    #Create blank form
    newform = MugCreateForm(requesting_user = request.user)
    
    return render(request, "createmug.html", {'form':newform, 'successful': successful,'invalid':invalid, 'errors': form.errors if invalid else [], 'successfulMessage' : successfulMessage})

@login_required(login_url="/mugrank/login/")
def createLetterboxdList(request):
    invalid = False
    successful = False
    successfulMessage = "Valid 🎥 List Created"

    if request.method == "POST":
        form = LetterboxdCreateForm(request.POST)
        if form.is_valid():
            #Process Data
            successful = True

            listURL = form.cleaned_data['letterboxd_url']

            if not listURL:
                return HttpResponse("Please supply a list_url.")

            filmList = Letterboxd.LetterboxdListToTMDBList(listURL, True, True)
            listName = next(filmList)
            listName = listName if listName else "Unnamed Letterboxd List"

            newList = List(
                name = listName,
                showStats = False,
                filmList = True,
            )
            newList.save()

            listUser = ListUser(
                list = newList,
                user = request.user,
            )

            listUser.save()

            mugCount = 0
            for film in filmList:
                newMug = FilmMug(
                    name = film[0]['title'] + f" ({film[0]['release_date'][:4]})" if film[0]['release_date'] else "",
                    list = newList,
                    tmdb_id = int(film[0]['id']),
                    letterboxd_slug = film[1],
                )

                newMug.updatePosterPath()
                newMug.save()
                mugCount += 1
            successfulMessage = f"Valid 🎥 List Created with {mugCount} films"

        else:
            invalid = True
            pass
    
    #Create blank form
    newform = LetterboxdCreateForm()
    
    return render(request, "createletterboxdlist.html", {'form':newform, 'successful': successful,'invalid':invalid, 'errors': form.errors if invalid else [], 'successfulMessage' : successfulMessage})

@login_required(login_url="/mugrank/login/")
def createList(request):
    invalid = False
    successful = False
    successfulMessage = "Valid List Created"

    if request.method == "POST":
        form = ListCreateForm(request.POST)
        if form.is_valid():
            #Process Data
            successful = True

            newList = List(
                name = form.cleaned_data['list_name'],
            )

            newList.save()

            listUser = ListUser(
                list = newList,
                user = request.user,
            )

            listUser.save()

            for jsonMug in form.cleaned_data['json']["mugs"]:
                newMug = Mug(
                    name = jsonMug["name"],
                    list = newList,
                )

                newMug.save()

                image_url = jsonMug["image"]
                response = requests.get(image_url)

                #ext = image.name.split('.')[-1]
                with open(f'mugrank/static/mugimages/{newMug.id}.jpg', 'wb+') as f:
                    f.write(response.content)
                
                newMug.image_path = f'{newMug.id}.jpg'
                
                newMug.save()

        else:
            invalid = True
            pass
    
    #Create blank form
    newform = ListCreateForm(initial={'json': {"mugs":[]}})
    
    return render(request, "createlist.html", {'form':newform, 'successful': successful,'invalid':invalid, 'errors': form.errors if invalid else [], 'successfulMessage' : successfulMessage})

def listHash(listID):
    hashed = hashlib.md5(f"{environ.get('SECRET_SALT')}{listID}".encode())
    return hashed.hexdigest()[:5]

@login_required(login_url="/mugrank/login/")
def createListInvite(request):
    invalid = False
    successful = False
    successfulMessage = ""

    if request.method == "POST":
        form = InviteCreateForm(request.POST, request.FILES, requesting_user = request.user)
        if form.is_valid():
            #Process Data
            successful = True
            listID = form.cleaned_data["list"].id
            
            successfulMessage = request.build_absolute_uri(f"/mugrank/invite/{listHash(listID)}_{listID}")
        else:
            invalid = True

    #Create blank form
    newform = InviteCreateForm(requesting_user = request.user)
    
    return render(request, "createmug.html", {'form':newform, 'successful': successful,'invalid':invalid, 'errors': form.errors if invalid else [], 'successfulMessage' : successfulMessage})

@login_required(login_url="/mugrank/login/")
def acceptInvite(request, invitation):
    (hash, id) = invitation.split("_")
    if (listHash(id) == hash and (mugList := List.objects.get(id=id))):
        if ListUser.objects.filter(user=request.user, list=mugList).exists():
            return redirect("../profile/?message=You're already part of this list.")
        else:
            newListUser = ListUser(
                user = request.user,
                list = mugList,
            )
            newListUser.save()

            return redirect(f"../profile/?message=You've been added to '{mugList.name}'.")
    else:
        return redirect("../profile/?message=This invite is invalid.")
    