from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fauxcademy', '0010_awardcategory_nomination'),
    ]

    operations = [
        migrations.AddField(
            model_name='awardcategory',
            name='importance',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
