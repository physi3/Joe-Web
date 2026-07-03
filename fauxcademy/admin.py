from django.contrib import admin
from .models import *

# Register your models here.
admin.site.site_header = "Fauxcademy Admin"

admin.site.register(Awards)
admin.site.register(EligibleFilm)