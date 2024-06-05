import logging
import os
import uuid

import clamd
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.contrib.sessions.backends.db import SessionStore
from notifications_python_client import NotificationsAPIClient

from request_a_govuk_domain.request.models import RegistrantTypeChoices
from request_a_govuk_domain.request.models.storage_util import select_storage

logger = logging.getLogger(__name__)

# The translation map translates the yes/no value stored in the session to human-readable values that will be shown
# in the emails. The translated values are based on what gets shown on the "Answers" page in the front-end
YES_NO_TRANSLATION_MAP = {
    "yes": "Yes, evidence provided",
    "no": "No evidence provided",
}

# The translation map translates the domain purpose value stored in the session to human-readable values that will
# be shown in the emails. The translated values are based on what gets shown on the "Answers" page in the front-end
DOMAIN_PURPOSE_TRANSLATION_MAP = {
    "website-email": "Website (may include email)",
    "email-only": "Email only",
}


def handle_uploaded_file(file: UploadedFile, session_id: str | None) -> str | None:
    """
    How and where to save a file that the user has uploaded

    :param file: a File object
    :param session_id for the current session
    :return: the name of the file as store on the server
    """
    if file.name is None:
        return None

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
    if settings.IS_SCANNING_ENABLED:
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
        elif registrant_type in ["central_government", "alb"]:
            route["primary"] = 2
            domain_purpose = session_data.get("domain_purpose")
            if domain_purpose is not None:
                if domain_purpose in ["email-only"]:
                    route["secondary"] = 5
                elif domain_purpose in ["website-email"]:
                    route["secondary"] = 7
                else:
                    route["secondary"] = 6
                    if session_data.get("written_permission") == "no":
                        route["tertiary"] = 9
            if session_data.get("minister") == "no":
                route["tertiary"] = 8

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
    # Override the secondary route so we always go to domain selection if the confirmation is not present
    if session_data.get("domain_confirmation") == "no":
        route["secondary"] = 12
    return route


def is_valid_session_data(rd: dict) -> bool:
    """
    check that registration data contained in a session dictionary is correct or note.
    Depending on the route taken by the users, some session fields should be present or not,
    or have specific value.
    :param rd: registration data as a dictionary
    :return: true is the data is valid, false otherwise
    """

    def not_str(field_name) -> bool:
        return not isinstance(rd.get(field_name), str)

    route = route_number(rd)
    if (
        not_str("domain_name")
        or not_str("registrar_name")
        or not_str("registrant_organisation")
        or not_str("registrant_full_name")
        or not_str("registrant_phone")
        or not_str("registrant_email")
        or not_str("registrant_role")
        or not_str("registrant_contact_email")
    ):
        return False
    if not rd.get("registrant_type") in [
        "central_government",
        "alb",
        "parish_council",
        "local_authority",
        "fire_service",
        "village_council",
        "combined_authority",
        "pcc",
        "joint_authority",
        "joint_committee",
        "psb_group",
        "psb_profession",
    ]:
        return False

    # Minister. Must be "yes" or "no" on route 2 and 8, otherwise None
    if route.get("primary") == 2:
        if rd.get("minister") not in ["yes", "no"]:
            return False
        if rd.get("minister") == "yes" and (
            not_str("minister_file_uploaded_filename")
            or not_str("minister_file_original_filename")
            or not_str("minister_file_uploaded_url")
        ):
            return False
    else:
        if rd.get("minister") is not None:
            return False

    # Exemption
    if route.get("primary") == 2 and route.get("secondary") == 7:
        if rd.get("exemption") != "yes":
            return False
        if (
            not_str("exemption_file_uploaded_filename")
            or not_str("exemption_file_original_filename")
            or not_str("exemption_file_uploaded_url")
        ):
            return False

    # written permission
    if (
        route.get("primary") == 3
        or (route.get("primary") == 2 and route.get("secondary") == 5)
        or (route.get("primary") == 2 and route.get("secondary") == 7)
    ):
        if rd.get("written_permission") != "yes":
            return False
        if (
            not_str("written_permission_file_uploaded_filename")
            or not_str("written_permission_file_original_filename")
            or not_str("written_permission_file_uploaded_url")
        ):
            return False
    return True


def add_to_session(form, request, field_names: list[str]) -> dict:
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


def remove_from_session(session: SessionStore, field_names: list[str]) -> dict:
    """
    Remove fields from a session, for instance when an uploaded
    file is removed
    """
    rd = session.get("registration_data")
    if session and session.session_key and rd:
        for field_name in field_names:
            if rd.get(field_name) is not None:
                del session["registration_data"][field_name]

        return rd
    else:
        return {}


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
    # This check is necessary for github actions ( where "NOTIFY_API_KEY" is not set and during build all the
    # cypress tests would fail where they reach Application submitted page, where the application will try to
    # send mail ). It is also needed for local environment if "NOTIFY_API_KEY" is not set
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
        if get_env_variable("ENVIRONMENT") == "prod":
            raise ValueError("Notify API key not found in Production environment")
        logger.info("Not sending email as Notify API key not found")


def personalisation(
    reference: str, registration_data: dict[str, str | None]
) -> dict[str, str | None]:
    """
    Creates personalisation dictionary to be used in the GovUK Notify templates

    :param reference: application reference
    :param registration_data: registration/application data

    :return: personalisation dictionary to be used in the GovUK Notify templates
    """
    domain_purpose = registration_data.get("domain_purpose")
    domain_purpose_personalisation = (
        DOMAIN_PURPOSE_TRANSLATION_MAP.get(domain_purpose) if domain_purpose else None
    )

    exemption = registration_data.get("exemption")
    exemption_personalisation = (
        YES_NO_TRANSLATION_MAP.get(exemption) if exemption else None
    )

    written_permission = registration_data.get("written_permission")
    written_permission_personalisation = (
        YES_NO_TRANSLATION_MAP.get(written_permission) if written_permission else None
    )

    minister = registration_data.get("minister")
    minister_personalisation = (
        YES_NO_TRANSLATION_MAP.get(minister) if minister else None
    )

    return {
        "domain_name": registration_data["domain_name"],
        "reference": reference,
        "registrar_name": registration_data["registrar_name"],
        "registrant_type": RegistrantTypeChoices.get_label(
            registration_data["registrant_type"]
        ),
        "domain_purpose": domain_purpose_personalisation,
        "exemption": exemption_personalisation,
        "written_permission": written_permission_personalisation,
        "minister": minister_personalisation,
        "registrant_organisation": registration_data["registrant_organisation"],
        "registrant_full_name": registration_data["registrant_full_name"],
        "registrant_phone": registration_data["registrant_phone"],
        "registrant_email": registration_data["registrant_email"],
        "registrant_role": registration_data["registrant_role"],
        "registrant_contact_email": registration_data["registrant_contact_email"],
    }


def route_specific_email_template(
    email_type: str, registration_data: dict[str, str]
) -> str:
    """
    Derive the email template based on email type ( confirmation/approval/rejection ) and route (central government/
    parish council etc.) derived from registration data

    :param email_type: email type (confirmation/approval/rejection)
    :param registration_data: registration/application data

    :return: email template
    """
    route = route_number(registration_data)
    if route["primary"] in [1, 3]:
        route_specific_email_template = f"{email_type}-{route['primary']}"
    else:
        route_specific_email_template = (
            f"{email_type}-{route['primary']}-{route['secondary']}"
        )
    return route_specific_email_template
