"""
Generated migration to make `Awards.name` unique per `owner`.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fauxcademy", "0002_alter_awards_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="awards",
            name="name",
            field=models.CharField(max_length=100),
        ),
        migrations.AddConstraint(
            model_name="awards",
            constraint=models.UniqueConstraint(fields=["owner", "name"], name="unique_award_owner_name"),
        ),
    ]
