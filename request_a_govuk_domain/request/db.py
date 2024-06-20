"""
Database interaction module for Register App.

This module provides functions for interacting with the database in Register App.
"""

import logging
from django.db import transaction

from request_a_govuk_domain.request.models import (
    Registrant,
    Registrar,
    Application,
    RegistrarPerson,
    RegistrantPerson,
    RegistryPublishedPerson,
    Review,
)
from .models.storage_util import select_storage

from .utils import route_number, is_valid_session_data

logger = logging.getLogger(__name__)


def sanitised_registration_data(rd: dict, session_id: str) -> dict:
    """
    Remove the fields in registration data that aren't relevant to the
    answers the user has entered

    This can happen if the user has changed their answer and gone through
    multiple paths, there might be some session data we don't need when adding
    the submission to the database.

    For instance, if the user has uploaded a minister-approval document but later
    changed their answer to say that they don't have minister approval, we need to
    remove the uploaded file and change the corresponding session data. Otherwise
    approvers might get confused seeing documents that are not relevant.
    Another example is if the user chose Central Government and thus a domain purpose,
    but later changed to Fire Service, then the domain purpose answer should be removed
    in order not to show in the Application.

    :param rd: a registration data dictionary
    :return: the sanitised registration data
    """

    def clear_upload(name: str) -> None:
        rd.pop(name, None)
        uploaded_file_name = rd.pop(f"{name}_file_uploaded_filename", None)
        # Delete any temporary files that are no longer needed by the application
        if uploaded_file_name:
            storage = select_storage()
            if storage.exists(uploaded_file_name):
                storage.delete(uploaded_file_name)

        rd.pop(f"{name}_file_original_filename", None)
        rd.pop(f"{name}_file_uploaded_url", None)

    route = route_number(rd)
    if route["primary"] == 1:
        # If the final route taken is 1 (parish/neighbourhood council), then we don't need
        # data collected via other routes: domain purpose, exemption, written permission, minister support.
        rd.pop("domain_purpose", None)
        clear_upload("exemption")
        clear_upload("written_permission")
        clear_upload("minister")
    elif route["primary"] == 2 and route["secondary"] == 5:
        # If the final route taken is 2-5 (central gov, email-only), then we don't need
        # data collected via other routes: exemption.
        clear_upload("exemption")
    elif route["primary"] == 3:
        # If the final route taken is 3 (county council, fire service, etc), then we don't need
        # data collected via other routes: domain_purpose, exemption, minister support.
        rd.pop("domain_purpose", None)
        clear_upload("exemption")
        clear_upload("minister")
    if route.get("tertiary", 0) == 8:
        # Route 8 is when user doesn't have minister support.
        # In that case remove uploaded data
        rd["minister"] = "no"
        rd.pop("minister_file_uploaded_filename", None)
        rd.pop("minister_file_original_filename", None)
        rd.pop("minister_file_uploaded_url", None)
    rd.pop("domain_confirmation", None)

    return rd


def no_existing_application(reference: str):
    """
    Check for the existence of application by reference
    :param reference:
    :return:
    """
    return not Application.objects.filter(reference=reference).exists()


def save_data_in_database(reference, request):
    """
    Saves registration_data ( from session ) in the database

    It reuses RegistrarPerson, RegistrantPerson, RegistryPublishedPerson and Registrant
    records if they already exist, instead of creating them, using get_or_create method.

    :param reference: Reference number of the application
    :param request: Request object
    """

    session_data = request.session.get("registration_data", {})
    registration_data = sanitised_registration_data(
        session_data, request.session.session_key
    )

    if not is_valid_session_data(registration_data):
        raise ValueError(
            "Invalid session data found. Failed to create a valid application from the data collected from the user"
        )

    try:
        with transaction.atomic():
            registrar_org = Registrar.objects.get(
                id=int(registration_data["registrar_organisation"].split("-")[1])
            )
            registrar_person, _ = RegistrarPerson.objects.get_or_create(
                registrar=registrar_org,
                name=registration_data["registrar_name"],
                email_address=registration_data["registrar_email"],
                phone_number=registration_data["registrar_phone"],
            )
            registrant_person, _ = RegistrantPerson.objects.get_or_create(
                name=registration_data["registrant_full_name"],
                email_address=registration_data["registrant_email"],
                phone_number=registration_data["registrant_phone"],
            )
            (
                registry_published_person,
                _,
            ) = RegistryPublishedPerson.objects.get_or_create(
                role=registration_data["registrant_role"],
                email_address=registration_data["registrant_contact_email"],
            )

            registrant_org, _ = Registrant.objects.get_or_create(
                name=registration_data["registrant_organisation"],
                type=registration_data["registrant_type"],
            )

            registrar_org = Registrar.objects.get(
                id=int(registration_data["registrar_organisation"].split("-")[1])
            )

            application = Application.objects.create(
                reference=reference,
                domain_name=registration_data["domain_name"],
                registrar_person=registrar_person,
                registrant_person=registrant_person,
                registry_published_person=registry_published_person,
                registrant_org=registrant_org,
                registrar_org=registrar_org,
                written_permission_evidence=registration_data.get(
                    "written_permission_file_uploaded_filename"
                ),
                domain_purpose=registration_data.get("domain_purpose"),
                ministerial_request_evidence=registration_data.get(
                    "minister_file_uploaded_filename"
                ),
                policy_exemption_evidence=registration_data.get(
                    "exemption_file_uploaded_filename"
                ),
            )
            logger.info(
                "Saved application %d with reference %s", application.id, reference
            )
            Review.objects.create(application=application)

    except Exception as e:
        logger.error(
            f"""Exception while saving data. Exception: {type(e).__name__} - {str(e)} ,
             Registration data: {registration_data}"""
        )
        raise e
