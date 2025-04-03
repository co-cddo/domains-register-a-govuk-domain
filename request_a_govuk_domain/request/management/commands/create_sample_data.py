import logging
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.utils import timezone

from request_a_govuk_domain.request import models
from request_a_govuk_domain.request.models.application import (
    Application,
    ApplicationStatus,
)
from request_a_govuk_domain.request.models.storage_util import select_storage
from request_a_govuk_domain.settings import S3_STORAGE_ENABLED

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
SEED_DOCS_PATH = os.path.join(SCRIPT_PATH, "..", "..", "..", "..", "seed", "documents")
MEDIA_ROOT_PATH = os.path.join(SCRIPT_PATH, "..", "..", "..", "media")

PERSON_NAMES = [
    "Bob Roberts",
    "Peter Peters",
    "Olivia Oliver",
    "Thomas Thomson",
    "Alice Allison",
    "Samuel Samuels",
    "William Williams",
    "Harry Harris",
    "Emily Emmerson",
]

CG_REGISTRANT_NAME = "Ministry of Domains"
PC_REGISTRANT_NAME = "Any Cast Parish Council"
OTHER_REGISTRANT_NAME = "Border Gateway County Council"

CG_DOMAIN_NAME = "ministryofdomains.gov.uk"
PC_DOMAIN_NAME = "anycastparishcouncil.gov.uk"
OTHER_DOMAIN_NAME = "bordergatway.gov.uk"
OTHER_DOMAIN_NAME_2 = "example.gov.uk"
OTHER_DOMAIN_NAME_3 = "example-pc.gov.uk"

CG_DOMAIN_PURPOSE = "Web site"

WRITTEN_PERMISSION_FN = "written_permission.png"
MINISTERIAL_REQUEST_FN = "ministerial_request.png"
POLICY_TEAM_EXEMPTION_FN = "policy_team_exception.png"

DUMMY_REGISTRARS = ["WeRegister", "WeAlsoRegister", "WeLikeToRegister"]
logger = logging.getLogger(__name__)


def create_sample_application(
    domain_name: str,
    registrant_name: str,
    registrar_index: int,
    person_names: list[str],
    reference_suffix: str,
    status: ApplicationStatus = ApplicationStatus.NEW,
    written_permission_file: str | None = None,
    ministerial_request_file: str | None = None,
    policy_exemption_file: str | None = None,
) -> Application:
    # Copy the sample data to the temporary storage so the system will assume it is comping from the temporary
    # location. This is needed as we have overridden the save method of the application to fetch the data
    # from the TEMP_STORAGE_ROOT root location if we are using S3
    if S3_STORAGE_ENABLED:
        for f in [
            written_permission_file,
            ministerial_request_file,
            policy_exemption_file,
        ]:
            logger.info("Copying seed file %s", f)
            if f:
                with open(
                    Path(__file__).parent.joinpath(f"../../../media/{f}").resolve(),
                    "rb",
                ) as f_content:
                    select_storage().save(f, f_content)

    registrant, _ = models.Registrant.objects.get_or_create(name=registrant_name)

    registrant_person, _ = models.RegistrantPerson.objects.get_or_create(
        name=person_names[0]
    )

    registry_published_person, _ = models.RegistryPublishedPerson.objects.get_or_create(
        name=person_names[1],
        email_address=f"{'.'.join(person_names[1].split()).lower()}@{registrant.name.replace(' ', '').lower()}.net",
    )

    registrar, _ = models.Registrar.objects.get_or_create(pk=registrar_index)

    registrar_person, _ = models.RegistrarPerson.objects.get_or_create(
        name=person_names[2], registrar=registrar
    )

    application = models.Application(
        reference=f"GOVUK{datetime.today().strftime('%Y%m%d')}{reference_suffix}",
        domain_name=domain_name,
        registrant_person=registrant_person,
        registrar_person=registrar_person,
        registry_published_person=registry_published_person,
        registrant_org=registrant,
        registrar_org=registrar,
        written_permission_evidence=written_permission_file,
        ministerial_request_evidence=ministerial_request_file,
        policy_exemption_evidence=policy_exemption_file,
        status=status,
    )

    application.save()

    models.Review.objects.create(application=application)

    return application


class Command(BaseCommand):
    help = "Create a sample application for local testing"

    def handle(self, *args, **options):
        for file in os.listdir(SEED_DOCS_PATH):
            try:
                shutil.copy(os.path.join(SEED_DOCS_PATH, file), MEDIA_ROOT_PATH)
            except shutil.SameFileError:
                pass

        # delete existing data in case this is run multiple times
        models.RegistryPublishedPerson.objects.all().delete()
        models.RegistrarPerson.objects.all().delete()
        models.RegistrantPerson.objects.all().delete()
        models.Registrant.objects.all().delete()
        models.Application.objects.all().delete()
        models.Review.objects.all().delete()

        # Always try to create the dummy registrars as they are needed by the Cypress tests
        for registrar in DUMMY_REGISTRARS:
            try:
                models.Registrar.objects.create(name=registrar)
            except IntegrityError:
                print(f"Not creating registrar {registrar} as it already exists.")

        # Create an application from a central government department. This must have written permission
        # and can have (does have) evidence of a ministerial request and a naming policy exemption

        create_sample_application(
            domain_name=CG_DOMAIN_NAME,
            registrant_name=CG_REGISTRANT_NAME,
            registrar_index=1,
            person_names=PERSON_NAMES[:3],
            reference_suffix="ABCD",
            written_permission_file=WRITTEN_PERMISSION_FN,
            ministerial_request_file=MINISTERIAL_REQUEST_FN,
            policy_exemption_file=POLICY_TEAM_EXEMPTION_FN,
        )

        # Create an application from a parish council. This cannot have any of the three evidence types.

        create_sample_application(
            domain_name=PC_DOMAIN_NAME,
            registrant_name=PC_REGISTRANT_NAME,
            registrar_index=2,
            person_names=PERSON_NAMES[3:6],
            reference_suffix="EFGH",
        )

        # Create an application from any other registrant (not a parish council or central government org).
        # This must have written permission and cannot have evidence of a minsterial request nor a naming
        # policy exemption

        create_sample_application(
            domain_name=OTHER_DOMAIN_NAME,
            registrant_name=OTHER_REGISTRANT_NAME,
            registrar_index=3,
            person_names=PERSON_NAMES[6:],
            reference_suffix="IJKL",
            written_permission_file=WRITTEN_PERMISSION_FN,
        )

        # Create an application in progress

        create_sample_application(
            domain_name=OTHER_DOMAIN_NAME_2,
            registrant_name=OTHER_REGISTRANT_NAME,
            registrar_index=3,
            person_names=PERSON_NAMES[6:],
            reference_suffix="MNOP",
            written_permission_file=WRITTEN_PERMISSION_FN,
            status=ApplicationStatus.IN_PROGRESS,
        )

        # Create an application needing more information from 2 weeks ago

        app = create_sample_application(
            domain_name=OTHER_DOMAIN_NAME_3,
            registrant_name=OTHER_REGISTRANT_NAME,
            registrar_index=3,
            person_names=PERSON_NAMES[6:],
            reference_suffix="QRST",
            written_permission_file=WRITTEN_PERMISSION_FN,
            status=ApplicationStatus.MORE_INFORMATION,
        )
        app.time_submitted = datetime.now(timezone.utc) - timedelta(days=15)
        app.save()

        # Create an application needing more information from 2 days ago

        app = create_sample_application(
            domain_name="another-domain.gov.uk",
            registrant_name=OTHER_REGISTRANT_NAME,
            registrar_index=3,
            person_names=PERSON_NAMES[6:],
            reference_suffix="QRES",
            written_permission_file=WRITTEN_PERMISSION_FN,
            status=ApplicationStatus.MORE_INFORMATION,
        )
        app.time_submitted = datetime.now(timezone.utc) - timedelta(days=3)
        app.save()
