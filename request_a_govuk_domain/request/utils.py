import logging
import os
import uuid
from typing import List

import clamd
from django.conf import settings
from django.core.exceptions import ValidationError
from notifications_python_client import NotificationsAPIClient

from request_a_govuk_domain.request.models.storage_util import select_storage

logger = logging.getLogger(__name__)


def handle_uploaded_file(file, session_id):
    """
    How and where to save a file that the user has uploaded

    :param file: a File object
    :param session_id for the current session
    :return: the name of the file as store on the server
    """

    _, file_extension = os.path.splitext(file.name)

    saved_filename = f"{session_id}/{uuid.uuid4()}{file_extension}"
    storage = select_storage()
    if not settings.IS_AWS:
        file_path = os.path.join(settings.MEDIA_ROOT, saved_filename)
    else:
        file_path = saved_filename
    logger.info(f"Saving {file.name} in to {file_path}")
    storage.save(file_path, file)
    return saved_filename


def validate_file_infection(file):
    """
    Incoming file is sent to clamd for scanning.
    Raises a ValidationError
    """
    if not settings.IS_AWS:
        cd = clamd.ClamdNetworkSocket(
            settings.CLAMD_TCP_ADDR, settings.CLAMD_TCP_SOCKET
        )
        result = cd.instream(file)

        if result and result["stream"][0] == "FOUND":
            raise ValidationError("File is infected with malware.", code="infected")
    else:
        logger.warning("Clam is not enabled on AWS")


def route_number(session_data: dict) -> dict[str, int]:
    route = {}
    registrant_type = session_data.get("registrant_type")
    if registrant_type is not None:
        if registrant_type in ["parish_council", "village_council"]:
            route["primary"] = 1
            if session_data.get("domain_confirmation") == "no":
                route["secondary"] = 12
        elif registrant_type in ["central_government", "ndpb"]:
            route["primary"] = 2
            domain_purpose = session_data.get("domain_purpose")
            if domain_purpose is not None:
                if domain_purpose in ["email-only"]:
                    route["secondary"] = 5
                    if session_data.get("minister") == "no":
                        route["tertiary"] = 8
                elif domain_purpose in ["website-email"]:
                    route["secondary"] = 7
                else:
                    route["secondary"] = 6
                    if session_data.get("written_permission") == "no":
                        route["tertiary"] = 9
        elif registrant_type in [
            "local_authority",
            "fire_service",
            "combined_authority",
            "pcc",
            "joint_authority",
            "joint_committee",
            "representing_psb",
            "representing_profession",
        ]:
            route["primary"] = 3
            if session_data.get("written_permission") == "no":
                route["secondary"] = 10
        else:
            route["primary"] = 4

    return route


def is_central_government(registrant_type: str) -> bool:
    """
    Check if the registrant type is Central Government or Non-departmental body
    Note: If above is True then registrant type will be considered as Central Government
    """
    return registrant_type in ["central_government", "ndpb"]


def add_to_session(form, request, field_names: List[str]) -> dict:
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
    return registration_data


def add_value_to_session(request, field_name: str, field_value) -> None:
    registration_data = request.session.get("registration_data", {})
    registration_data[field_name] = field_value
    request.session["registration_data"] = registration_data


def remove_from_session(session, field_names: List[str]) -> dict:
    """
    Remove fields from a session, for instance when an uploaded
    file is removed
    """
    for field_name in field_names:
        if session["registration_data"].get(field_name) is not None:
            if field_name.endswith("uploaded_filename"):
                # remove the file associated
                select_storage().delete(session["registration_data"].get(field_name))
            del session["registration_data"][field_name]

    return session["registration_data"]


def get_env_variable(key: str, default=None) -> str:
    """
    Utility to get the environment variable

    param: key - environment variable name in .env file
    param: default - default value if environment variable not found

    :return: value - environment variable value
    """
    return os.getenv(key, default)


def translate_notify_missing_service_id_error(e):
    """
    If the Notify API key is invalid, then Notify API throws an error message saying "Missing service ID" which is
    not very clear. This method is to translate that message to more clear message ""Notify API key seems
    invalid"
    """
    error_type = type(e).__name__
    error_message = str(e)
    if error_type == "AssertionError" and error_message == "Missing service ID":
        raise ValueError("Notify API key seems invalid") from e


def send_email(email_address: str, template_id: str, personalisation: dict) -> None:
    """
    Method to send email using Notify API

    param: email_address: Email address of the recipient
    param: template_id: Template id of the Email Template
    param: personalisation: Dictionary of Personalisation data
    """
    notify_api_key = get_env_variable("NOTIFY_API_KEY")

    # If api key is found then send email, else log that it was not found
    if notify_api_key:
        try:
            notifications_client = NotificationsAPIClient(notify_api_key)
            notifications_client.send_email_notification(
                email_address=email_address,
                template_id=template_id,
                personalisation=personalisation,
            )
        except Exception as e:
            translate_notify_missing_service_id_error(e)
            raise e
    else:
        logger.info("Not sending email as Notify API key not found")
