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
)
from request_a_govuk_domain.request.models.review_choices import (
    RegistryDetailsReviewChoices,
    RegistrantOrgReviewChoices,
    RegistrantPersonReviewChoices,
    RegistrantPermissionReviewChoices,
    PolicyExemptionReviewChoices,
    DomainNameRulesReviewChoices,
    RegistrantSeniorSupportReviewChoices,
    RegistrarDetailsReviewChoices,
)


class ReviewSetTestCase(TestCase):
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
        request = Mock()
        request.session = SessionDict({"registration_data": self.registration_data})

        # Simulate application creation through client screens
        self.application = db.save_data_in_database("ABCDEFGHIJK", request)

        # Make the application email unique so that we are sure when we compare the data later
        self.registration_data["registrar_email"] = "dummy_registrar_email-xx@gov.uk"

        # Now we review the last application created by the client
        self.review = Review.objects.first()

        self.review.registry_details = RegistryDetailsReviewChoices.APPROVE  # type: ignore
        self.review.registrant_org = RegistrantOrgReviewChoices.APPROVE  # type: ignore
        self.review.registrant_person = RegistrantPersonReviewChoices.APPROVE  # type: ignore
        self.review.registrant_permission = RegistrantPermissionReviewChoices.APPROVE  # type: ignore
        self.review.policy_exemption = PolicyExemptionReviewChoices.APPROVE  # type: ignore
        self.review.domain_name_rules = DomainNameRulesReviewChoices.APPROVE  # type: ignore
        self.review.registrant_senior_support = RegistrantSeniorSupportReviewChoices.APPROVE  # type: ignore
        self.review.registrar_details = RegistrarDetailsReviewChoices.APPROVE  # type: ignore

        self.review.registry_details_notes = "a"  # type: ignore
        self.review.registrant_org_notes = "a"  # type: ignore
        self.review.registrant_person_notes = "a"  # type: ignore
        self.review.registrant_permission_notes = "a"  # type: ignore
        self.review.policy_exemption_notes = "a"  # type: ignore
        self.review.domain_name_rules_notes = "a"  # type: ignore
        self.review.registrant_senior_support_notes = "a"  # type: ignore
        self.review.registrar_details_notes = "a"  # type: ignore

    def test_review_approval(self):
        """
        Test the approval
        """
        approve_response = self.c.post(
            get_admin_change_view_url(self.review),  # type: ignore
            data={
                "reason": "a",
                "_approve": "APPROVE",
                "registry_details": RegistryDetailsReviewChoices.APPROVE,
                "registry_details_notes": "a",
                "registrant_org": RegistrantOrgReviewChoices.APPROVE,
                "registrant_org_notes": "a",
                "registrant_person": RegistrantPersonReviewChoices.APPROVE,
                "registrant_person_notes": "a",
                "registrant_permission": RegistrantPermissionReviewChoices.APPROVE,
                "registrant_permission_notes": "a",
                "policy_exemption": PolicyExemptionReviewChoices.APPROVE,
                "policy_exemption_notes": "a",
                "domain_name_rules": DomainNameRulesReviewChoices.APPROVE,
                "domain_name_rules_notes": "a",
                "registrant_senior_support": RegistrantSeniorSupportReviewChoices.APPROVE,
                "registrant_senior_support_notes": "a",
                "registrar_details": RegistryDetailsReviewChoices.APPROVE,
                "registrar_details_notes": "a",
                "domain_name_availability": RegistryDetailsReviewChoices.APPROVE,
                "domain_name_availability_notes": "a",
            },
            follow=True,
        )

        self.assertContains(approve_response, "Reason for approval: a")

    def test_review_rejection(self):
        """
        Test the rejection
        """
        approve_response = self.c.post(
            get_admin_change_view_url(self.review),
            data={
                "reason": "a",
                "_approve": "APPROVE",
                "registry_details": RegistryDetailsReviewChoices.REJECT,
                "registry_details_notes": "a",
                "registrant_org": RegistrantOrgReviewChoices.APPROVE,
                "registrant_org_notes": "a",
                "registrant_person": RegistrantPersonReviewChoices.APPROVE,
                "registrant_person_notes": "a",
                "registrant_permission": RegistrantPermissionReviewChoices.APPROVE,
                "registrant_permission_notes": "a",
                "policy_exemption": PolicyExemptionReviewChoices.APPROVE,
                "policy_exemption_notes": "a",
                "domain_name_rules": DomainNameRulesReviewChoices.APPROVE,
                "domain_name_rules_notes": "a",
                "registrant_senior_support": RegistrantSeniorSupportReviewChoices.APPROVE,
                "registrant_senior_support_notes": "a",
                "registrar_details": RegistryDetailsReviewChoices.APPROVE,
                "registrar_details_notes": "a",
                "domain_name_availability": RegistryDetailsReviewChoices.APPROVE,
                "domain_name_availability_notes": "a",
            },
            follow=True,
        )

        self.assertContains(
            approve_response, "This application can&#x27;t be approved!"
        )

    def test_review_missing_notes(self):
        """
        Test the missing rejection
        """
        approve_response = self.c.post(
            get_admin_change_view_url(self.review),
            data={
                "reason": "a",
                "_approve": "APPROVE",
                "registry_details": RegistryDetailsReviewChoices.APPROVE,
                "registry_details_notes": "",
                "registrant_org": RegistrantOrgReviewChoices.APPROVE,
                "registrant_org_notes": "a",
                "registrant_person": RegistrantPersonReviewChoices.APPROVE,
                "registrant_person_notes": "a",
                "registrant_permission": RegistrantPermissionReviewChoices.APPROVE,
                "registrant_permission_notes": "a",
                "policy_exemption": PolicyExemptionReviewChoices.APPROVE,
                "policy_exemption_notes": "a",
                "domain_name_rules": DomainNameRulesReviewChoices.APPROVE,
                "domain_name_rules_notes": "a",
                "registrant_senior_support": RegistrantSeniorSupportReviewChoices.APPROVE,
                "registrant_senior_support_notes": "a",
                "registrar_details": RegistryDetailsReviewChoices.APPROVE,
                "registrar_details_notes": "a",
                "domain_name_availability": RegistryDetailsReviewChoices.APPROVE,
                "domain_name_availability_notes": "a",
            },
            follow=True,
        )

        self.assertContains(approve_response, "Please correct the error below.")

    def test_review_missing_reason(self):
        """
        Test the missing reason rejection
        """
        approve_response = self.c.post(
            get_admin_change_view_url(self.review),
            data={
                "reason": "",
                "_approve": "APPROVE",
                "registry_details": RegistryDetailsReviewChoices.APPROVE,
                "registry_details_notes": "a",
                "registrant_org": RegistrantOrgReviewChoices.APPROVE,
                "registrant_org_notes": "a",
                "registrant_person": RegistrantPersonReviewChoices.APPROVE,
                "registrant_person_notes": "a",
                "registrant_permission": RegistrantPermissionReviewChoices.APPROVE,
                "registrant_permission_notes": "a",
                "policy_exemption": PolicyExemptionReviewChoices.APPROVE,
                "policy_exemption_notes": "a",
                "domain_name_rules": DomainNameRulesReviewChoices.APPROVE,
                "domain_name_rules_notes": "a",
                "registrant_senior_support": RegistrantSeniorSupportReviewChoices.APPROVE,
                "registrant_senior_support_notes": "a",
                "registrar_details": RegistryDetailsReviewChoices.APPROVE,
                "registrar_details_notes": "a",
                "domain_name_availability": RegistryDetailsReviewChoices.APPROVE,
                "domain_name_availability_notes": "a",
            },
            follow=True,
        )

        self.assertContains(approve_response, "Please correct the error below.")


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
