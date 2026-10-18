from django.contrib import admin
from .models import Group, GroupMember, PhotoSubmission, WeeklyDispatch, WeeklyDispatchEntry
from django import forms

class GroupAdmin(admin.ModelAdmin):
	list_display = ("name", "created_at")


class GroupMemberAdmin(admin.ModelAdmin):
	list_display = ("name", "user", "group",)
	search_fields = ("name", "user__username", "user__email")
	widgets = {
		"colour": forms.TextInput(attrs={"type": "color"})
	}


class PhotoSubmissionAdmin(admin.ModelAdmin):
	list_display = ("user", "group", "date", "time")
	list_filter = ("date", "group")
	search_fields = ("user__username", "caption")
	readonly_fields = ("date", "cached_address",)
	ordering = ("-date",)

class WeeklyDispatchAdmin(admin.ModelAdmin):
	list_display = ("week_start", "published", "editor")
	list_filter = ("published",)
	search_fields = ("editor__username",)
	ordering = ("-week_start",)

admin.site.site_header = "Photo of the Day Admin"
admin.site.register(Group, GroupAdmin)
admin.site.register(GroupMember, GroupMemberAdmin)
admin.site.register(PhotoSubmission, PhotoSubmissionAdmin)
admin.site.register(WeeklyDispatch, WeeklyDispatchAdmin)
admin.site.register(WeeklyDispatchEntry)