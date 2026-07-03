"""
Generated migration to replace owner+name unique constraint with a
case-insensitive constraint on name (Lower(name) + owner).
"""
from django.db import migrations, models
import django.db.models.functions as functions
from django.db.models import F


class Migration(migrations.Migration):

    dependencies = [
        ("fauxcademy", "0003_awards_unique_owner_name"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="awards",
            name="unique_award_owner_name",
        ),
        migrations.AddConstraint(
            model_name="awards",
            constraint=models.UniqueConstraint(functions.Lower("name"), F("owner"), name="unique_award_owner_name_ci"),
        ),
    ]
