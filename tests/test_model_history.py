from unittest.mock import Mock

from django.test import TestCase

from request_a_govuk_domain.request import db
from request_a_govuk_domain.request.models import (
    Review,
    ApplicationStatus,
)
from tests.util import get_admin_change_view_url, SessionDict, AdminScreenTestMixin

from request_a_govuk_domain.request.models import Application


class CheckHistoryTestCase(AdminScreenTestMixin, TestCase):
    def test_application_history(self):
        """
        Test case to check that we load the correct application on the review screen.
        When we click on the item in the list, we load the correct data from the corresponding review steps.
        :return:
        """
        request = Mock()
        request.session = SessionDict({"registration_data": self.registration_data})

        # Simulate application creation through client screens
        status = db.save_data_in_database("ABCDEFGHIJK", request)
        print(f"{status=}")
        application = Application.objects.filter(reference="ABCDEFGHIJK")[0]

        # see the records in history table
        history = application.history.all()  # type: ignore
        self.assertEqual(len(history), 1)

        response = self.admin_client.get(get_admin_change_view_url(application))
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
        db.save_data_in_database("ABCDEFGHIJL", request)
        application = Application.objects.filter(reference="ABCDEFGHIJL")[0]

        # Now we review the last application created by the client
        review = Review.objects.filter(
            application__reference=application.reference
        ).first()

        # see the records in history table
        history = review.history.all()  # type: ignore
        self.assertEqual(len(history), 1)

        response = self.admin_client.get(get_admin_change_view_url(review))

        self.assertContains(response, "History")

        # change review field
        review.registrar_details_notes = "test"  # type: ignore
        review.save()  # type: ignore
        history = review.history.all()  # type: ignore
        self.assertEqual(len(history), 2)
