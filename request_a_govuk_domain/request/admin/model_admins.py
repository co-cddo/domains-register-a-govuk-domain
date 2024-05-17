from django.contrib import admin, messages
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.http import HttpResponseRedirect
from django.http import FileResponse
from django.urls import reverse

from request_a_govuk_domain.request.models import Application, Review
from .forms import ReviewForm
from .mixins import ReviewerReadOnlyFieldsMixin


class DomainRegistrationUserAdmin(UserAdmin):
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return False


class DomainRegistrationGroupAdmin(GroupAdmin):
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return False


class ReviewAdmin(admin.ModelAdmin):
    model = Review
    form = ReviewForm

    list_display = (
        "get_reference",
        "get_domain_name",
        "get_status",
        "get_registrar_org",
        "get_registrant_org",
        "get_time_submitted",
        "get_owner",
    )

    def _get_formatted_display_fields(self, display_fields: dict) -> str:
        formatted_fields = ""
        for key, value in display_fields.items():
            formatted_fields = f"{formatted_fields}<li>{key} : {value}</li>"
        return "<ul>" + formatted_fields + "</ul>"

    def get_registrar_fieldset(self, obj):
        return (
            "The registrar's details",
            {
                "fields": ("registrar_details", "registrar_details_notes"),
                "description": self._get_formatted_display_fields(
                    {
                        "Registrar organisation name": obj.application.registrar_org.name,
                        "Full name": obj.application.registrar_person.name,
                        "Telephone number": obj.application.registrar_person.phone_number,
                        "Email address": obj.application.registrar_person.email_address,
                    }
                ),
            },
        )

    def get_domain_name_fieldset(self, obj):
        return (
            "Domain name availability",
            {
                "fields": (
                    "domain_name_availability",
                    "domain_name_availability_notes",
                ),
                "description": self._get_formatted_display_fields(
                    {"Domain name requested": obj.application.domain_name}
                ),
            },
        )

    def get_registrant_org_fieldset(self, obj):
        return (
            "The registrant's organisation",
            {
                "fields": ("registrant_org", "registrant_org_notes"),
                "description": self._get_formatted_display_fields(
                    {"Registrant's organisation": obj.application.registrant_org.name}
                ),
            },
        )

    def registrant_person_fieldset(self, obj):
        return (
            "The registrant's identity and their role in the organisation",
            {
                "fields": ("registrant_person", "registrant_person_notes"),
                "description": self._get_formatted_display_fields(
                    {"Registrant's name'": obj.application.registrant_person.name}
                ),
            },
        )

    def get_registrant_permission_fieldset(self, obj):
        if obj.application.written_permission_evidence:
            return (
                "The registrant's permission to apply for the domain",
                {
                    "fields": ("registrant_permission", "registrant_permission_notes"),
                },
            )
        return None

    def get_policy_exemption_fieldset(self, obj):
        if obj.application.policy_exemption_evidence:
            return (
                "Exemption from using the GOV.UK website",
                {
                    "fields": ("policy_exemption", "policy_exemption_notes"),
                },
            )
        return None

    def get_domain_name_rules_fieldset(self, obj):
        return (
            "Domain name meets the naming rules",
            {
                "fields": ("domain_name_rules", "domain_name_rules_notes"),
                "description": self._get_formatted_display_fields(
                    {"Domain name requested": obj.application.domain_name}
                ),
            },
        )

    def get_senior_support_fieldset(self, obj):
        if obj.application.ministerial_request_evidence:
            return (
                "Domain name has Ministerial/Perm Sec support",
                {
                    "fields": (
                        "registrant_senior_support",
                        "registrant_senior_support_notes",
                    ),
                },
            )
        return None

    def _relevant_fieldsets(self, obj):
        return [
            self.get_registrar_fieldset(obj),
            self.get_domain_name_fieldset(obj),
            self.get_registrant_org_fieldset(obj),
            self.registrant_person_fieldset(obj),
            self.get_registrant_permission_fieldset(obj),
            self.get_policy_exemption_fieldset(obj),
            self.get_domain_name_rules_fieldset(obj),
            self.get_senior_support_fieldset(obj),
        ]

    def get_fieldsets(self, request, obj=None):
        fieldsets = self._relevant_fieldsets(obj)
        return fieldsets

    def get_reference(self, obj):
        return obj.application.reference

    def get_domain_name(self, obj):
        return obj.application.domain_name

    def get_status(self, obj):
        return obj.application.status

    def get_registrar_org(self, obj):
        return obj.application.registrar_org

    def get_registrant_org(self, obj):
        return obj.application.registrant_org

    def get_time_submitted(self, obj):
        return obj.application.time_submitted

    def get_owner(self, obj):
        return obj.application.owner


class ApplicationAdmin(ReviewerReadOnlyFieldsMixin, admin.ModelAdmin):
    model = Application
    change_form_template = "admin/application_change_form.html"
    list_display = [
        "reference",
        "domain_name",
        "status",
        "registrar_org",
        "registrant_org",
        "time_submitted",
        "owner",
    ]
    list_filter = ["status", "registrar_org", "registrant_org"]

    def download_written_permission_evidence(self, obj):
        return self.generate_download_link(obj, "download_written_permission_evidence")

    def download_ministerial_request_evidence(self, obj):
        return self.generate_download_link(obj, "download_ministerial_request_evidence")

    def download_policy_exemption_evidence(self, obj):
        return self.generate_download_link(obj, "download_policy_exemption_evidence")

    def download_file(self, request, field_name, object_id):
        instance = self.model.objects.get(pk=object_id)
        try:
            file = getattr(instance, field_name)
        except AttributeError:
            file = getattr(instance.centralgovt, field_name)
        return FileResponse(file.open("rb"))

    download_written_permission_evidence.short_description = (  # type: ignore
        "Written permission evidence"
    )

    download_ministerial_request_evidence.short_description = (  # type: ignore
        "Ministerial request evidence"
    )
    download_policy_exemption_evidence.short_description = (  # type: ignore
        "Naming policy exemption evidence"
    )

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj) + ["time_submitted"]

    def response_change(self, request, obj):
        if "_approve" in request.POST:
            if obj.review.is_approvable():
                return HttpResponseRedirect(
                    f"{reverse('application_confirm')}?obj_id={obj.id}&action=approval"
                )
            else:
                self.message_user(
                    request, "This application can't be approved!", messages.ERROR
                )
                return HttpResponseRedirect(
                    reverse("admin:request_application_change", args=[obj.id])
                )
        if "_reject" in request.POST:
            if obj.review.is_rejectable():
                return HttpResponseRedirect(
                    f"{reverse('application_confirm')}?obj_id={obj.id}&action=rejection"
                )
            else:
                self.message_user(
                    request, "This application can't be rejected!", messages.ERROR
                )
                return HttpResponseRedirect(
                    reverse("admin:request_application_change", args=[obj.id])
                )
        return super().response_change(request, obj)