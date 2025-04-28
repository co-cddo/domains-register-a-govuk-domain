from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase

EXPECTED_PERMISSIONS = [
    "change_application",
    "change_review",
    "view_registrant",
    "view_registrar",
    "view_registrarperson",
    "view_registrantperson",
    "view_registrypublishedperson",
]


class CreateReviewerGroupTestCase(TestCase):
    def setUp(self):
        Group.objects.all().delete()

    def test_group_created(self):
        call_command("create_reviewer_group")
        self.assertTrue(Group.objects.filter(name="reviewer").exists())

    def test_group_permissions(self):
        call_command("create_reviewer_group")
        reviewer_group = Group.objects.get(name="reviewer")
        codenames = [permission["codename"] for permission in reviewer_group.permissions.all().values()]
        self.assertEqual(sorted(EXPECTED_PERMISSIONS), sorted(codenames))
