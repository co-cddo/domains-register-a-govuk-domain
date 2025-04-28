import logging
import re

from celery import shared_task
from django.db import transaction
from dotenv import load_dotenv
from notifications_python_client import NotificationsAPIClient
from notifications_python_client.errors import HTTPError

from request_a_govuk_domain.request.constants import NOTIFY_TEMPLATE_ID_MAP
from request_a_govuk_domain.request.models import (
    Application,
    ApplicationStatus,
    NotificationResponseID,
)
from request_a_govuk_domain.request.utils import (
    get_env_variable,
    get_notification_client,
    send_email,
)

load_dotenv()

logger = logging.getLogger(__name__)


def reference(body: str) -> str | None:
    """
    Extract Application reference from email body

    :param body: Email body
    :return: Application reference
    """
    pattern = r"Reference number: ([A-Z0-9]+)"
    match = re.search(pattern, body)
    if match:
        return match.group(1)
    return None


def update_application_and_send_failure_email(email_failure_notification: dict) -> None:
    """
    Updates application status and sends email

    This method:
    # Gets the application from the DB for the application reference ( contained in email_failure_notification )
    # Determines the application "to be" status ( Failed Confirmation/Decision Email )
    # Updates the application status and sends email

    :param email_failure_notification: - Information on the failed email
    :return: None
    """

    application = Application.objects.get(reference=email_failure_notification["application_reference"])

    # Based on the failed email subject, decide the application "to be" status
    application_to_be_status = (
        ApplicationStatus.FAILED_CONFIRMATION_EMAIL
        if email_failure_notification["subject"].endswith("received")
        else ApplicationStatus.FAILED_DECISION_EMAIL
    )

    application.status = application_to_be_status
    application.save()
    send_failed_email(email_failure_notification)


def send_failed_email(email_failure_notification: dict) -> None:
    """
    Creates personalisation for Notify template and sends email

    :param email_failure_notification: - Information on the failed email
    :return: None
    """
    env = get_env_variable("ENVIRONMENT")
    personalisation = {
        "env": env,
        "reference": email_failure_notification["application_reference"],
        "registrar_email": email_failure_notification["email_address"],
        "status": email_failure_notification["status"],
    }
    notify_template_id = (
        NOTIFY_TEMPLATE_ID_MAP["email-failure-prod"]
        if env == "prod"
        else NOTIFY_TEMPLATE_ID_MAP["email-failure-non-prod"]
    )
    send_email(
        email_address=get_env_variable("NOTIFY_EMAIL_FAILURE_RECIPIENT"),
        template_id=notify_template_id,
        personalisation=personalisation,
    )


def get_notification_for_id(
    notifications_client: NotificationsAPIClient,
    notification_response_id: NotificationResponseID,
) -> dict | None:
    """
    Gets the notification information for a given notification response id.

    :param notifications_client: NotificationsAPIClient object
    :param notification_response_id: NotificationResponseID object
    :return: notification ( dictionary containing notification information )
    """
    try:
        notification = notifications_client.get_notification_by_id(notification_response_id.id)
        return notification
    except HTTPError as e:
        if e.response.status_code == 404 and e.response.reason == "NOT FOUND":
            """
            This can happen if the original email address is a GOV UK Notify's "simulate delivered email address", in
            which only email delivery is simulated but no email is sent and Notification API will not
            have a record for the corresponding id

            In this scenario, we need to just log it and delete the notification_response_id data
            """
            logger.info(f"Notification with id {notification_response_id.id} not found.")
            # Since the notification is not found, delete it, so that we won't have to track it
            notification_response_id.delete()
            return None
        else:
            raise e


@shared_task
@transaction.atomic
def check_email_failure_and_notify() -> None:
    """
    Checks Notify email failure to registrar email address, if failed then update application status and
    send notification to internal team
    """
    notifications_client = get_notification_client()

    if notifications_client:
        notification_response_ids = NotificationResponseID.objects.all()

        for notification_response_id in notification_response_ids:
            notification = get_notification_for_id(notifications_client, notification_response_id)
            if notification:
                if notification["status"] == "delivered":
                    # Delete the notification response id, as the email has been delivered, so no need to track anymore
                    notification_response_id.delete()
                if "failure" in notification["status"]:
                    notification["application_reference"] = reference(notification["body"])
                    logger.info(f"Email send for Application reference {notification['application_reference']} failed")
                    update_application_and_send_failure_email(notification)
                    # Delete the notification response id, as the necessary action after email failure email has been
                    # taken, so no need to track anymore
                    notification_response_id.delete()
