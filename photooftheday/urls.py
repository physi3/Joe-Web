from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import map_views

urlpatterns = [
    path("", views.index, name="index"),
    path("map/", map_views.photo_map, name="photo_map"),
    path("map/data/", map_views.map_data, name="photo_map_data"),
    path("map/photos/<int:photo_id>/", map_views.map_photo, name="photo_map_detail"),
    path("map/photos/<int:photo_id>/thumbnail/<str:size>/", map_views.map_thumbnail, name="photo_map_thumbnail"),
    path("login/", auth_views.LoginView.as_view(template_name='photooftheday/login.html'), name="login"),
    path("calendar/<int:year>/<int:month_int>/", views.calendar_view, name="calendar"),
    path("calendar/", views.calendar_this_month, name="calendar_this_month"),
    path("week/", views.this_week, name="this_week"),
    path("week/<int:year>/<int:month>/<int:day>/", views.week, name="this_week"),
    path("week/save/<int:dispatch_entry_id>/", views.save_weekly_setup, name="save_week_layout"),
    path("week/publish/<int:dispatch_id>/", views.publish_weekly_dispatch, name="publish_week"),
    path("<int:year>/<int:month>/<int:day>/", views.day, name="day"),
    path("<int:year>/<int:month>/<int:day>/upload/", views.upload, name="upload"), # type: ignore
]
