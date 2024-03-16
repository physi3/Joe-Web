from django.urls import path
from . import views
urlpatterns = [
    path('', views.index),
    path('sketches/', views.sketches),
    path('sketches/<str:sketch>/', views.sketchView),
    path('sketches/<str:sketch>/source/', views.sourceView),
]
