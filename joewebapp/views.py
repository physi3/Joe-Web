from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Sketch

def index(request):
    return render(request, "index.html")

def sketches(request):
    ctx = {"sketches" : Sketch.objects.all()}
    return render(request, "sketches.html", ctx)

def sketchView(request, sketch):
    ctx = {"sketch":sketch}
    return render(request, f"sketches/{Sketch.objects.get(name=sketch).templateName}.html", ctx)