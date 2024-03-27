import base64

from django.test import TestCase
from django.core.exceptions import ValidationError

from six import BytesIO

from request_a_govuk_domain.request.utils import validate_file_infection


class FileInfectionTestCase(TestCase):
    def test_file_infection_fail(self):
        # test infected signature from calmd library
        infected_signature = base64.b64decode(
            b"WDVPIVAlQEFQWzRcUFpYNTQoUF4pN0NDKTd9JEVJQ0FSLVNUQU5EQVJELUFOVElWSVJVUy1URVNU\nLUZJTEUhJEgrSCo=\n"  # pragma: allowlist secret
        )
        with self.assertRaises(ValidationError):
            validate_file_infection(BytesIO(infected_signature))

    def test_file_infection_success(self):
        test = base64.b64decode(b"test")
        self.assertIsNone(validate_file_infection(BytesIO(test)))
