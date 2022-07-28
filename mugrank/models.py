from pyexpat import model
from django.db import models
from django.contrib.auth.models import User

class List(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Mug(models.Model):
    K = 32

    name = models.CharField(max_length=100, blank=True)
    image_path = models.CharField(max_length=100, blank=True)
    elo = models.IntegerField(default=1000)
    list = models.ForeignKey(List, on_delete=models.CASCADE)

    def expectedScore(self, enemy):
        return 1 / (1 + 10**((enemy.elo - self.elo)/400))
    
    def updateRatings(self, score, other):
        self.elo += round(self.K * (score - self.expectedScore(other)))

    def __str__(self):
        return self.name

class ListUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list = models.ForeignKey(List, on_delete=models.CASCADE)

    def findMugsToRate(self):
        mugs = Mug.objects.filter(list__exact=self.list)
        for mugOne in mugs.order_by('?'):
            for mugTwo in mugs.order_by('?'):
                if mugOne.id == mugTwo.id:
                    continue
                ratings = MugRankRecord.objects.filter(user__exact=self.user)
                if (ratings.filter(mug_one__exact=mugOne).filter(mug_two__exact=mugTwo).exists()
                    or ratings.filter(mug_one__exact=mugTwo).filter(mug_two__exact=mugOne).exists()):
                    continue
                return (mugOne, mugTwo)
        
        # Rated all mugs

        for mugOne in mugs.order_by('?'):
            for mugTwo in mugs.order_by('?'):
                if mugOne.id != mugTwo.id:
                    return (mugOne, mugTwo)

    def getContributions(self):
        recordsQuery = MugRankRecord.objects.filter(user__exact=self.user).filter(mug_one__list__exact=self.list)
        return recordsQuery.count()


    def __str__(self):
        return f"{self.list}.{self.user}"

class MugRankRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mug_one = models.ForeignKey(Mug, on_delete=models.CASCADE, related_name="mug_one")
    mug_two = models.ForeignKey(Mug, on_delete=models.CASCADE, related_name="mug_two")
    one_won = models.BooleanField()
