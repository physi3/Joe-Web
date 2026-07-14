from .services.tmdbClient import MovieClient, PersonClient, PosterURL

from django.contrib.auth.models import User
from django.db import models
from django.db.models.functions import Lower
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Awards(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    results_ready = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    class Meta:
        constraints = [
            models.UniqueConstraint(Lower("slug"), "owner", name="unique_award_owner_slug"),
        ]
    
    def clean(self):
        if self.owner and self.slug:
            qs = Awards.objects.filter(owner=self.owner, slug__iexact=self.slug)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({'slug': 'You already have an award with this URL title.'})

    def get_absolute_url(self):
        return reverse('user_list', kwargs={
            'username': self.owner.username,
            'listname': self.slug,
        })

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            while Awards.objects.filter(owner=self.owner, slug__iexact=unique_slug).exclude(pk=self.pk or None).exists():
                counter += 1
                unique_slug = f"{base_slug}-{counter}"
            self.slug = unique_slug

        super().save(*args, **kwargs)

    def has_access(self, user):
        if user == self.owner:
            return True
        return self.memberships.filter(user=user).exists()

    def is_admin(self, user):
        if user == self.owner:
            return True
        return self.memberships.filter(user=user, is_admin=True).exists()

    def getCategories(self):
        return AwardCategory.objects.filter(awards=self)

    def totalVoteState(self):
        counts = {"finished":0, "partial":0, "not_started":0}

        for membership in self.memberships.select_related('user'):
            counts[self.userVoteState(membership.user)] += 1

        return counts

    def userVoteState(self, user):
        ballotsCast = []
        for category in self.getCategories():
            ballotsCast.append(Ballot.objects.filter(category=category, user=user).exists())

        if all(ballotsCast):
            return "finished"
        if any(ballotsCast):
            return "partial"
        return "not_started"

    @property
    def memberships(self):
        return AwardMembership.objects.filter(award=self)
    


class AwardMembership(models.Model):
    award = models.ForeignKey(Awards, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='award_memberships')
    is_admin = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['award', 'user'], name='unique_award_user'),
        ]

    def __str__(self):
        role = 'admin' if self.is_admin else 'member'
        return f'{self.user.username} ({role}) of {self.award.name}'

    def save(self, *args, **kwargs):
        if self.user == self.award.owner:
            self.is_admin = True
        super().save(*args, **kwargs)


@receiver(post_save, sender=Awards)
def ensure_owner_membership(sender, instance, created, **kwargs):
    AwardMembership.objects.update_or_create(
        award=instance,
        user=instance.owner,
        defaults={'is_admin': True},
    )


class EligibleFilm(models.Model):
    tmdb_id = models.IntegerField()
    awards = models.ForeignKey(Awards, on_delete=models.CASCADE)
    
    cache_LOD = models.IntegerField(default=0, help_text="Cache Level of Detail: 0 = no cache, 1 = title only, 2 = basic info")

    cached_title = models.CharField(max_length=200, blank=True)

    cached_tagline = models.CharField(max_length=200, blank=True)
    cached_overview = models.TextField(blank=True)
    cached_poster_path = models.CharField(null=True, max_length=200, blank=True)
    cached_release_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Film {self.cached_title} for Award {self.awards.name}"

    def RefreshCache(self, LOD = 2):
        tmdbMovie = self.tmdbMovie()

        if LOD >= 1:
            self.cached_title = tmdbMovie.get("title", self.cached_title)
        if LOD >= 2:
            self.cached_tagline = tmdbMovie.get("tagline", self.cached_tagline)
            self.cached_overview = tmdbMovie.get("overview", self.cached_overview)
            self.cached_poster_path = tmdbMovie.get("poster_path", self.cached_poster_path)
            self.cached_release_date = tmdbMovie.get("release_date", self.cached_release_date)

        self.cache_LOD = LOD
        self.save()

    def GetCTX(self, LOD = 2, getNominations = False):
        if self.cache_LOD < LOD:
            self.RefreshCache(LOD)

        ctx = {
            "tmdb_id": self.tmdb_id,
            "title": self.cached_title,
        }

        if LOD < 2:
            return ctx

        ctx.update({"tagline": self.cached_tagline,
            "overview": self.cached_overview,
            "poster_url": PosterURL(self.cached_poster_path, type="movie"),
            "release_date": self.cached_release_date})

        if not getNominations:
            return ctx

        ctx.update({
            "nominations" : Nomination.objects.filter(film=self)
        })

        return ctx

    def tmdbMovie(self):
        movie_client = MovieClient()
        return movie_client.details(self.tmdb_id)


class UserEligibleFilmStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='film_statuses')
    eligible_film = models.ForeignKey(EligibleFilm, on_delete=models.CASCADE, related_name='user_statuses')
    is_watched = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'eligible_film'], name='unique_user_eligible_film_status'),
        ]

    def __str__(self):
        title = self.eligible_film.cached_title or str(self.eligible_film.tmdb_id)
        state = 'watched' if self.is_watched else 'unwatched'
        return f'{self.user.username} {state} {title}'


class AwardCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    awards = models.ForeignKey(Awards, on_delete=models.CASCADE, related_name='categories')
    nominee_type = models.CharField(max_length=50, choices=[('film', 'Film'), ('cast', 'Cast'), ('crew', 'Crew')], default='film')
    importance = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['importance', 'name']
        constraints = [
            models.UniqueConstraint(
                Lower("slug"),
                "awards",
                name="unique_category_award_slug"
            )
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            while AwardCategory.objects.filter(awards=self.awards, slug__iexact=unique_slug).exclude(pk=self.pk or None).exists():
                counter += 1
                unique_slug = f"{base_slug}-{counter}"
            self.slug = unique_slug

        super().save(*args, **kwargs)
    

class Nomination(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(AwardCategory, on_delete=models.CASCADE)
    film = models.ForeignKey(EligibleFilm, on_delete=models.CASCADE)
    nominated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    nominated_person = models.ForeignKey("NominatedPerson", on_delete=models.CASCADE, null=True, blank=True)
    nominated_role = models.CharField(null=True, blank=True, max_length=50)

    def clean(self):
        super().clean()

        if self.category.nominee_type in ["cast", "crew"] and self.nominated_person is None:
            raise ValidationError({
                "nominated_person": "This category requires a nominated person."
            })
        
        queryset = Nomination.objects.filter(category=self.category)

        if self.pk:
            queryset = queryset.exclude(pk=self.pk)

        nominee_type = self.category.nominee_type

        if nominee_type == "film":
            if queryset.filter(film=self.film).exists():
                raise ValidationError(
                    "This film has already been nominated in this category."
                )

        else:
            if queryset.filter(
                film=self.film,
                nominated_person=self.nominated_person,
                nominated_role=self.nominated_role,
            ).exists():
                raise ValidationError(
                    "This nomination already exists."
                )

    def GetCTX(self):
        ctx = {}

        filmCtx = self.film.GetCTX(LOD=2)
        ctx["film_title"] = filmCtx["title"]
        ctx["id"] = self.id
        ctx["str"] = str(self)

        match self.category.nominee_type:
            case "film":
                
                ctx["title"] = filmCtx["title"]
                ctx["poster_url"] = filmCtx["poster_url"]

            case "cast" | "crew":
                person = self.nominated_person
                if person is None:
                    raise Exception("Person not defined")

                personCtx = person.GetCTX(LOD=2)
                ctx["title"] = personCtx["name"]
                ctx["poster_url"] = personCtx["poster_url"]

                ctx["person_name"] = personCtx["name"]
                ctx["person_role"] = self.nominated_role

        return ctx

    def __str__(self):
        match self.category.nominee_type:
            case "film":
                return self.film.GetCTX(1)["title"]
            case "cast":
                person = self.nominated_person
                if person is None:
                    raise Exception("Person not defined")
                
                return f"{person.GetCTX(1)["name"]} as {self.nominated_role}"
            case "crew":
                person = self.nominated_person
                if person is None:
                    raise Exception("Person not defined")
                
                return f"{person.GetCTX(1)["name"]} for {self.film.GetCTX(1)["title"]}"
    

class NominatedPerson(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    
    cache_LOD = models.IntegerField(default=0, help_text="Cache Level of Detail: 0 = no cache, 1 = title only, 2 = basic info")

    cached_name = models.CharField(max_length=200, blank=True)

    cached_biography = models.CharField(max_length=200, blank=True)
    cached_poster_path = models.CharField(null=True, max_length=200, blank=True)

    def __str__(self):
        return f"Person {self.cached_name}"

    def RefreshCache(self, LOD = 2):
        tmdbPerson = self.tmdbPerson()

        if LOD >= 1:
            self.cached_name = tmdbPerson.get("name", self.cached_name)
        if LOD >= 2:
            self.cached_biography = tmdbPerson.get("biography", self.cached_biography)
            self.cached_poster_path = tmdbPerson.get("profile_path", self.cached_poster_path)

        self.cache_LOD = LOD
        self.save()

    def GetCTX(self, LOD = 2):
        if self.cache_LOD < LOD:
            self.RefreshCache(LOD)

        ctx = {
            "tmdb_id": self.tmdb_id,
            "name": self.cached_name,
            "biography": self.cached_biography,
            "poster_url": PosterURL(self.cached_poster_path, type="person"),
        }

        return ctx

    def tmdbPerson(self):
        person_client = PersonClient()
        return person_client.details(self.tmdb_id)
    

class Ballot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(AwardCategory, on_delete=models.CASCADE)

    first_choice = models.ForeignKey(
        Nomination,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="first_choice_ballots"
    )

    second_choice = models.ForeignKey(
        Nomination,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="second_choice_ballots"
    )

    third_choice = models.ForeignKey(
        Nomination,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="third_choice_ballots"
    )

    def clean(self):
        choices = [
            self.first_choice,
            self.second_choice,
            self.third_choice
        ]

        choices = [choice for choice in choices if choice]

        # No duplicate nominations
        ids = [choice.id for choice in choices]
        if len(ids) != len(set(ids)):
            raise ValidationError(
                "A nomination cannot appear more than once on a ballot."
            )

        # All nominations must belong to this ballot's category
        for choice in choices:
            if choice.category != self.category:
                raise ValidationError(
                    "All choices must belong to the ballot category."
                )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "category"],
                name="unique_user_category_ballot"
            )
        ]