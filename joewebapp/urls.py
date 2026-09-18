from django.urls import path
from .views import personal, auth, sketches

urlpatterns = [
    path('', personal.index),
    path('sketches/', sketches.index),
    path('sketches/<str:sketch>/', sketches.view),
    path('sketches/<str:sketch>/source/', sketches.source),
    path("login/", auth.JoeLoginView.as_view(template_name="auth/login.html", next_page="/"), name="login"),
    path("auth/<str:service>/", auth.auth),
]
