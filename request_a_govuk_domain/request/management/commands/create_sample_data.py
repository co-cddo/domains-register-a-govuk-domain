import logging
import os
import shutil
from datetime import datetime, timedelta, timezone
import random
import string
import csv
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from request_a_govuk_domain.request import models
from request_a_govuk_domain.request.models.application import (
    Application,
    ApplicationStatus,
)
from request_a_govuk_domain.request.models.storage_util import select_storage
from request_a_govuk_domain.settings import S3_STORAGE_ENABLED

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
SEED_PATH = os.path.join(SCRIPT_PATH, "..", "..", "..", "..", "seed")
SEED_DOCS_PATH = os.path.join(SEED_PATH, "documents")
MEDIA_ROOT_PATH = os.path.join(SCRIPT_PATH, "..", "..", "..", "media")

PERSON_NAMES: list[str] = []
DOMAIN_NAMES: list[str] = []
CENTRAL_GOV_DOMAINS: list[list[str]] = []
COUNCIL_DOMAINS: list[list[str]] = []

with open(os.path.join(SEED_PATH, "people-names.csv")) as file:
    reader = csv.reader(file)
    for row in reader:
        PERSON_NAMES.append(row[0])

with open(os.path.join(SEED_PATH, "central-gov-domains.csv")) as file:
    reader = csv.reader(file)
    for row in reader:
        CENTRAL_GOV_DOMAINS.append(row)

with open(os.path.join(SEED_PATH, "council-domains.csv")) as file:
    reader = csv.reader(file)
    for row in reader:
        COUNCIL_DOMAINS.append(row)

WRITTEN_PERMISSION_FILENAME = "written_permission.png"
MINISTERIAL_REQUEST_FILENAME = "ministerial_request.png"
POLICY_TEAM_EXEMPTION_FILENAME = "policy_team_exception.png"

TEST_REGISTRARS = ["WeRegister", "WeAlsoRegister", "WeLikeToRegister"]

logger = logging.getLogger(__name__)


def random_past_datetime(maxdays: int = 7) -> datetime:
    start = datetime.now(timezone.utc) - timedelta(days=maxdays)
    end = datetime.now(timezone.utc)
    random_duration = timedelta(
        seconds=random.randint(0, int((end - start).total_seconds())),
    )
    return start + random_duration


def create_sample_application(
    domain_name: str,
    registrant_name: str,
    registrar_index: int,
    person_names: list[str],
    reference_suffix: str,
    written_permission_file: str | None = None,
    ministerial_request_file: str | None = None,
    policy_exemption_file: str | None = None,
    domain_purpose: str = "website-email",
) -> Application:
    """
    Create an application from the parameters passed.
    """

    # Copy the sample files to the temporary storage so the system will assume it is coming from the temporary
    # location. This is needed as we have overridden the save method of the application to fetch the data
    # from the TEMP_STORAGE_ROOT root location if we are using S3
    print(person_names)
    if S3_STORAGE_ENABLED:
        for f in [
            written_permission_file,
            ministerial_request_file,
            policy_exemption_file,
        ]:
            if f:
                logger.info("Copying seed file %s", f)
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
        domain_purpose=domain_purpose,
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

        # Always try to those registrars as they are needed by the Cypress tests
        for registrar in TEST_REGISTRARS:
            try:
                models.Registrar.objects.create(name=registrar)
            except IntegrityError:
                print(f"Not creating registrar {registrar} as it already exists.")

        registrar_count = models.Registrar.objects.count()

        # 1. Parish council domains
        for index, (registrant, domain) in enumerate(COUNCIL_DOMAINS):
            domain_purpose = (
                "email-only" if random.randint(0, 10) == 0 else "website-email"
            )
            nbp = len(PERSON_NAMES)
            three_persons = [
                PERSON_NAMES[random.randint(0, nbp - 1)],
                PERSON_NAMES[random.randint(0, nbp - 1)],
                PERSON_NAMES[random.randint(0, nbp - 1)],
            ]
            create_sample_application(
                domain_name=domain,
                registrant_name=registrant,
                registrar_index=index % registrar_count,
                person_names=three_persons,
                reference_suffix="".join(
                    random.choice(string.ascii_uppercase) for _ in range(4)
                ),
                domain_purpose=domain_purpose,
            )

        # 2. Central government domains
        for index, (registrant, domain) in enumerate(CENTRAL_GOV_DOMAINS):
            domain_purpose = (
                "email-only" if random.randint(0, 10) == 0 else "website-email"
            )
            maybe_policy_exemption_file = (
                POLICY_TEAM_EXEMPTION_FILENAME if random.randint(0, 10) == 0 else None
            )
            maybe_ministerial_request = (
                MINISTERIAL_REQUEST_FILENAME if random.randint(0, 1) == 0 else None
            )
            create_sample_application(
                domain_name=domain,
                registrant_name=registrant,
                registrar_index=index % registrar_count,
                person_names=PERSON_NAMES[
                    index % len(PERSON_NAMES) : (index + 3) % len(PERSON_NAMES)
                ],
                reference_suffix="".join(
                    random.choice(string.ascii_uppercase) for _ in range(4)
                ),
                domain_purpose=domain_purpose,
                written_permission_file=WRITTEN_PERMISSION_FILENAME,
                policy_exemption_file=maybe_policy_exemption_file,
                ministerial_request_file=maybe_ministerial_request,
            )

        users = list(User.objects.all())

        for app in models.Application.objects.all():
            app.time_submitted = random_past_datetime(maxdays=15)
            owner = users[random.randint(0, len(users) - 1)]

            if random.randint(0, 10) > 0:
                match random.randint(0, 3):
                    case 0:
                        app.status = ApplicationStatus.IN_PROGRESS
                    case 1:
                        app.status = ApplicationStatus.CURRENTLY_WITH_NAC
                    case 2:
                        app.status = ApplicationStatus.READY_2I
                    case 3:
                        app.status = ApplicationStatus.MORE_INFORMATION
                app.owner = owner
                app.last_updated = datetime.now(timezone.utc)
                app.last_updated_by = owner
            app.save()
