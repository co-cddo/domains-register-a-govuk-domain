from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from request_a_govuk_domain.request import models

VIEWABLE_MODELS = [
    models.Registrant,
    models.Registrar,
    models.RegistrantPerson,
    models.RegistrarPerson,
    models.RegistryPublishedPerson,
]
EDITABLE_MODELS = [models.Review, models.Application]


class Command(BaseCommand):
    help = "Create the reviewer user group to manage permissions for non-superusers"

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name="reviewer")

        view_content_types = [
            ContentType.objects.get_for_model(model) for model in VIEWABLE_MODELS
        ]

        edit_content_types = [
            ContentType.objects.get_for_model(model) for model in EDITABLE_MODELS
        ]

        view_permissions = [
            Permission.objects.get(codename=f"view_{ct.model}", content_type=ct)
            for ct in view_content_types
        ]
        edit_permissions = [
            Permission.objects.get(codename=f"change_{ct.model}", content_type=ct)
            for ct in edit_content_types
        ]

        group.permissions.add(*view_permissions, *edit_permissions)

        if not created:
            print("Reviewer group already exists")
