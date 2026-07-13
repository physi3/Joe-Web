from django.contrib import admin
from .models import *

# Register your models here.
admin.site.site_header = "Fauxcademy Admin"

admin.site.register(Awards)
admin.site.register(EligibleFilm)
admin.site.register(AwardMembership)
admin.site.register(UserEligibleFilmStatus)
admin.site.register(AwardCategory)
admin.site.register(Nomination)
admin.site.register(NominatedPerson)
admin.site.register(Ballot)