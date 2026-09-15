from django.db import migrations, models


def set_member_names(apps, schema_editor):
	GroupMember = apps.get_model("photooftheday", "GroupMember")
	for member in GroupMember.objects.select_related("user").all():
		member.name = member.user.username
		member.save(update_fields=["name"])


class Migration(migrations.Migration):

	dependencies = [
		("photooftheday", "0003_photosubmission_cached_address"),
	]

	operations = [
		migrations.AddField(
			model_name="groupmember",
			name="name",
			field=models.CharField(max_length=150, default=""),
		),
		migrations.RunPython(set_member_names, migrations.RunPython.noop),
		migrations.AlterField(
			model_name="groupmember",
			name="name",
			field=models.CharField(max_length=150),
		),
	]