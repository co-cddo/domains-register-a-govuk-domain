from unittest.mock import Mock

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from request_a_govuk_domain.request import db
from request_a_govuk_domain.request.management.commands import add_init_guidance_text
from request_a_govuk_domain.request.models import (
    Registrar,
    Application,
    Registrant,
    RegistrantPerson,
    RegistrarPerson,
    RegistryPublishedPerson,
    Review,
)


class ModelAdminTestCase(TestCase):
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

    def test_create_approval_works(self):
        """
        Test case to check that we load the correct application on the review screen.
        When we click on the item in the list, we load the correct data from the corresponding review steps.
        :return:
        """
        request = Mock()
        request.session = SessionDict({"registration_data": self.registration_data})

        # Simulate application creation through client screens
        db.save_data_in_database("ABCDEFGHIJK", request)
        # Simulate application creation through admin screen
        Application.objects.create(
            reference="ABCDEFGHIJL",
            registrant_org=self.registrant,
            registrant_person=self.registrant_person,
            registrar_org=self.registrar,
            registrar_person=self.registrar_person,
            registry_published_person=self.registry_publish_person,
        )

        # Make the application email unique so that we are sure when we compare the data later
        self.registration_data["registrar_email"] = "dummy_registrar_email-xx@gov.uk"
        # Simulate application creation through client screens
        application_to_approve = db.save_data_in_database("ABCDEFGHIJG", request)

        # Now we review the last application created by the client
        review = Review.objects.filter(
            application__reference=application_to_approve.reference
        ).first()
        response = self.c.get(get_admin_change_view_url(review))
        with self.subTest("Review screen shows correct parameters"):
            # Page title should display application reference and the domain name
            self.assertEqual(
                f"{application_to_approve.reference} - {application_to_approve.domain_name}",
                response.context_data["subtitle"],
            )
            # Addition check the ids are correctly assigned.
            # The id of the review should be one less than of the application
            # as we created one application outside the normal flow
            self.assertEqual(
                review.id + 1,
                application_to_approve.id,
                "Id of the review should one less than the application id",
            )
            # Object id should be the same as the review id
            self.assertEqual(review.id, int(response.context_data["object_id"]))

        with self.subTest("Approving the review brings up the correct data"):
            approve_response = self.c.post(
                get_admin_change_view_url(review),
                data={"reason": "good application", "_approve": "Approve"},
                follow=True,
            )
            # Check that the data shown on the screen is from the correct application
            self.assertContains(
                approve_response,
                "Send an email confirming the approval to dummy_registrar_email-xx@gov.uk",
            )
            self.assertContains(
                approve_response, "Reason for approval: good application"
            )

            # Make sure the id displayed on the url is the id if the application
            self.assertEqual(
                f"/admin/application_confirm/?obj_id={application_to_approve.id}&action=approval",
                approve_response.redirect_chain[0][0],
            )

        with self.subTest(
            "Confirming the application will change the status to approved"
        ):
            # All the parameters used below are validate in the previous step
            approve_response = self.c.post(
                approve_response.redirect_chain[0][0],
                data={
                    "_confirm": "Confirm",
                    "action": "approval",
                    "obj_id": application_to_approve.id,
                },
                follow=True,
            )
            # Refresh from the database
            application_to_approve.refresh_from_db()
            self.assertEqual("approved", application_to_approve.status)
            self.assertContains(approve_response, "Approval email sent")


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
