from datetime import datetime
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from request_a_govuk_domain.request import db
from request_a_govuk_domain.request.admin.model_admins import ApplicationAdmin
from request_a_govuk_domain.request.models import Application, Registrar


class ModelAdminActionsTestCase(TestCase):
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

        User.objects.create_superuser(
            username="superuser",
            password="secret",  # pragma: allowlist secret
            email="admin@example.com",
        )

    def test_file_is_downloaded(self):
        request = Mock()
        request.session = SessionDict({"registration_data": self.registration_data})
        db.save_data_in_database("ABCDEFGHIJK", request)
        app = Application.objects.filter(reference="ABCDEFGHIJK")[0]
        c = Client()
        c.login(username="superuser", password="secret")  # pragma: allowlist secret

        # Patch get_business_days_to_complete to return a value
        with patch.object(ApplicationAdmin, "get_business_days_to_complete", return_value=5):
            response = c.post(
                reverse(
                    "admin:request_application_changelist",
                ),
                data={
                    "action": "export",
                    "_selected_action": [app.pk],
                },
                follow=True,
            )

            self.assertEqual(
                response.get("Content-Disposition"),
                f"attachment; filename=request.application_{datetime.today().strftime('%Y-%m-%d')}_data_backup.csv",
            )

            self.assertContains(response, "reference")
            self.assertContains(response, "ABCDEFGHIJK")
            # Check if the business days to complete is included in the export
            self.assertContains(response, "Business days to complete")
            self.assertContains(response, "5")


class SessionDict(dict):
    def __init__(self, *k, **kwargs):
        self.__dict__ = self
        super().__init__(*k, **kwargs)
        self.session_key = "session-key"
