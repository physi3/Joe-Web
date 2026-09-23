from django.urls import path
from .views import personal, auth, sketches
from .scripts import MancinoView

personalPages = {
    "" : personal.CurrentPersonalPage,
    "archive/2026/" : personal.CurrentPersonalPage,
    "archive/2025/" : personal.PersonalPage2025,
}

personalUrlPatterns = [
    pattern
    for prefix, page in personalPages.items()
    for pattern in page.GetUrlPatterns(prefix)
]

urlpatterns = [
    *personalUrlPatterns,
    path('sketches/', sketches.index),
    path('sketches/<str:sketch>/', sketches.view),
    path('sketches/<str:sketch>/source/', sketches.source),
    path("login/", auth.JoeLoginView.as_view(template_name="auth/login.html", next_page="/"), name="login"),
    path("auth/<str:service>/", auth.auth),
    path("scripts/the-mancino-affair/", MancinoView),
]
