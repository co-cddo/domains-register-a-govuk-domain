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
        models.RegistryPublishedPerson.objects.all().delete()
        models.RegistrarPerson.objects.all().delete()
        models.Registrar.objects.all().delete()
        models.Registrant.objects.all().delete()
        models.Application.objects.all().delete()
        models.CentralGovernmentAttributes.objects.all().delete()
        models.Review.objects.all().delete()

        registrant_person = models.RegistrantPerson.objects.create(name=PERSON_NAMES[0])

        registry_published_person = models.RegistryPublishedPerson.objects.create(
            name=PERSON_NAMES[2]
        )

        registrars = [
            models.Registrar.objects.create(name=name) for name in REGISTRAR_NAMES
        ]

        application_registrar = registrars[0]

        registrar_person = models.RegistrarPerson.objects.create(
            name=PERSON_NAMES[1], registrar=application_registrar
        )

        registrants = [
            models.Registrant.objects.create(
                name=name,
                type=models.RegistrantTypeChoices.CENTRAL_GOVERNMENT,
            )
            for name in REGISTRANT_NAMES
        ]

        application = models.Application(
            reference="GOVUK20240327ABCD",
            domain_name=DOMAIN_NAME,
            registrant_person=registrant_person,
            registrar_person=registrar_person,
            registry_published_person=registry_published_person,
            registrant_org=registrants[0],
            registrar_org=application_registrar,
            written_permission_evidence=WRITTEN_PERMISSION_FN,
        )

        application.save()

        models.CentralGovernmentAttributes.objects.create(
            application=application,
            ministerial_request_evidence=MINISTERIAL_REQUEST_FN,
            policy_exemption_evidence=POLICY_TEAM_EXEMPTION_FN,
        )

        models.Review.objects.create(application=application)
