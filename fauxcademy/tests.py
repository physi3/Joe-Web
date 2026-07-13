import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AwardCategory, AwardMembership, Awards


class InviteUserViewTests(TestCase):
    def test_admin_can_invite_user_to_award(self):
        User = get_user_model()
        owner = User.objects.create_user(username="owner", password="secret")
        invitee = User.objects.create_user(username="invitee", password="secret")
        award = Awards.objects.create(name="Test Award", owner=owner)

        self.client.force_login(owner)
        response = self.client.post(
            reverse("invite_user", kwargs={"username": owner.username, "listname": award.slug}),
            {"username": invitee.username},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["message"], "Invitation sent successfully.")
        self.assertTrue(AwardMembership.objects.filter(award=award, user=invitee).exists())
        self.assertFalse(AwardMembership.objects.get(award=award, user=invitee).is_admin)


class CategoriesViewTests(TestCase):
    def test_categories_page_renders_award_categories(self):
        User = get_user_model()
        owner = User.objects.create_user(username="owner", password="secret")
        award = Awards.objects.create(name="Test Award", owner=owner)
        category = AwardCategory.objects.create(name="Best Picture", awards=award)

        self.client.force_login(owner)
        response = self.client.get(reverse("categories", kwargs={"username": owner.username, "listname": award.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, category.name)
