from enum import Enum
from django.shortcuts import render
from django.urls import path

class PersonalPage:
    @classmethod
    def GetUrlPatterns(cls, prefix=""):
        return [
            path(prefix, cls.index),
        ]

    @classmethod
    def index(cls, request):
        raise NotImplementedError("Subclasses must implement index method.")

class PersonalPage2025(PersonalPage):
    @classmethod
    def index(cls, request):
        return render(request, "2025/index.html")