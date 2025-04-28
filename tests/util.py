from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from request_a_govuk_domain.request.management.commands import add_init_guidance_text
from request_a_govuk_domain.request.models import (
    Registrant,
    RegistrantPerson,
    Registrar,
    RegistrarPerson,
    RegistryPublishedPerson,
)


class AdminScreenTestMixin:
    def setUp(self):
        self.registrar = Registrar.objects.create(name="dummy registrar")
        self.registrar_person = RegistrarPerson.objects.create(name="dummy registrar person", registrar=self.registrar)
        self.registrant = Registrant.objects.create(name="dummy registrant")
        self.registrant_person = RegistrantPerson.objects.create(name="dummy registrant person")
        self.registry_publish_person = RegistryPublishedPerson.objects.create(name="dummy reg publish person")
        self.registration_data = {
            "registrant_type": "parish_council",
            "domain_name": "test.domain.gov.uk",
            "registrar_name": "dummy registrar",
            "registrar_email": "dummy_registrar_email@gov.uk",
            "registrar_phone": "23456789",
            "registrar_organisation": f"{self.registrar.name}-{self.registrar.id}",
            "registrant_organisation": "dummy org",
            "registrant_full_name": "dummy user",
            "registrant_phone": "012345678",
            "registrant_email": "dummy@test.gov.uk",
            "registrant_role": "dummy",
            "registrant_contact_email": "dummy@test.gov.uk",
        }

        self.superuser = User.objects.create_superuser(
            username="superuser",
            password="secret",  # pragma: allowlist secret
            email="admin@example.com",
        )
        self.reviewer = User.objects.create_superuser(
            username="reviewer",
            password="secret",  # pragma: allowlist secret
            email="reviewer@example.com",
        )
        guidance_text = add_init_guidance_text.Command()
        guidance_text.handle()
        self.admin_client = Client()
        self.admin_client.login(username="superuser", password="secret")  # pragma: allowlist secret

    def get_application_update_json(self, application):
        data = {
            # Assign the application to reviewer
            "time_decided_0": "2024-08-23",
            "time_decided_1": "17:35:58",
            "reference": application.reference,
            "status": application.status,
            "domain_name": application.domain_name,
            "registrar_person": application.registrar_person.id,
            "registrant_person": application.registrant_person.id,
            "registry_published_person": application.registry_published_person.id,
            "registrant_org": application.registrant_org.id,
            "registrar_org": application.registrar_org.id,
        }
        return data


class SessionDict(dict):
    """
    Utility class to mock the HTTP session object.
    """

    def __init__(self, *k, **kwargs):
        self.__dict__ = self
        super().__init__(*k, **kwargs)
        self.session_key = "session-key"


def get_response_content(response):
    content = str(response.content)
    return content.replace("\\n", "")


def get_admin_change_view_url(obj: object) -> str:
    return reverse_("change", obj)


def get_admin_history_view_url(obj: object) -> str:
    return reverse_("history", obj)


def reverse_(method: str, obj: object) -> str:
    return reverse(
        ("admin:{}_{}_" + method).format(obj._meta.app_label, type(obj).__name__.lower()),  # type: ignore
        args=(obj.pk,),  # type: ignore
    )
