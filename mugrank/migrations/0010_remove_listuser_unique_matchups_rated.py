# Generated by Django 4.0.6 on 2022-07-23 21:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mugrank', '0009_remove_listuser_completed_rankings_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listuser',
            name='unique_matchups_rated',
        ),
    ]
