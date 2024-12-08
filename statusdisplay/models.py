from django.db import models
import datetime

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.name}"

class Status(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    createTime = models.DateTimeField()

    lineOne = models.CharField(max_length=20, blank=True)
    lineTwo = models.CharField(max_length=20, blank=True)
    lineThree = models.CharField(max_length=20, blank=True)
    lineFour = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name_plural = "Statuses"

    def __str__(self):
        return f"{self.user} - {self.createTime.strftime('%d %b %Y, %I:%M%p')}"

class Display(models.Model):
    name = models.CharField(max_length=32)
    targetUser = models.ForeignKey(User, on_delete=models.RESTRICT)
    backlight = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"
    