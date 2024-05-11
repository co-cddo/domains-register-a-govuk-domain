import os
from django.core.management.base import BaseCommand
from request_a_govuk_domain.request import models


SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
INIT_GUIDANCE_PATH = os.path.join(SCRIPT_PATH, "..", "..", "init_guidance")

GUIDANCE_SECTIONS = (
    "domain_name_availability",
    "domain_name_rules",
    "policy_exemption",
    "registrant_org",
    "registrant_permission",
    "registrant_person",
    "registrant_senior_support",
    "registrar_details",
)


class Command(BaseCommand):
    help = "Add initial guidance text for reviewers into the database"

    def handle(self, *args, **options):
        if not models.ReviewFormGuidance.objects.all():
            for section in GUIDANCE_SECTIONS:
                with open(
                    os.path.join(INIT_GUIDANCE_PATH, f"{section}.md"), "r"
                ) as file:
                    guidance = file.read()
                models.ReviewFormGuidance.objects.create(name=section, how_to=guidance)
