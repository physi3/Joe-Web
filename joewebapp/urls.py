from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('sketches/', views.sketches),
    path('sketches/<str:sketch>/', views.sketchView),
    path('sketches/<str:sketch>/source/', views.sourceView),
    path("login/", views.JoeLoginView.as_view(template_name="auth/login.html", next_page="/"), name="login"),
    path("auth/<str:service>/", views.auth),
]
