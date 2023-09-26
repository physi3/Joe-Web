from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from mugrank.models import Mug, MugRankRecord, ListUser, List
from .forms import *

from django.shortcuts import redirect

import requests

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

    listuser = ListUser.objects.filter(user__exact=request.user).get(list__id=listID)
    (mugOne, mugTwo) = listuser.findMugsToRate()
    ctx = {'mugOne':mugOne, 'mugTwo':mugTwo, 'list':List.objects.get(pk=listID), 'listID':listID, 'showStats':List.objects.get(pk=listID).showStats}
    return render(request, "rank.html", ctx)

@login_required(login_url="/mugrank/login/")
def showViewPage(request, listID):
    mugList = List.objects.get(id=listID)
    orderedMugs = Mug.objects.filter(list__exact=mugList).order_by('-elo')

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
    return render(request, "profile.html", {'muglists':muglists})

@login_required(login_url="/mugrank/login/")
def addMug(request):
    invalid = False
    successful = False

    if request.method == "POST":
        form = MugCreateForm(request.POST, request.FILES)
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
    newform = MugCreateForm()
    
    return render(request, "addmug.html", {'form':newform, 'successful': successful,'invalid':invalid, 'errors': form.errors if invalid else []})


@login_required(login_url="/mugrank/login/")
def newList(request):
    invalid = False
    successful = False

    if request.method == "POST":
        form = ListCreateForm(request.POST)
        if form.is_valid():
            #Process Data
            successful = True

            newList = List(
                name = form.cleaned_data['list_name'],
            )

            newList.save()

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
    newform = ListCreateForm()
    
    return render(request, "newlist.html", {'form':newform, 'successful': successful,'invalid':invalid, 'errors': form.errors if invalid else []})
