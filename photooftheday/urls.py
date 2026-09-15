from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", auth_views.LoginView.as_view(template_name='photooftheday/login.html'), name="login"),
    path("<int:year>/<int:month>/<int:day>/", views.day, name="day"),
    path("<int:year>/<int:month>/<int:day>/upload/", views.upload, name="upload"), # type: ignore
]