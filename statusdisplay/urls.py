from django.urls import path
from . import views

urlpatterns = [
    path("status/", views.statusView),
    path("status/<str:queryUser>/", views.getLatestStatus),
    path("displayCheck/", views.displayCheck),
    path("getDisplayID/<str:displayName>/", views.getDisplayID),
    path("toggleBacklight/", views.toggleBacklight),
]
