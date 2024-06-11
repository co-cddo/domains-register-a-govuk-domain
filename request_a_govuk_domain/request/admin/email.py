import hashlib
from datetime import timedelta

from django.utils import timezone

from request_a_govuk_domain.request.models import Application, Review
from request_a_govuk_domain.request.constants import NOTIFY_TEMPLATE_ID_MAP
from request_a_govuk_domain.request import utils
from request_a_govuk_domain.request.utils import get_env_variable


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


def nominet_env_variable(env_var_name: str) -> str | None:
    """
    Gets environment variable for nominet.
    :param env_var_name: Name of the environment variable
    :return: Environment variable value or None
    """
    env_variable_value = get_env_variable(env_var_name)

    # Nominet related environment variables are fetched from AWS SecretManager. The default/initial values
    # for these are "default" and the actual values are set manually. Following code ensures that a
    # non-default/actual values are set in production environment, otherwise it errors out
    if get_env_variable("ENVIRONMENT") == "prod" and env_variable_value == "default":
        raise ValueError(
            f"Proper value for env variable {env_var_name} not found in Production environment"
        )
    return env_variable_value


def token(reference, domain_name: str) -> str:
    """
    Generates a token for Nominet, using the logic provided by Nominet
    :param reference: Application reference
    :param domain_name: Domain name, for which the application is made
    :return: Token
    """
    # token_id is application reference except the prefix "GOVUK"
    token_id = reference[5:]

    roms_id = nominet_env_variable("NOMINET_ROMSID")
    secret = nominet_env_variable("NOMINET_SECRET")  # pragma: allowlist secret

    # Token expiry date time is 60 days from now in UTC in the format: YYYYMMDDHHMM
    token_expiry_datetime = (timezone.now() + timedelta(days=60)).strftime("%Y%m%d%H%M")

    # Generate the SHA-256 encoded signature
    signature = hashlib.sha256(
        (token_id + roms_id + domain_name + token_expiry_datetime + secret).encode()
    ).hexdigest()

    #  Concatenate required attributes into the final token
    generated_token = (
        f"#{token_id}#{roms_id}#{domain_name}#{token_expiry_datetime}#{signature}"
    )
    return generated_token


def send_approval_or_rejection_email(request):
    """
    Sends Approval/Rejection mail depending on the action ( approval/rejection ) in the request object

    :param request: Request object
    """
    application = Application.objects.get(pk=request.POST["obj_id"])
    registrar_email = application.registrar_person.email_address
    reference = application.reference

    # Build registration data dictionary to pass it to personalisation method
    registration_data = registration_data_from_application(application)
    personalisation_dict = utils.personalisation(reference, registration_data)

    # action would be either approval or rejection
    approval_or_rejection = request.POST["action"]

    # If approval_or_rejection is approval, then add token to the personalisation
    if approval_or_rejection == "approval":
        personalisation_dict["token"] = token(
            reference, registration_data["domain_name"]
        )
    else:
        # we add the reason for the approval/rejection to personalisation_dict
        review = Review.objects.filter(application__id=application.id).first()
        personalisation_dict["reason_for_rejection"] = review.reason

    route_specific_email_template_name = utils.route_specific_email_template(
        approval_or_rejection, registration_data
    )

    utils.send_email(
        email_address=registrar_email,
        template_id=NOTIFY_TEMPLATE_ID_MAP[
            route_specific_email_template_name
        ],  # Notify template id of Approval/Rejection mail
        personalisation=personalisation_dict,
    )
