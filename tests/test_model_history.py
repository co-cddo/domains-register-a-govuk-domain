from unittest.mock import Mock

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from request_a_govuk_domain.request import db
from request_a_govuk_domain.request.management.commands import add_init_guidance_text
from request_a_govuk_domain.request.models import (
    Registrar,
    Registrant,
    RegistrantPerson,
    RegistrarPerson,
    RegistryPublishedPerson,
    Review,
    ApplicationStatus,
)


class CheckHistoryTestCase(TestCase):
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

        User.objects.create_superuser(
            username="superuser",
            password="secret",  # pragma: allowlist secret
            email="admin@example.com",
        )
        guidance_text = add_init_guidance_text.Command()
        guidance_text.handle()
        self.c = Client()
        self.c.login(
            username="superuser", password="secret"  # pragma: allowlist secret
        )

    def test_application_history(self):
        """
        Test case to check that we load the correct application on the review screen.
        When we click on the item in the list, we load the correct data from the corresponding review steps.
        :return:
        """
        request = Mock()
        request.session = SessionDict({"registration_data": self.registration_data})

        # Simulate application creation through client screens
        application = db.save_data_in_database("ABCDEFGHIJK", request)

        # see the records in history table
        history = application.history.all()  # type: ignore
        self.assertEqual(len(history), 1)

        response = self.c.get(get_admin_change_view_url(application))
        self.assertContains(response, "History")

        # change application field
        application.status = ApplicationStatus.IN_PROGRESS
        application.save()
        history = application.history.all()  # type: ignore
        self.assertEqual(len(history), 2)

    def test_review_history(self):
        """
        Test case to check that we load the correct application on the review screen.
        When we click on the item in the list, we load the correct data from the corresponding review steps.
        :return:
        """
        request = Mock()
        request.session = SessionDict({"registration_data": self.registration_data})

        # Simulate application creation through client screens
        application = db.save_data_in_database("ABCDEFGHIJL", request)

        # Now we review the last application created by the client
        review = Review.objects.filter(
            application__reference=application.reference
        ).first()

        # see the records in history table
        history = review.history.all()  # type: ignore
        self.assertEqual(len(history), 1)

        response = self.c.get(get_admin_change_view_url(review))

        self.assertContains(response, "History")

        # change review field
        review.registrar_details_notes = "test"  # type: ignore
        review.save()  # type: ignore
        history = review.history.all()  # type: ignore
        self.assertEqual(len(history), 2)


def get_admin_change_view_url(obj: object) -> str:
    return reverse(
        "admin:{}_{}_change".format(obj._meta.app_label, type(obj).__name__.lower()),  # type: ignore
        args=(obj.pk,),  # type: ignore
    )


class SessionDict(dict):
    def __init__(self, *k, **kwargs):
        self.__dict__ = self
        super().__init__(*k, **kwargs)
        self.session_key = "session-key"
