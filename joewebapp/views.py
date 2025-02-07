from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.templatetags.static import static
from json import loads as loadJson
from .models import *

def index(request):
    return render(request, "index.html")


def getSketchesJSON():
    with open("joewebapp/"+static('sketches.json')) as f:
        return loadJson(f.read())

def sketches(request):
    sketchesJSON = getSketchesJSON()
    ctx = {"sketches" : sketchesJSON["sketches"]}
    return render(request, "sketches.html", ctx)

def getSketch(sketchName):
    sketchesJSON = getSketchesJSON()["sketches"]
    correctSketchObj = None
    for sketchObj in sketchesJSON:
        if sketchObj['urlName'] == sketchName:
            correctSketchObj = sketchObj
    return correctSketchObj

def sketchView(request, sketch):
    sketchObj = getSketch(sketch)
    ctx = {"sketch":sketchObj}

    return render(request, f"sketches/{sketchObj['templateName']}.html", ctx)

def sourceView(request, sketch):
    sketchObj = getSketch(sketch)
    source = []
    for script in sketchObj["scripts"]:
        with open("joewebapp"+static("sketches/"+script)) as file:
            source.append(file.read())

    ctx = {"sketch":sketchObj, "source":source}

    return render(request, f"sketches/source.html", ctx)

def auth(request, service):
    body = {}

    if request.user.is_authenticated:
        user = request.user
        body["username"] = user.username
    else:
        return JsonResponse({"error": "Not logged in"}, status=401)

    try:
        serviceObject = Service.objects.get(name__iexact=service)
        body["service"] = serviceObject.name
        
    except Service.DoesNotExist:
        return JsonResponse({"error": "Invalid service"}, status=400)

    body["authorized"] = user.is_superuser or UserServiceAccess.objects.filter(user=request.user, service=serviceObject).exists()
    statusCode = 200 if body["authorized"] else 403
    return JsonResponse(body, status = statusCode)
