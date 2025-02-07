from django.urls import path
from . import views

urlpatterns = [
    path("status/", views.statusView),
    path("status/<str:queryUser>/", views.getLatestStatus),
    path("displayCheck/", views.displayCheck),
    path('displayCheckStream/', views.displayCheckAsync),
    path("getDisplayID/<str:displayName>/", views.getDisplayID),
    path("toggleBacklight/", views.toggleBacklight),
]
