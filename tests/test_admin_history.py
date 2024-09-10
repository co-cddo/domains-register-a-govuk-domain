from time import sleep
from unittest.mock import Mock

from django.test import TestCase

from request_a_govuk_domain.request import db
from request_a_govuk_domain.request.models import Review
from tests.util import (
    AdminScreenTestMixin,
    SessionDict,
    get_admin_history_view_url,
    get_response_content,
    get_admin_change_view_url,
)


class SimpleHistoryTest(AdminScreenTestMixin, TestCase):
    def test_application_history(self):
        """
        Test the application approval creates the relevant history records.
        - A record with status 'New' created when the application is created
        - A record with status 'Approved' created when the application is approved
        :return:
        """
        request = Mock()
        request.session = SessionDict({"registration_data": self.registration_data})

        # Simulate application creation through client screens
        application = db.save_data_in_database("ABCDEFGHIJK", request)
        sleep(1)

        # Simulate 1st review user interaction.
        # Now we review the last application created by the client
        review = Review.objects.filter(
            application__reference=application.reference
        ).first()

        review_response = self.admin_client.post(
            get_admin_change_view_url(review),
            {
                "_approve": "true",
                "registrar_details": "approve",
                "registrar_details_notes": "I approve",
                "domain_name_availability": "approve",
                "domain_name_availability_notes": "I approve",
                "registrant_org": "approve",
                "registrant_org_notes": "I approve",
                "registrant_person": "approve",
                "registrant_person_notes": "I approve",
                "domain_name_rules": "approve",
                "domain_name_rules_notes": "I approve",
                "registry_details": "approve",
                "registry_details_notes": "I approve",
                "reason": "Looks good to me",
            },
            follow=True,
        )

        # raise Exception(f"Review id is {review.id}, redirect chain {review_response.redirect_chain[0][0]}")
        self.admin_client.post(
            review_response.redirect_chain[0][0],
            {"action": "approval", "obj_id": application.id, "_confirm": "Confirm"},
        )
        response = self.admin_client.get(get_admin_history_view_url(review))
        self.assertEqual(response.status_code, 200)
        content = get_response_content(response)
        history_records = list(application.history.all().order_by("-history_id"))
        # the final record is present at the top
        self.assertInHTML(
            f"""
            <tr>
            <td>
            <a href="/admin/request/application/{application.id}/history/{history_records[0].history_id}/">
            {history_records[0].history_date.strftime('%b. %d, %Y, %I:%M %p')}
            </a>
            </td>
            <td>
            <a href="/admin/auth/user/{self.superuser.pk}/change/">superuser (owner)</a>
            </td>
            <td>
            Approved
            </td>
            </tr>
        """,
            content,
            msg_prefix=content,
        )
        # Initial record creation is present at the bottom
        self.assertInHTML(
            f"""
            <tr>
            <td>
            <a href="/admin/request/application/{application.id}/history/{history_records[-1].history_id}/">
            {history_records[-1].history_date.strftime('%b. %d, %Y, %I:%M %p')}
            </a>
            </td><td>
            -
            </td><td>
            New
            </td>
            </tr>
        """,
            content,
            msg_prefix=content,
        )
