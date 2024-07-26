import datetime
from django.test import TestCase

from request_a_govuk_domain.request.models import (
    Registrar,
    Application,
    Registrant,
    RegistrantPerson,
    RegistrarPerson,
    RegistryPublishedPerson,
    ApplicationStatus,
    TimeFlag,
)

from request_a_govuk_domain.request.tasks import check_application_status


class CheckApplicationStatusTestCase(TestCase):
    def setUp(self):
        self.registrar = Registrar.objects.create(name="dummy registrar")
        self.registrar_person = RegistrarPerson.objects.create(
            name="dummy registrar person", registrar=self.registrar
        )
        self.registrant = Registrant.objects.create(name="dummy registrant")
        self.registrant_person = RegistrantPerson.objects.create(
            name="dummy registrant person"
        )
        self.registry_publish_person = RegistryPublishedPerson.objects.create(
            name="dummy reg publish person"
        )
        self.registration_data = {
            "registrant_type": "parish_council",
            "domain_name": "test.domain.gov.uk",
            "registrar_name": "dummy registrar",
            "registrar_email": "dummy_registrar_email@gov.uk",
            "registrar_phone": "23456789",
            "registrar_organisation": f"{self.registrar.name}-{self.registrar.id}",
            "registrant_organisation": "dummy org",
            "registrant_full_name": "dummy user",
            "registrant_phone": "012345678",
            "registrant_email": "dummy@test.gov.uk",
            "registrant_role": "dummy",
            "registrant_contact_email": "dummy@test.gov.uk",
        }
        self.time_flags = TimeFlag.objects.create()

    def test_change_application_status_from_more_information_to_on_hold(self):
        """
        Test case to check the change of application status from more information to on hold.
        :return:
        """
        # more info application
        self.app1 = Application.objects.create(
            reference="ABCDEFGHIJK",
            status=ApplicationStatus.MORE_INFORMATION,
            last_updated=datetime.datetime.now() - datetime.timedelta(days=5),
            registrant_org=self.registrant,
            registrant_person=self.registrant_person,
            registrar_org=self.registrar,
            registrar_person=self.registrar_person,
            registry_published_person=self.registry_publish_person,
        )
        check_application_status()

        self.app1.refresh_from_db()
        self.assertEqual(self.app1.status, ApplicationStatus.ON_HOLD)

    def test_change_application_status_from_on_hold_to_closed(self):
        """
        Test case to check the change of application status from on hold to rejected.
        :return:
        """
        # on hold application
        self.app2 = Application.objects.create(
            reference="ABCDEFGHIJL",
            status=ApplicationStatus.ON_HOLD,
            last_updated=datetime.datetime.now() - datetime.timedelta(days=61),
            registrant_org=self.registrant,
            registrant_person=self.registrant_person,
            registrar_org=self.registrar,
            registrar_person=self.registrar_person,
            registry_published_person=self.registry_publish_person,
        )
        check_application_status()

        self.app2.refresh_from_db()
        self.assertEqual(self.app2.status, ApplicationStatus.REJECTED)
