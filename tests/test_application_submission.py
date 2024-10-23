import concurrent
import functools
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from unittest.mock import Mock, patch

from django.db import connection
from django.test import TransactionTestCase

from request_a_govuk_domain.request.models import Registrar, Application
from request_a_govuk_domain.request.views import ConfirmView


def release_connection(wrapped_function):
    # Decorator to release connection at the end.
    # This should be usd to wrap the function that runs in a thread.
    # There is a Django issue, that does not cose the connection if used within a thread pool
    # https://stackoverflow.com/questions/44802617/database-is-being-accessed-by-other-users-error-when-using-threadpoolexecutor
    # https://james.lin.net.nz/2016/04/22/make-sure-you-are-closing-the-db-connections-after-accessing-django-orm-in-your-threads/
    #
    @functools.wraps(wrapped_function)
    def _release_connection(*args, **kwargs) -> Any:
        try:
            return wrapped_function(*args, **kwargs)
        finally:
            connection.close()

    return _release_connection


class ServiceFailureErrorHandlerTests(TransactionTestCase):
    def setUp(self):
        self.registrar = Registrar.objects.create(name="dummy registrar")
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

    def test_application_submit_saved(self):
        """
        If the token in the url does matches the one in the session,
        then application saved.
        :return:
        """
        s = self.client.session
        s.update(
            {
                "registration_data": self.registration_data,
                "application_reference": "GOVUK20062024QTLV",
            }
        )
        s.save()
        with self.assertLogs() as ctx_:
            res = self.client.post("/confirm/", data={})
            self.assertIn(
                f"INFO:request_a_govuk_domain.request.views:Saving form {s.session_key}",
                ctx_.output,
            )
            self.assertEqual(302, res.status_code)
            self.assertEqual(1, Application.objects.count())

    def test_application_success_page_only_works_for_existing_applications(self):
        """
        Success page returns 200 status when correct reference is passed
        :return:
        """
        s = self.client.session
        s.update(
            {
                "registration_data": self.registration_data,
                "application_reference": "GOVUK20062024QTLV",
            }
        )
        s.save()
        with self.assertLogs() as ctx_:
            res = self.client.post("/confirm/", data={})
            self.assertIn(
                f"INFO:request_a_govuk_domain.request.views:Saving form {s.session_key}",
                ctx_.output,
            )
            self.assertEqual(302, res.status_code)
            self.assertEqual(1, Application.objects.count())

            res = self.client.get("/success/")
            self.assertEqual(200, res.status_code)

    def test_application_success_page_raise_error_for_invalid_reference(self):
        """
        Success page returns 400 status if called outside the process
        :return:
        """
        s = self.client.session
        s.update(
            {
                "registration_data": self.registration_data,
                "application_reference": "GOVUK20062024QTLV",
            }
        )
        s.save()
        with self.assertLogs() as ctx_:
            res = self.client.post("/confirm/", data={}, follow=True)
            self.assertIn(
                f"INFO:request_a_govuk_domain.request.views:Saving form {s.session_key}",
                ctx_.output,
            )
            self.assertEqual(200, res.status_code)
            self.assertEqual(1, Application.objects.count())
            # Application reference will be cleand up from the session after success page
            self.assertIsNone(self.client.session.get("application_reference"))

            # Simulate accessing the success page after the process has completed
            res = self.client.get("/success/", follow=True)

            self.assertEqual(400, res.status_code)

    def test_application_submit_only_saved_once_on_concurrent_submits(self):
        """
        Make sure we only create one application in the database even if the user sends multiple
        concurrent submits - multiple click on submit button
        :return:
        """

        @release_connection
        def make_request():
            class SessionDict(dict):
                def __init__(self, *k, **kwargs):
                    self.__dict__ = self
                    super().__init__(*k, **kwargs)
                    self.session_key = "session-key"

            mock_request = Mock()
            mock_request.session = SessionDict(
                {
                    "registration_data": self.registration_data,
                    "application_reference": "GOVUK20062024QTLV",
                }
            )
            return ConfirmView().post(mock_request)

        num_threads = 5
        with ThreadPoolExecutor() as executor:
            features = [executor.submit(make_request) for i in range(num_threads)]
            concurrent.futures.wait(features)
        exception_count = 0
        success_count = 0
        for feature in features:
            if feature._result:
                success_count += 1
            elif feature._exception:
                exception_count += 1
        # Only one will succeed
        self.assertEqual(1, success_count)
        # Remaining duplicate submissions will fail
        self.assertEqual(4, exception_count)
        # Only one application will be saved int the database
        self.assertEqual(1, Application.objects.count())

    def test_unhandled_errors_are_treated_as_500(self):
        """
        Any error in creating the application is passed on as an internal server error.
        :return:
        """

        class SessionDict(dict):
            def __init__(self, *k, **kwargs):
                self.__dict__ = self
                super().__init__(*k, **kwargs)
                self.session_key = "session-key"

        with self.assertRaises(Exception):
            mock_request = Mock()
            mock_request.session = SessionDict({})
            # Try to save the application without any session data
            mock_request.POST = {}
            return ConfirmView().post(mock_request)

    def test_application_success(self):
        """
        On multiple clicks, we avoid saving same application to DB.
        Test to confirm multiple clicks won't throw 500 error
        :return:
        """

        with patch(
            "request_a_govuk_domain.request.views.ConfirmView.save_application_to_database_and_send_confirmation_email"
        ) as mock_save:
            mock_save.return_value = True
            res = self.client.post("/confirm/", data={})

        self.assertEqual(302, res.status_code)
