# Generated by Django 4.0.6 on 2022-07-23 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mugrank', '0006_alter_mug_elo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mug',
            name='image_path',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
