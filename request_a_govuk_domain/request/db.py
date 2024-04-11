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
    CentralGovernmentAttributes,
    RegistrarPerson,
    RegistrantPerson,
    RegistryPublishedPerson,
)
from request_a_govuk_domain.request.utils import is_central_government, route_number

logger = logging.getLogger(__name__)


def save_data_in_database(reference, request):
    """
    Saves registration_data ( from session ) in the database

    It reuses RegistrarPerson, RegistrantPerson, RegistryPublishedPerson and Registrant
    records if they already exist, instead of creating them, using get_or_create method.

    :param reference: Reference number of the application
    :param request: Request object
    """
    registration_data = request.session.get("registration_data", {})
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

            # Written permission is needed for all routes except route 1  ( Parish/Community/Neighbourhood/Village
            # council )
            if route_number(registration_data).get("primary") != 1:
                written_permission_evidence = registration_data[
                    "written_permission_file_uploaded_filename"
                ]
            else:
                written_permission_evidence = None

            application = Application.objects.create(
                reference=reference,
                domain_name=registration_data["domain_name"],
                registrar_person=registrar_person,
                registrant_person=registrant_person,
                registry_published_person=registry_published_person,
                registrant_org=registrant_org,
                registrar_org=registrar_org,
                written_permission_evidence=written_permission_evidence,
            )

            # Create CentralGovernmentAttributes, if the registrant type is central_government
            if is_central_government(registration_data["registrant_type"]):
                CentralGovernmentAttributes.objects.create(
                    application=application,
                    domain_purpose=registration_data["domain_purpose"],
                    ministerial_request_evidence=registration_data.get(
                        "minister_file_uploaded_filename", None
                    ),
                    policy_exemption_evidence=registration_data.get(
                        "exemption_file_uploaded_filename", None
                    ),
                )
    except Exception as e:
        logger.error(
            f"""Exception while saving data. Exception: {type(e).__name__} - {str(e)} ,
             Registration data: {registration_data}"""
        )
        raise e
