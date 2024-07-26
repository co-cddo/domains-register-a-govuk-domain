from zoneinfo import ZoneInfo

import django.db.models.fields.files
import markdown
from django.contrib import admin, messages
from django.contrib.admin.widgets import AdminFileWidget
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.http import HttpResponseRedirect, FileResponse
from django.template.loader import render_to_string
from django.urls import reverse, path
from django.utils.html import format_html

from request_a_govuk_domain.request.models import (
    Application,
    Review,
    ReviewFormGuidance,
    ApplicationStatus,
    RegistrantPerson,
    RegistrarPerson,
    RegistryPublishedPerson,
    Registrant,
    Registrar,
    TimeFlag,
)
from .filters import (
    StatusFilter,
    OwnerFilter,
    RegistrarOrgFilter,
    RegistrantOrgFilter,
    wrap_with_application_filter,
)
from .forms import ReviewForm
from ..models.storage_util import s3_root_storage

MAX_OBJECTS = 1


class FileDownloadMixin:
    """
    Provide file download support for the given admin class.
    """

    def download_file_view(self, request, object_id, field_name):
        """
        Implement this method to provide the specific retrieval of the object based on the given id
        :param request: Current request object
        :param object_id: id of the object containing the field
        :param field_name: which file field to download from the object
        :return:
        """
        pass

    @property
    def uid(self):
        """
        Unique id for the current subclass
        :return:
        """
        pass

    def get_urls(self):
        """
        Generate the custom url for the download_file_view.
        :return:
        """
        urls = super().get_urls()
        custom_urls = [
            path(
                f"download_{self.uid}/<int:object_id>/<str:field_name>/",
                self.admin_site.admin_view(self.download_file_view),
                name=f"{self.uid}_download_file",
            ),
        ]
        return custom_urls + urls

    def generate_download_link(self, obj, field_name, link_text):
        link = reverse(f"admin:{self.uid}_download_file", args=[obj.pk, field_name])
        return format_html(f'<a href="{link}" target="_blank">{link_text}</a>')


class CustomAdminFileWidget(AdminFileWidget):
    """
    Extend the default template to open the links on a new tab
    """

    template_name = "admin/clearable_file_input.html"


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


def convert_to_local_time(obj):
    """
    Utility function to convert a utc time to local time string
    :param obj:
    :return:
    """
    return (
        obj.astimezone(ZoneInfo("Europe/London")).strftime("%d %b %Y %H:%M:%S %p")
        if obj
        else "-"
    )


class ReviewAdmin(FileDownloadMixin, admin.ModelAdmin):
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
        "get_last_updated",
        "get_owner",
    )
    list_filter = (
        wrap_with_application_filter(StatusFilter),
        wrap_with_application_filter(OwnerFilter),
        wrap_with_application_filter(RegistrarOrgFilter),
        wrap_with_application_filter(RegistrantOrgFilter),
    )

    def download_file_view(self, request, object_id, field_name):
        review = self.model.objects.get(id=object_id)
        application = review.application
        file = getattr(application, field_name)
        # We need to use root_storage as the default storage always
        # refer to the TEMP_STORAGE_ROOT as the parent.
        return FileResponse(s3_root_storage().open(file.name, "rb"))

    @property
    def uid(self):
        return "review"

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
                    {
                        "Domain name requested": obj.application.domain_name,
                        "Reason for request": obj.application.domain_purpose,
                    }
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
                    {
                        "Registrant's name": obj.application.registrant_person.name,
                        "Telephone number": obj.application.registrant_person.phone_number,
                        "Email address": obj.application.registrant_person.email_address,
                    }
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

    def get_registry_details(self, obj):
        return (
            "Registry published details",
            {
                "fields": ("registry_details", "registry_details_notes"),
                "description": self._get_formatted_display_fields(
                    {
                        "Registrant role": obj.application.registry_published_person.role,
                        "Registrant email": obj.application.registry_published_person.email_address,
                    }
                )
                + markdown.markdown(
                    ReviewFormGuidance.objects.get(name="registry_details").how_to
                ),
            },
        )

    def get_reason_for_approval_rejection(self, obj):
        return (
            "Reason for Approval or Rejection",
            {
                "fields": ["reason"],
            },
        )

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            fieldset
            for fieldset in (
                self.get_registrar_fieldset(obj),
                self.get_domain_name_fieldset(obj),
                self.get_registrant_org_fieldset(obj),
                self.get_registrant_person_fieldset(obj),
                self.get_registrant_permission_fieldset(obj),
                self.get_policy_exemption_fieldset(obj),
                self.get_domain_name_rules_fieldset(obj),
                self.get_senior_support_fieldset(obj),
                self.get_registry_details(obj),
                self.get_reason_for_approval_rejection(obj),
            )
            if fieldset
        ]
        return fieldsets

    @admin.display(description="Reference")
    def get_reference(self, obj):
        return obj.application.reference

    @admin.display(description="Domain Name")
    def get_domain_name(self, obj):
        return obj.application.domain_name

    @admin.display(description="Status")
    def get_status(self, obj):
        return obj.application.status

    @admin.display(description="Registrar org")
    def get_registrar_org(self, obj):
        return obj.application.registrar_org

    @admin.display(description="Registrant org")
    def get_registrant_org(self, obj):
        return obj.application.registrant_org

    @admin.display(description="Time Submitted (UK time)")
    def get_time_submitted(self, obj):
        return convert_to_local_time(obj.application.time_submitted)

    @admin.display(description="Last updated (UK time)")
    def get_last_updated(self, obj):
        return convert_to_local_time(obj.application.last_updated)

    @admin.display(description="Owner")
    def get_owner(self, obj):
        return obj.application.owner

    def response_change(self, request, obj):
        if "_approve" in request.POST:
            if obj.is_approvable():
                return HttpResponseRedirect(
                    f"{reverse('application_confirm')}?obj_id={obj.application.id}&action=approval"
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
                    f"{reverse('application_confirm')}?obj_id={obj.application.id}&action=rejection"
                )
            else:
                self.message_user(
                    request, "This application can't be rejected!", messages.ERROR
                )
                return HttpResponseRedirect(
                    reverse("admin:request_review_change", args=[obj.id])
                )
        return super().response_change(request, obj)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Save the application attributes
        if obj.application.status == ApplicationStatus.NEW:
            obj.application.status = ApplicationStatus.IN_PROGRESS
        # Change the owner to be the current user regardless if there is already a user
        # assigned or not
        obj.application.owner = request.user
        obj.application.save()

    def has_add_permission(self, request):
        return False


class ApplicationAdmin(FileDownloadMixin, admin.ModelAdmin):
    model = Application
    list_display = [
        "reference",
        "domain_name",
        "status",
        "registrar_org",
        "registrant_org",
        "time_submitted_local_time",
        "last_updated_local_time",
        "owner",
    ]
    list_filter = (
        StatusFilter,
        OwnerFilter,
        RegistrarOrgFilter,
        RegistrantOrgFilter,
    )
    formfield_overrides = {
        django.db.models.fields.files.FileField: {"widget": CustomAdminFileWidget},
    }

    def download_file_view(self, request, object_id, field_name):
        application = self.model.objects.get(id=object_id)
        file = getattr(application, field_name)
        return FileResponse(s3_root_storage().open(file.name, "rb"))

    @property
    def uid(self):
        return "application"

    @admin.display(description="Time Submitted (UK time)")
    def time_submitted_local_time(self, obj):
        return convert_to_local_time(obj.time_submitted)

    @admin.display(description="Last updated (UK time)")
    def last_updated_local_time(self, obj):
        return convert_to_local_time(obj.last_updated)

    def save_model(self, request, obj, form, change):
        # When an application is saved, if it is still in the new state (not manually set)
        # update it to be 'in progress'
        if obj.status == ApplicationStatus.NEW and "status" not in form.changed_data:
            obj.status = ApplicationStatus.IN_PROGRESS
        # if the application owner is not set, then set it as the current user
        if not obj.owner and "owner" not in form.changed_data:
            obj.owner = request.user
        super().save_model(request, obj, form, change)


class RegistrarPersonAdmin(admin.ModelAdmin):
    model = RegistrarPerson


class RegistrantPersonAdmin(admin.ModelAdmin):
    model = RegistrantPerson


class RegistryPublishedPersonAdmin(admin.ModelAdmin):
    model = RegistryPublishedPerson


class RegistrantAdmin(admin.ModelAdmin):
    model = Registrant


class RegistrarAdmin(admin.ModelAdmin):
    model = Registrar


class TimeFlagAdmin(admin.ModelAdmin):
    model = TimeFlag

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False
