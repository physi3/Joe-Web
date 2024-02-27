from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.index),
    path("expectedscore/", views.expectedScore),
    path("rank/<int:listID>/", views.showRankPage),
    path("view/<int:listID>/", views.showViewPage),
    path("contributions/<int:listID>/", views.showContributionsPage),
    path('login/', auth_views.LoginView.as_view(template_name="login.html", next_page="/mugrank/profile")),
    path('profile/', views.profile),
    path('addmug/', views.addMug),
    path('newlist/', views.newList),
    path('newletterboxd/', views.letterboxdList),
]