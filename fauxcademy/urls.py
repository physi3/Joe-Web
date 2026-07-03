from django.urls import path
from . import views

urlpatterns = [
    path("<str:username>/<str:listname>/", views.userList, name="user_list"),
    path("<str:username>/<str:listname>/add-film/", views.addFilm, name="add_film"),
    path("film-search/", views.filmSearch, name="film_search"),
]