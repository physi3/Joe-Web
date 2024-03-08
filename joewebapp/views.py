from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.templatetags.static import static
from json import loads as loadJson

def index(request):
    return render(request, "index.html")


def getSketchesJSON():
    with open("joewebapp/"+static('sketches.json')) as f:
        return loadJson(f.read())

def sketches(request):
    sketchesJSON = getSketchesJSON()
    ctx = {"sketches" : sketchesJSON["sketches"]}
    return render(request, "sketches.html", ctx)

def sketchView(request, sketch):
    sketchesJSON = getSketchesJSON()["sketches"]
    correctSketchObj = None
    for sketchObj in sketchesJSON:
        if sketchObj['urlName'] == sketch:
            correctSketchObj = sketchObj
    ctx = {"sketch":correctSketchObj}

    return render(request, f"sketches/{correctSketchObj['templateName']}.html", ctx)