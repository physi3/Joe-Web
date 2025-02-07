from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index),
    path('sketches/', views.sketches),
    path('sketches/<str:sketch>/', views.sketchView),
    path('sketches/<str:sketch>/source/', views.sourceView),
    path("login/", auth_views.LoginView.as_view(template_name="auth/login.html"), name="login"),
    path("auth/<str:service>/", views.auth),
]
