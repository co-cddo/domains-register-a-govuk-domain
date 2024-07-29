import re

from django.core.exceptions import ValidationError


class BaseValidator:
    def __init__(self, error_message=None):
        self.error_message = error_message


class PhoneNumberValidator(BaseValidator):
    phone_number_pattern = re.compile(r"^\s*0(?:\s*\d){9,10}\s*$")

    def __call__(self, phone_number):
        if re.fullmatch(self.phone_number_pattern, phone_number) is None:
            raise ValidationError(self.error_message)


class NonEmptyValidator(BaseValidator):
    def __call__(self, txt: str):
        if not txt or not txt.strip():
            raise ValidationError(self.error_message)
