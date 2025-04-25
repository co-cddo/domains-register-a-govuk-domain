from unittest.mock import Mock
from freezegun import freeze_time

import parameterized
from django.test import TestCase


from request_a_govuk_domain.request import db
from request_a_govuk_domain.request.models import (
    Application,
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
from tests.util import AdminScreenTestMixin, SessionDict, get_admin_change_view_url


class ModelAdminTestCase(AdminScreenTestMixin, TestCase):
    @parameterized.parameterized.expand(
        [
            [None, "superuser", "superuser"],
            ["reviewer", "superuser", "reviewer"],
            ["superuser", "superuser", "superuser"],
        ],
        name_func=lambda testcase_func, param_num, param: "%s_%s"
        % (
            testcase_func.__name__,
            parameterized.parameterized.to_safe_name(
                "_".join(["owner_is", str(param.args[0]), "updated_by", param.args[1]]),
            ),
        ),
    )
    def test_last_modified_is_set_correctly(self, owner, changed_by, expected_owner):
        """
        Test the owner and last updated by fields are set correctly.
        :return:
        """
        request = Mock()
        request.session = SessionDict({"registration_data": self.registration_data})

        # Simulate application creation through client screens
        db.save_data_in_database("ABCDEFGHIJK", request)
        application = Application.objects.filter(reference="ABCDEFGHIJK")[0]

        # Application retrieval, check original condition
        response = self.admin_client.get(get_admin_change_view_url(application))
        self.assertIsNone(response.context_data["original"].owner)
        self.assertIsNone(response.context_data["original"].last_updated_by)

        data = self.get_application_update_json(application)
        if owner:
            data["owner"] = getattr(self, owner).id

        self.admin_client.post(
            get_admin_change_view_url(application),
            data=data,
            follow=True,
        )
        application.refresh_from_db()
        # Owner will be set to the value if given else will take the value of the updated user
        self.assertEqual(expected_owner, application.owner.username)
        # 'superuser' is the one last actioned on the data
        self.assertEqual(changed_by, application.last_updated_by.username)

    @parameterized.parameterized.expand(
        [
            ["approve", "Good Application", "approval", "approved_no_delay"],
            ["reject", "Bad Application", "rejection", "rejected_no_delay"],
        ]
    )
    def test_create_approval_works(self, status, reason, action, sub_status):
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
        db.save_data_in_database("ABCDEFGHIJG", request)
        application_to_approve = Application.objects.filter(reference="ABCDEFGHIJG")[0]

        # Now we review the last application created by the client
        review = Review.objects.filter(
            application__reference=application_to_approve.reference
        ).first()

        review.registry_details = RegistryDetailsReviewChoices.APPROVE  # type: ignore
        review.registrant_org = RegistrantOrgReviewChoices.APPROVE  # type: ignore
        review.registrant_person = RegistrantPersonReviewChoices.APPROVE  # type: ignore
        review.registrant_permission = RegistrantPermissionReviewChoices.APPROVE  # type: ignore
        review.policy_exemption = PolicyExemptionReviewChoices.APPROVE  # type: ignore
        review.domain_name_rules = DomainNameRulesReviewChoices.APPROVE  # type: ignore
        review.registrant_senior_support = RegistrantSeniorSupportReviewChoices.APPROVE  # type: ignore
        review.registrar_details = RegistrarDetailsReviewChoices.APPROVE  # type: ignore

        review.registry_details_notes = "a"  # type: ignore
        review.registrant_org_notes = "a"  # type: ignore
        review.registrant_person_notes = "a"  # type: ignore
        review.registrant_permission_notes = "a"  # type: ignore
        review.policy_exemption_notes = "a"  # type: ignore
        review.domain_name_rules_notes = "a"  # type: ignore
        review.registrant_senior_support_notes = "a"  # type: ignore
        review.registrar_details_notes = "a"  # type: ignore

        response = self.admin_client.get(get_admin_change_view_url(review))
        with self.subTest("Review screen shows correct parameters"):
            # Page title should display application reference and the domain name
            self.assertEqual(
                f"{application_to_approve.reference} - {application_to_approve.domain_name}",
                response.context_data["subtitle"],
            )
            # Addition check the ids are correctly assigned.
            # The id of the review should not be equal to the application
            # as we created one application outside the normal flow
            self.assertNotEqual(
                review.id,
                application_to_approve.id,
                "Id of the review should not be equal to the application id",
            )
            # Object id should be the same as the review id
            self.assertEqual(review.id, int(response.context_data["object_id"]))

        with self.subTest("Approving the review brings up the correct data"):
            approve_response = self.admin_client.post(
                get_admin_change_view_url(review),
                data={
                    "reason": reason,
                    f"_{status}": f"{status.capitalize()}",
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
            # Check that the data shown on the screen is from the correct application
            self.assertContains(
                approve_response,
                f"Send an email confirming the {action} to dummy_registrar_email-xx@gov.uk",
            )
            self.assertContains(approve_response, f"Reason for {action}: {reason}")

            # Make sure the id displayed on the url is the id if the application
            self.assertEqual(
                f"/admin/application_confirm/?obj_id={application_to_approve.id}&action={action}",
                approve_response.redirect_chain[0][0],
            )

        with self.subTest(
            "Confirming the application will change the status to approved"
        ):
            # All the parameters used below are validate in the previous step
            approve_response = self.admin_client.post(
                approve_response.redirect_chain[0][0],
                data={
                    "_confirm": "Confirm",
                    "action": f"{action}",
                    "obj_id": application_to_approve.id,
                    "sub_status": f"{sub_status}",
                },
                follow=True,
            )
            # Refresh from the database
            application_to_approve.refresh_from_db()
            self.assertEqual(
                f"{'approved' if action == 'approval' else 'rejected'}",
                application_to_approve.status,
            )
            self.assertContains(approve_response, f"{action.capitalize()} email sent")
            self.assertEqual(
                application_to_approve.last_updated_by.username, "superuser"
            )

            with self.subTest(f"Owner is set to {self.superuser.username}"):
                self.assertEqual(application_to_approve.owner.username, "superuser")

    def test_time_elapsed_correct(self):
        """
        Test to check if the time_elapsed function returns the expected result
        """
        request = Mock()
        request.session = SessionDict({"registration_data": self.registration_data})

        with freeze_time("2025-01-01"):
            db.save_data_in_database("ABCDEFGHIJG", request)
            application = Application.objects.filter(reference="ABCDEFGHIJG")[0]

        # wait 2 days
        with freeze_time("2025-01-03"):
            self.assertEqual(application.time_elapsed().days, 2)

        # wait another 3 days and approve
        with freeze_time("2025-01-06"):
            review = Review.objects.filter(
                application__reference=application.reference
            ).first()

            response = self.admin_client.post(
                get_admin_change_view_url(review),
                data={
                    "reason": "approved",
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

            self.admin_client.post(
                response.redirect_chain[0][0],
                data={
                    "_confirm": "Confirm",
                    "action": "approval",
                    "obj_id": application.id,
                    "sub_status": "approved_no_delay",
                },
                follow=True,
            )
            application.refresh_from_db()

            # Application has been closed, so time elapsed is time between created and now
            self.assertEqual(application.time_elapsed().days, 5)

        # wait some more
        with freeze_time("2025-01-20"):
            # Application has been closed, so time elapsed is time between created and when
            # it was closed, so same as above regardless of time since
            self.assertEqual(application.time_elapsed().days, 5)
