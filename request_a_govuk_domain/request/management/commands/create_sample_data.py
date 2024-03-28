import os
import shutil
from django.core.management.base import BaseCommand
from request_a_govuk_domain.request import models


SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
SEED_DOCS_PATH = os.path.join(SCRIPT_PATH, "..", "..", "..", "..", "seed", "documents")
MEDIA_ROOT_PATH = os.path.join(SCRIPT_PATH, "..", "..", "..", "media")

PERSON_NAMES = ["Bob Roberts", "Peter Peters", "Olivia Oliver"]

REGISTRANT_NAMES = ["HMRC", "MOD", "MOT", "MOJ"]
REGISTRAR_NAMES = ["WeRegister", "Registrations R Us", "Fantastic Registrar", "HMRC"]

DOMAIN_NAME = "ministryofdomains.gov.uk"
DOMAIN_PURPOSE = "Web site"

WRITTEN_PERMISSION_FN = "written_permission.png"
MINISTERIAL_REQUEST_FN = "ministerial_request.png"
POLICY_TEAM_EXEMPTION_FN = "policy_team_exception.png"


class Command(BaseCommand):
    help = "Create a sample application for local testing"

    def handle(self, *args, **options):
        for file in os.listdir(SEED_DOCS_PATH):
            try:
                shutil.copy(os.path.join(SEED_DOCS_PATH, file), MEDIA_ROOT_PATH)
            except shutil.SameFileError:
                pass

        # delete existing data in case this is run multiple times
        models.Person.objects.all().delete()
        models.Registrar.objects.all().delete()
        models.Registrant.objects.all().delete()
        models.Application.objects.all().delete()
        models.CentralGovernmentAttributes.objects.all().delete()
        models.Review.objects.all().delete()

        persons = [models.Person.objects.create(name=name) for name in PERSON_NAMES]

        registrars = [
            models.Registrar.objects.create(name=name) for name in REGISTRAR_NAMES
        ]

        registrants = [
            models.Registrant.objects.create(
                name=name,
                type=models.RegistrantTypeChoices.central_government,
            )
            for name in REGISTRANT_NAMES
        ]

        application = models.Application(
            domain_name=DOMAIN_NAME,
            applicant=persons[0],
            registrant_person=persons[1],
            responsible_person=persons[2],
            registrant_org=registrants[0],
            registrar=registrars[0],
            written_permission_evidence=WRITTEN_PERMISSION_FN,
        )

        application.save()

        models.CentralGovernmentAttributes.objects.create(
            application=application,
            ministerial_request_evidence=MINISTERIAL_REQUEST_FN,
            policy_exemption_evidence=POLICY_TEAM_EXEMPTION_FN,
        )

        models.Review.objects.create(application=application)
