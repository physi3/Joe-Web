from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from typing import Any
from decimal import Decimal
from datetime import datetime

from photooftheday.utils.geocoding import readable_from_decimal

try:
	from PIL import Image, ExifTags
except Exception:  # Pillow may not be installed in the environment running static checks
	Image = None
	ExifTags = None


class Group(models.Model):
	"""A Photo-of-the-Day group containing exactly three users."""

	name = models.CharField(max_length=100, blank=True)
	created_at = models.DateTimeField(default=timezone.now)

	# Annotate reverse relation manager populated by Django's FK related_name
	members: Any


	def __str__(self):
		return self.name or f"Group #{self.pk}"

	@property
	def member_count(self):
		return self.members.count()

	def is_full(self):
		return self.member_count >= 3


class GroupMember(models.Model):
	"""Membership linking a single `User` to a `Group`.

	A `OneToOneField` on `user` enforces that a user can be in only one group.
	We enforce a maximum of 3 members per group in `save()`.
	"""

	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	group = models.ForeignKey(Group, related_name="members", on_delete=models.CASCADE)
	name = models.CharField(max_length=150)

	class Meta:
		ordering = ("group",)

	def __str__(self):
		return f"{self.user} in {self.group}"

	def clean(self):
		# Prevent adding more than 3 members to a group
		if self.pk is None and self.group.members.count() >= 3:
			raise ValidationError({"group": "This group already has 3 members."})

	def save(self, *args, **kwargs):
		if self.pk is None and not self.name:
			self.name = self.user.username
		self.full_clean()
		super().save(*args, **kwargs)


class PhotoSubmission(models.Model):
	"""A submitted photo for a given day by a user in a group."""

	group = models.ForeignKey(Group, related_name="submissions", on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="photo_submissions", on_delete=models.CASCADE)
	image = models.ImageField(upload_to="photooftheday/%Y/%m/%d/")
	caption = models.TextField(blank=True)
	time = models.TimeField(null=True, blank=True)

	# Simple geotag fields (latitude / longitude). Use Decimal for precision.

	latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
	longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

	# A date-only field to enforce one submission per-user-per-day.
	date = models.DateField(editable=False, db_index=True)

	cached_address = models.JSONField(null=True, blank=True, editable=False)

	class Meta:
		ordering = ("-date","user",)
		constraints = [
			models.UniqueConstraint(fields=["user", "date"], name="unique_submission_per_user_per_day"),
		]

	def __str__(self):
		return f"Submission by {self.user} on {self.date}"

	def clean(self):
		# Ensure the submitting user is a member of the referenced group
		if not GroupMember.objects.filter(group=self.group, user=self.user).exists():
			raise ValidationError({"user": "User must be a member of the submission's group."})

		# Enforce one submission per user per day
		if self.user and self.date:
			qs = PhotoSubmission.objects.filter(user=self.user, date=self.date)
			if self.pk:
				qs = qs.exclude(pk=self.pk)
			if qs.exists():
				raise ValidationError({"user": "User already has a submission for this day."})

	def cache_address_from_latlon(self):
		"""If latitude and longitude are set, use reverse geocoding to cache a human-readable address."""
		if self.latitude is not None and self.longitude is not None:
			address = readable_from_decimal(float(self.latitude), float(self.longitude))
			self.cached_address = address
		else:
			self.cached_address = {"name": None, "city": "Unknown", "country": None}

	def save(self, *args, **kwargs):
		self.cache_address_from_latlon()
		super().save(*args, **kwargs)

