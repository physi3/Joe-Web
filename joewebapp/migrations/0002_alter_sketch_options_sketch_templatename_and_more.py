# Generated by Django 4.0 on 2023-04-08 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('joewebapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sketch',
            options={'verbose_name_plural': 'Sketches'},
        ),
        migrations.AddField(
            model_name='sketch',
            name='templateName',
            field=models.CharField(default='temp', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='sketch',
            name='image',
            field=models.ImageField(blank=True, upload_to='joewebapp/sketch-images/'),
        ),
    ]
