from enum import Enum
import json
from django.shortcuts import render
from django.templatetags.static import static
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

    @classmethod
    def archiveData(cls):
        raise NotImplementedError("Subclasses must implement archiveData method.")

class CurrentPersonalPage(PersonalPage):
    @classmethod
    def GetUrlPatterns(cls, prefix=""):
        return [
            path(prefix, cls.index),
            path(f"{prefix}projects/", cls.projects),
        ]

    @classmethod
    def index(cls, request):
        return render(request, "current/index.html", {
            "cv": cls.getCVJson(),
            "archive_pages": [
                PersonalPage2025.archiveData(),
            ],
        })

    @classmethod
    def projects(cls, request):
        return render(request, "current/projects.html")

    @classmethod
    def getCVJson(cls):
        with open("joewebapp/"+static('current/cv.json')) as f:
            return json.load(f)

    @classmethod
    def archiveData(cls):
        return {"year" : "current", "url" : "/archive/current/"}

class PersonalPage2025(PersonalPage):
    @classmethod
    def index(cls, request):
        return render(request, "2025/index.html")

    @classmethod
    def archiveData(cls):
        return {"year" : "2025", "url" : "/archive/2025/"}