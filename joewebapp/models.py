from django.db import models

class Sketch(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(blank=True, upload_to='joewebapp/sketch-images/')
    templateName = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Sketches"

    def __str__(self):
        return f"{self.name} Sketch"