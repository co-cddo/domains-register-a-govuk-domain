from django.core.management.base import BaseCommand
from request_a_govuk_domain.request import models


PERSON_NAMES = ["Bob Roberts", "Peter Peters", "Olivia Oliver"]

REGISTRANT_ORG = "Ministry of Domains"
REGISTRAR = "WeRegister"

DOMAIN_NAME = "ministryofdomains.gov.uk"
DOMAIN_PURPOSE = "Web site"


class Command(BaseCommand):
    help = "Create a sample application for local testing"

    def handle(self, *args, **options):
        persons = [models.Person.objects.create(name=name) for name in PERSON_NAMES]

        registrar = models.Registrar(name=REGISTRAR)
        registrant = models.Registrant(
            name=REGISTRANT_ORG,
            type=models.RegistrantTypeChoices.central_government,
        )

        application = models.Application(
            domain_name=DOMAIN_NAME,
            applicant=persons[0],
            registrant_person=persons[1],
            responsible_person=persons[2],
            registrant_org=registrant,
            registrar=registrar,
            written_permission_evidence="",
        )

        registrar.save()
        registrant.save()
        application.save()

        models.CentralGovernmentAttributes.objects.create(application=application)
        models.Review.objects.create(application=application)
