from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('fauxcademy', '0009_usereligiblefilmstatus_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AwardCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('nominee_type', models.CharField(choices=[('film', 'Film'), ('cast', 'Cast'), ('crew', 'Crew')], default='film', max_length=50)),
                ('awards', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='fauxcademy.awards')),
            ],
        ),
        migrations.CreateModel(
            name='Nomination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nominated_person_tmdb_id', models.IntegerField(blank=True, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fauxcademy.awardcategory')),
                ('film', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fauxcademy.eligiblefilm')),
                ('nominated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
        ),
    ]
