# Generated by Django 4.0 on 2024-02-27 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mugrank', '0012_filmmug'),
    ]

    operations = [
        migrations.AddField(
            model_name='list',
            name='filmList',
            field=models.BooleanField(default=False),
        ),
    ]
