from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fauxcademy', '0011_awardcategory_importance'),
    ]

    operations = [
        migrations.AddField(
            model_name='awardcategory',
            name='slug',
            field=models.SlugField(blank=True, max_length=120),
        ),
    ]
