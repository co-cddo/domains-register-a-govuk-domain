import os
import uuid
from typing import List
from django.conf import settings


def handle_uploaded_file(file):
    """
    How and where to save a file that the user has uploaded

    :param file: a File object
    :return: the name of the file as store on the server
    """
    _, file_extension = os.path.splitext(file.name)

    saved_filename = f"{uuid.uuid4()}{file_extension}"

    file_path = os.path.join(settings.MEDIA_ROOT, saved_filename)
    with open(file_path, "wb") as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    return saved_filename


def create_summary_list(registration_data):
    summary_list = [
        {"summary_key": "Organisation type", "summary_value": registration_data.get('registrant_type', ''), "change_url": "registrant_type"},
        {"summary_key": "Organisation name", "summary_value": registration_data.get('registrant_organisation_name', ''), "change_url": "registrant"},
        {"summary_key": "Registrant's written permission", "summary_value": f"{registration_data.get('written_permission', '')}, evidence provided.", "change_url": "written_permission_upload"},
        {"summary_key": "Domain name", "summary_value": registration_data.get('domain_name', ''), "change_url": "domain"}
    ]
    if 'registrant_type' in registration_data and registration_data["registrant_type"] == "central_government":
        summary_list.insert(2, {"summary_key": "Reason for request", "summary_value": registration_data.get('domain_purpose', ''), "change_url": "domain_purpose"})
        summary_list.insert(3, {"summary_key": "Exemption from GOV.UK website", "summary_value": f"{registration_data.get('exe_radio', '')}, evidence provided.", "change_url": "exemption_upload"})
        summary_list.insert(6, {"summary_key": "Minister's support", "summary_value": f"{registration_data.get('minister_radios', '')}, evidence provided.", "change_url": "minister_upload"})

    return summary_list


class RegistrationDataClass:
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)


def is_central_government(registrant_type: str) -> bool:
    """
    Check if the registrant type is Central Government or Non-departmental body
    Note: If above is True then registrant type will be considered as Central Government
    """
    return registrant_type in ["central_government", "ndpb"]


def add_to_session(form, request, field_names: List[str]) -> tuple:
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


def remove_from_session(session, field_names: List[str]) -> None:
    """
    Remove fields from a session, for instance when an uploaded
    file is removed
    """
    for field_name in field_names:
        if session["registration_data"].get(field_name) is not None:
            session["registration_data"][field_name] = None
