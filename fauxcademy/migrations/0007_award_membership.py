"""Add AwardMembership model and create owner memberships."""

from django.db import migrations, models


def create_owner_memberships(apps, schema_editor):
    Awards = apps.get_model('fauxcademy', 'Awards')
    AwardMembership = apps.get_model('fauxcademy', 'AwardMembership')

    for award in Awards.objects.all():
        AwardMembership.objects.update_or_create(
            award=award,
            user=award.owner,
            defaults={'is_admin': True},
        )


def delete_owner_memberships(apps, schema_editor):
    AwardMembership = apps.get_model('fauxcademy', 'AwardMembership')
    AwardMembership.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('fauxcademy', '0006_eligiblefilm_cache_lod_eligiblefilm_cached_overview_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AwardMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_admin', models.BooleanField(default=False)),
                ('award', models.ForeignKey(on_delete=models.CASCADE, related_name='memberships', to='fauxcademy.awards')),
                ('user', models.ForeignKey(on_delete=models.CASCADE, related_name='award_memberships', to='auth.user')),
            ],
        ),
        migrations.AddConstraint(
            model_name='awardmembership',
            constraint=models.UniqueConstraint(fields=['award', 'user'], name='unique_award_user'),
        ),
        migrations.RunPython(create_owner_memberships, delete_owner_memberships),
    ]
