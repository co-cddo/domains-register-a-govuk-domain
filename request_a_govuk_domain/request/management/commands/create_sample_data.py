from django.core.management.base import BaseCommand
from request_a_govuk_domain.request import models


PERSON_NAMES = ["Bob Roberts", "Peter Peters", "Olivia Oliver"]

REGISTRANT_NAMES = ["HMRC", "MOD", "MOT", "MOJ"]
REGISTRAR_NAMES = ["WeRegister", "Registrations R Us", "Fantastic Registrar", "HMRC"]

DOMAIN_NAME = "ministryofdomains.gov.uk"
DOMAIN_PURPOSE = "Web site"


class Command(BaseCommand):
    help = "Create a sample application for local testing"

    def handle(self, *args, **options):
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
            written_permission_evidence="",
        )

        application.save()

        models.CentralGovernmentAttributes.objects.create(application=application)
        models.Review.objects.create(application=application)
