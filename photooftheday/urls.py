from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", auth_views.LoginView.as_view(template_name='photooftheday/login.html'), name="login"),
    path("calendar/<int:year>/<int:month_int>/", views.calendar_view, name="calendar"),
    path("calendar/", views.calendar_this_month, name="calendar_this_month"),
    path("week/", views.this_week, name="this_week"),
    path("week/<int:year>/<int:month>/<int:day>/", views.week, name="this_week"),
    path("week/save/<int:dispatch_entry_id>/", views.save_weekly_setup, name="save_week_layout"),
    path("<int:year>/<int:month>/<int:day>/", views.day, name="day"),
    path("<int:year>/<int:month>/<int:day>/upload/", views.upload, name="upload"), # type: ignore
]