import datetime
import zoneinfo
from unittest.mock import Mock, call, patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from parameterized import parameterized

from request_a_govuk_domain.request import db
from request_a_govuk_domain.request.admin.model_admins import convert_to_local_time
from request_a_govuk_domain.request.models import Application, Registrar


class ModelAdminTestCase(TestCase):
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

    def test_bst_time_is_converted_correctly(self):
        """
        Zero GMT should be converted to 1AM local time as we are in BST
        :return:
        """
        bst_date = datetime.datetime(2024, 5, 1, 0, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo(key="GMT"))
        self.assertEqual("01 May 2024 01:00:00 AM", convert_to_local_time(bst_date))

    def test_gmt_time_is_converted_correctly(self):
        """
        Zero GMT should not be converted as the time zone is GMT in November
        :return:
        """
        gmt_date = datetime.datetime(2024, 11, 1, 0, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo(key="GMT"))
        self.assertEqual("01 Nov 2024 00:00:00 AM", convert_to_local_time(gmt_date))

    @parameterized.expand(
        [
            ["new_document.pdf", "new_document.pdf"],
            ["new document.pdf", "new_document.pdf"],
            [
                "new -document _with more ' spaces.pdf",
                "new_document_with_more_spaces.pdf",
            ],
        ]
    )
    def test_file_is_uploaded_from_admin_screen(self, file_name, expected_name):
        request = Mock()
        request.session = SessionDict({"registration_data": self.registration_data})
        db.save_data_in_database("ABCDEFGHIJK", request)
        app = Application.objects.filter(reference="ABCDEFGHIJK")[0]
        c = Client()
        c.login(username="superuser", password="secret")  # pragma: allowlist secret

        written_permission_evidence = SimpleUploadedFile(file_name, b"file_content", content_type="application/pdf")
        with patch("request_a_govuk_domain.request.models.application.S3_STORAGE_ENABLED", True):
            with patch("request_a_govuk_domain.request.models.application.select_storage") as mock_select_storage:
                mock_storage = Mock()
                mock_storage.bucket_name = "mock-data-bucket"
                mock_select_storage.return_value = mock_storage
                # run test
                response = c.post(
                    get_admin_change_view_url(app),
                    data={
                        "written_permission_evidence": written_permission_evidence,
                        "reference": app.reference,
                        "time_decided_0": "2024-06-24",
                        "time_decided_1": "12:00",
                        "status": app.status,
                        "domain_name": app.domain_name,
                        "registrar_person": app.registrar_person.id,
                        "registrant_person": app.registrant_person.id,
                        "registry_published_person": app.registry_published_person.id,
                        "registrant_org": app.registrant_org.id,
                        "registrar_org": app.registrar_org.id,
                    },
                    follow=True,
                )

        mock_storage.assert_has_calls(
            [
                call.connection.meta.client.put_object(
                    Bucket="mock-data-bucket",
                    Key=f"temp_files/{file_name}",
                    Body=b"file_content",
                ),
                call.connection.meta.client.copy_object(
                    Bucket="mock-data-bucket",
                    CopySource=f"mock-data-bucket/temp_files/{file_name}",
                    Key=f"applications/ABCDEFGHIJK/{expected_name}",
                ),
                call.delete(f"temp_files/{file_name}"),
            ]
        )
        self.assertEqual(response.status_code, 200)


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
