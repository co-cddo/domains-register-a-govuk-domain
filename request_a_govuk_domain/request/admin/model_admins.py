from django.contrib import admin, messages
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, FileResponse
from django.urls import reverse, path
from django.utils.html import format_html
import markdown


from request_a_govuk_domain.request.models import (
    Application,
    Review,
    ReviewFormGuidance,
)
from .forms import ReviewForm


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
    change_form_template = "admin/review_change_form.html"

    list_display = (
        "get_reference",
        "get_domain_name",
        "get_status",
        "get_registrar_org",
        "get_registrant_org",
        "get_time_submitted",
        "get_owner",
    )

    def generate_download_link(self, obj, field_name, link_text):
        link = reverse("admin:review_download_file", args=[obj.pk, field_name])
        return format_html(f'<a href="{link}" target="_blank">{link_text}</a>')

    def download_file_view(self, request, object_id, field_name):
        review = self.model.objects.get(id=object_id)
        application = review.application
        file = getattr(application, field_name)
        return FileResponse(file.open("rb"))

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "download/<int:object_id>/<str:field_name>/",
                self.admin_site.admin_view(self.download_file_view),
                name="review_download_file",
            ),
        ]
        return custom_urls + urls

    def _get_formatted_display_fields(self, display_fields: dict) -> str:
        return render_to_string(
            "admin/reviewer_read_only_fields.html", {"display_fields": display_fields}
        )

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
                )
                + markdown.markdown(
                    ReviewFormGuidance.objects.get(name="registrar_details").how_to
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
                )
                + markdown.markdown(
                    ReviewFormGuidance.objects.get(
                        name="domain_name_availability"
                    ).how_to
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
                )
                + markdown.markdown(
                    ReviewFormGuidance.objects.get(name="registrant_org").how_to
                ),
            },
        )

    def get_registrant_person_fieldset(self, obj):
        return (
            "The registrant's identity and their role in the organisation",
            {
                "fields": ("registrant_person", "registrant_person_notes"),
                "description": self._get_formatted_display_fields(
                    {"Registrant's name'": obj.application.registrant_person.name}
                )
                + markdown.markdown(
                    ReviewFormGuidance.objects.get(name="registrant_person").how_to
                ),
            },
        )

    def get_registrant_permission_fieldset(self, obj):
        if obj.application.written_permission_evidence:
            download_link = self.generate_download_link(
                obj, "written_permission_evidence", "View document"
            )
            return (
                "The registrant's permission to apply for the domain",
                {
                    "fields": ("registrant_permission", "registrant_permission_notes"),
                    "description": self._get_formatted_display_fields(
                        {"Evidence": download_link}
                    )
                    + markdown.markdown(
                        ReviewFormGuidance.objects.get(
                            name="registrant_permission"
                        ).how_to
                    ),
                },
            )

    def get_policy_exemption_fieldset(self, obj):
        if obj.application.policy_exemption_evidence:
            download_link = self.generate_download_link(
                obj, "policy_exemption_evidence", "View document"
            )
            return (
                "Exemption from using the GOV.UK website",
                {
                    "fields": ("policy_exemption", "policy_exemption_notes"),
                    "description": self._get_formatted_display_fields(
                        {"Evidence": download_link}
                    )
                    + markdown.markdown(
                        ReviewFormGuidance.objects.get(name="policy_exemption").how_to
                    ),
                },
            )

    def get_domain_name_rules_fieldset(self, obj):
        return (
            "Domain name meets the naming rules",
            {
                "fields": ("domain_name_rules", "domain_name_rules_notes"),
                "description": self._get_formatted_display_fields(
                    {"Domain name requested": obj.application.domain_name}
                )
                + markdown.markdown(
                    ReviewFormGuidance.objects.get(name="domain_name_rules").how_to
                ),
            },
        )

    def get_senior_support_fieldset(self, obj):
        if obj.application.ministerial_request_evidence:
            download_link = self.generate_download_link(
                obj, "ministerial_request_evidence", "View document"
            )
            return (
                "Domain name has Ministerial/Perm Sec support",
                {
                    "fields": (
                        "registrant_senior_support",
                        "registrant_senior_support_notes",
                    ),
                    "description": self._get_formatted_display_fields(
                        {"Evidence": download_link}
                    )
                    + markdown.markdown(
                        ReviewFormGuidance.objects.get(
                            name="registrant_senior_support"
                        ).how_to
                    ),
                },
            )

    def _relevant_fieldsets(self, obj):
        return [
            self.get_registrar_fieldset(obj),
            self.get_domain_name_fieldset(obj),
            self.get_registrant_org_fieldset(obj),
            self.get_registrant_person_fieldset(obj),
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

    def response_change(self, request, obj):
        if "_approve" in request.POST:
            if obj.is_approvable():
                return HttpResponseRedirect(
                    f"{reverse('application_confirm')}?obj_id={obj.id}&action=approval"
                )
            else:
                self.message_user(
                    request, "This application can't be approved!", messages.ERROR
                )
                return HttpResponseRedirect(
                    reverse("admin:request_review_change", args=[obj.id])
                )
        if "_reject" in request.POST:
            if obj.is_rejectable():
                return HttpResponseRedirect(
                    f"{reverse('application_confirm')}?obj_id={obj.id}&action=rejection"
                )
            else:
                self.message_user(
                    request, "This application can't be rejected!", messages.ERROR
                )
                return HttpResponseRedirect(
                    reverse("admin:request_review_change", args=[obj.id])
                )
        return super().response_change(request, obj)


class ApplicationAdmin(admin.ModelAdmin):
    model = Application
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
