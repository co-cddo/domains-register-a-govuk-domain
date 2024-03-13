import os
import csv
from typing import List

from django.conf import settings


def handle_uploaded_file(file):
    file_path = os.path.join(settings.MEDIA_ROOT, file.name)
    with open(file_path, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def organisations_list() -> list:
    """
    Hard coded path for now
    (
        ("Unread", ("Unread")),
        ("Read", ("Read"))
    )
    """
    csv_filename = os.path.join(
        os.getcwd(), "request_a_govuk_domain", "input/organisations.csv"
    )
    data: list[tuple[str, str]] = [("", "Select your organisation from the list")]
    with open(csv_filename) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data.append((row[0], (row[0])))
    return data


def is_central_government(registrant_type: str) -> bool:
    """
    Check if the registrant type is Central Government or Non-departmental body
    Note: If above is True then registrant type will be considered as Central Government
    """
    return registrant_type in ["central_government", "ndpb"]


def add_to_session(form, request, field_names: List[str]) -> str:
    """
    Common utility method to clean the list of fields and save them in the session. This is to save boilerplate code.

    :param form: form object
    :param request: request object
    :param field_names: list of field names to be cleaned and saved in the session

    :return: A tuple of cleaned field value and registration data
    """
    registration_data = request.session.get("registration_data", {})
    for field_name in field_names:
        field_value = form.cleaned_data[field_name]
        registration_data[field_name] = field_value
    request.session["registration_data"] = registration_data
    return field_value, registration_data
