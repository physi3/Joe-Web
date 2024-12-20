# Generated by Django 4.0 on 2024-12-08 17:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('statusdisplay', '0003_alter_status_linefour_alter_status_lineone_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Display',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('backlight', models.BooleanField(default=True)),
                ('targetUser', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='statusdisplay.user')),
            ],
        ),
    ]
