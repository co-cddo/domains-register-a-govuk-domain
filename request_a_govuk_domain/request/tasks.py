import logging

from celery import shared_task

from request_a_govuk_domain.request.management.commands.check_email_failure import (
    check_email_failure_and_notify,
)

logger = logging.getLogger(__name__)


@shared_task
def email_fail_check_task():
    """
    Calls check_email_failure_and_notify
    """
    logger.info("In email_fail_check_task")
    check_email_failure_and_notify()
