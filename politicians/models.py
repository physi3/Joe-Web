from django.db import models
from django.contrib.auth.models import User

class Politician(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    globalElo = models.IntegerField()

    def __str__(self) -> str:
        return self.name

class PoliticianUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contributions = models.IntegerField()

class UserPolitician(models.Model):
    politician = models.ForeignKey(Politician, on_delete=models.CASCADE)
    user = models.ForeignKey(PoliticianUser, on_delete=models.CASCADE)
    personalElo = models.IntegerField()
