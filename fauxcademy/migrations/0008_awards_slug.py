from django.db import migrations, models
from django.db.models import F
from django.db.models.functions import Lower
from django.utils.text import slugify


def generate_unique_slug(award, existing_slugs):
    base_slug = slugify(award.name) or 'award'
    candidate = base_slug
    counter = 1
    while candidate.lower() in existing_slugs:
        counter += 1
        candidate = f"{base_slug}-{counter}"
    existing_slugs.add(candidate.lower())
    return candidate


def populate_slugs(apps, schema_editor):
    Awards = apps.get_model('fauxcademy', 'Awards')
    existing_slugs = set()

    for award in Awards.objects.all().order_by('owner_id', 'id'):
        candidate = slugify(award.name) or 'award'
        slug = candidate
        counter = 1
        while slug.lower() in existing_slugs or Awards.objects.filter(owner=award.owner, slug__iexact=slug).exclude(pk=award.pk).exists():
            counter += 1
            slug = f"{candidate}-{counter}"
        award.slug = slug
        award.save()
        existing_slugs.add(slug.lower())


class Migration(migrations.Migration):

    dependencies = [
        ('fauxcademy', '0007_award_membership'),
    ]

    operations = [
        migrations.AddField(
            model_name='awards',
            name='slug',
            field=models.SlugField(blank=True, default='', max_length=100),
            preserve_default=False,
        ),
        migrations.RunPython(populate_slugs, reverse_code=migrations.RunPython.noop),
        migrations.RemoveConstraint(
            model_name='awards',
            name='unique_award_owner_name',
        ),
        migrations.AddConstraint(
            model_name='awards',
            constraint=models.UniqueConstraint(Lower('slug'), F('owner'), name='unique_award_owner_slug'),
        ),
    ]
