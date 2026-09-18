from enum import Enum
from django.shortcuts import render

def index(request):
    return render(request, "index.html")