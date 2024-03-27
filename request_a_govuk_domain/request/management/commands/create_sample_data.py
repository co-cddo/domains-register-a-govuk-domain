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
                type=models.RegistrantTypeChoices.central_government,
            )
            for name in REGISTRANT_NAMES
        ]

        application = models.Application(
            domain_name=DOMAIN_NAME,
            registrant_person=registrant_person,
            registrar_person=registrar_person,
            registry_published_person=registry_published_person,
            registrant_org=registrants[0],
            registrar_org=application_registrar,
            written_permission_evidence="something",
        )

        application.save()

        models.CentralGovernmentAttributes.objects.create(application=application)
        models.Review.objects.create(application=application)
