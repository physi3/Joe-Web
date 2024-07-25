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
    path('new/mug/', views.createMug),
    path('new/list/', views.createList),
    path('new/letterboxd/', views.createLetterboxdList),
    path('new/listuser/', views.createListInvite),
    path('invite/<invitation>', views.acceptInvite),
    path("update/<int:listID>/", views.updateList),
]