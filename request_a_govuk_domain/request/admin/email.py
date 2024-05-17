from request_a_govuk_domain.request.models import Application
from request_a_govuk_domain.request.constants import NOTIFY_TEMPLATE_ID_MAP
from request_a_govuk_domain.request import utils


def registration_data_from_application(
    application: Application,
) -> dict[str, str | None]:
    """
    Builds registration_data dictionary from application so that it can be used in creating personalisation in a
    standard way

    :param application: The application object fetched from the data model

    :return: A dictionary of registration data
    """
    registration_data = {
        "registrar_name": application.registrar_person.name,
        "domain_name": application.domain_name,
        "registrant_type": application.registrant_org.type,
        "domain_purpose": application.domain_purpose,
        "exemption": "yes" if application.policy_exemption_evidence else "no",
        "written_permission": "yes"
        if application.written_permission_evidence
        else "no",
        "minister": "yes" if application.ministerial_request_evidence else "no",
        "registrant_organisation": application.registrant_org.name,
        "registrant_full_name": application.registrant_person.name,
        "registrant_phone": str(application.registrant_person.phone_number),
        "registrant_email": application.registrant_person.email_address,
        "registrant_role": application.registry_published_person.role,
        "registrant_contact_email": application.registry_published_person.email_address,
    }
    return registration_data


def send_approval_or_rejection_email(request):
    """
    Sends Approval/Rejection mail depending on the action ( approval/rejection ) in the request object

    :param request: Request object
    """
    application = Application.objects.get(pk=request.POST["obj_id"])
    registrar_email = application.registrar_person.email_address
    reference = application.reference

    # Build registration data dictionary to pass it to create_personalisation method
    registration_data = registration_data_from_application(application)
    personalisation_dict = utils.personalisation(reference, registration_data)

    route_specific_email_template_name = utils.route_specific_email_template(
        request.POST["action"], registration_data
    )

    utils.send_email(
        email_address=registrar_email,
        template_id=NOTIFY_TEMPLATE_ID_MAP[
            route_specific_email_template_name
        ],  # Notify template id of Approval/Rejection mail
        personalisation=personalisation_dict,
    )
