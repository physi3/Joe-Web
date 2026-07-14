from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("change-password/", views.change_password_view, name="change_password"),
    path("logout/", views.logout_view, name="logout"),
    path("film-search/", views.filmSearch, name="film_search"),
    path("person-search/", views.personSearch, name="person_search"),
    path("<str:username>/", views.profile, name="profile"),
    path("<str:username>/create-award/", views.createAward, name="create-award"),
    path("<str:username>/<str:listname>/", views.userList, name="user_list"),
    path("<str:username>/<str:listname>/members/", views.members, name="members"),
    path("<str:username>/<str:listname>/categories/", views.categories, name="categories"),
    path("<str:username>/<str:listname>/categories/create-category/", views.createCategory, name="create_category"),
    path("<str:username>/<str:listname>/categories/<slug:slug>/", views.category_detail, name="category_detail"),
    path("<str:username>/<str:listname>/categories/<slug:slug>/remove/", views.removeCategory, name="remove-category"),
    path("<str:username>/<str:listname>/categories/<slug:slug>/add-nomination/", views.addNomination, name="add-nomination"),
    path("<str:username>/<str:listname>/categories/<slug:slug>/remove-nomination/", views.removeNomination, name="remove-nomination"),
    path("<str:username>/<str:listname>/categories/<slug:slug>/vote/", views.castVote, name="cast-vote"),
    path("<str:username>/<str:listname>/invite/", views.inviteUser, name="invite_user"),
    path("<str:username>/<str:listname>/add-film/", views.addFilm, name="add_film"),
    path("<str:username>/<str:listname>/remove-film/", views.removeFilm, name="remove_film"),
    path("<str:username>/<str:listname>/watch-film/", views.watchFilm, name="watch_film"),
    path("<str:username>/<str:listname>/film-details/", views.filmModal, name="film_details"),
]