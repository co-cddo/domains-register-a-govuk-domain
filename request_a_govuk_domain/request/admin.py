import hashlib
from datetime import timedelta
from functools import partial

from django.views import View
from django.contrib import admin, messages
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.db.models import FileField
from django.http import HttpResponseRedirect, FileResponse
from django.shortcuts import render
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

from .constants import NOTIFY_TEMPLATE_ID_MAP

# from .utils import send_email
from .models import Application, ApplicationStatus, Review
from .utils import (
    send_email,
    personalisation,
    route_specific_email_template,
    get_env_variable,
)


class ReviewerReadOnlyFieldsMixin:
    """
    This will convert any file fields to a link pointing to a view named admin:download_file. Which enables the user
    to download the file for viewing. This view has to be implemented by the model admin that uses this mixin.

    The ModelAdmin will need to implement a method prefixed with download_<file field attribute>
    for each file field available in the model and call the generate_download_link function in it.
    Following code shows how it is done for a model which contains a file field called 'gds_exemption_evidence'

        def download_gds_exemption_evidence(self, obj):
            return self.generate_download_link(obj.gds_exemption_evidence.name)

        # Set the short description attribute on the method so it will be used as the label in the form
        download_gds_exemption_evidence.short_description = "GDS exemption evidence"

    """

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        else:
            return self._get_field_names(not request.user.is_superuser) + [
                "time_decided"
            ]

    def get_fields(self, request, obj=None):
        return self._get_field_names(not request.user.is_superuser)

    def get_urls(self):
        urls = super().get_urls()
        all_fields = []
        all_fields.extend(self.model._meta.fields)
        for inline in self.inlines:
            all_fields.extend(inline.model._meta.fields)
        extra_urls = [
            path(
                f"<int:object_id>/download_{field.attname}/",
                self.admin_site.admin_view(
                    partial(self.download_file, field_name=field.attname)
                ),
                name="download_" + field.attname,
            )
            for field in all_fields
            if isinstance(field, FileField)
        ]
        # NOTE! Our custom urls have to go before the default urls, because they
        # default ones match anything.
        return extra_urls + urls

    def generate_download_link(self, obj, field):
        field_name = field.replace("download_", "")
        if getattr(obj, field_name):
            link = reverse(
                f"admin:{field}",
                args=[obj.id],
            )
            return format_html(
                f'<a href="{{}}" download="{getattr(obj, field_name).name}">{{}}</a>',
                link,
                "Download File",
            )
        else:
            return "--"

    def download_file(self, request, field_name, object_id):
        """
        Override this method in the child class to provide the implementation. Note that for inline admin classes
        this must be overriden in the 'parent' class (the class which inherits from admin.ModelAdmin) and not
        the inline class (inherits from StackedInline or TabularInline). Any method in the inline classes is
        ignored

        :param request: Http request
        :param field_name: Name of the file field
        :param object_id: object id to retrieve
        :return:
        """
        raise NotImplementedError(
            "Override this method in your model admin to get the file"
        )

    def _get_field_names(self, add_download_fields=False):
        """
        Get the list of field names to show on the admin screen depending on the flag provided.
        This will add extra attribute starting with "download_" replacing any FileFields
        that exist in the model if add_add_download_fields set to true. Will return unmodified
        list of field names (excluding the id) if the flag is set to false.
        :param add_download_fields: set to true if the FileFields should be replaced with download links
        :return: list of field names applicable for the current view.
        """
        return [
            field.name
            for field in self.model._meta.fields
            if not isinstance(field, FileField) and field.name != "id"
        ] + (
            [
                "download_" + field.attname
                for field in self.model._meta.fields
                if isinstance(field, FileField)
            ]
            if add_download_fields
            else [
                field.name
                for field in self.model._meta.fields
                if isinstance(field, FileField)
            ]
        )


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


class ReviewInline(admin.StackedInline):
    model = Review
    can_delete = False
    verbose_name_plural = "Reviews"


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
        "#"
        + token_id
        + "#"
        + roms_id
        + "#"
        + domain_name
        + "#"
        + token_expiry_datetime
        + "#"
        + signature
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
    personalisation_dict = personalisation(reference, registration_data)

    # action would be either approval or rejection
    approval_or_rejection = request.POST["action"]

    # If it is approval, then add token to the personalisation
    if approval_or_rejection == "approval":
        personalisation_dict["token"] = token(
            reference, registration_data["domain_name"]
        )

    route_specific_email_template_name = route_specific_email_template(
        approval_or_rejection, registration_data
    )

    send_email(
        email_address=registrar_email,
        template_id=NOTIFY_TEMPLATE_ID_MAP[
            route_specific_email_template_name
        ],  # Notify template id of Approval/Rejection mail
        personalisation=personalisation_dict,
    )


class DecisionConfirmationView(View, admin.ModelAdmin):
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        obj = Application.objects.get(pk=request.GET.get("obj_id"))
        context = {"obj": obj, "action": request.GET.get("action")}
        return render(request, "admin/application_decision_confirmation.html", context)

    def _set_application_status(self, request):
        obj = Application.objects.get(pk=request.POST.get("obj_id"))
        if request.POST.get("action") == "approval":
            obj.status = ApplicationStatus.APPROVED
        elif request.POST.get("action") == "rejection":
            obj.status = ApplicationStatus.REJECTED
        obj.time_decided = timezone.now()
        obj.save()

    def post(self, request):
        if "_confirm" in request.POST:
            try:
                # send email
                send_approval_or_rejection_email(request)
                self._set_application_status(request)
                # To show the backend app user a message "[Approval/Rejection] email sent", get the type of
                # action ( i.e. whether it is Approval or Rejection )
                approval_or_rejection = request.POST["action"].capitalize()
                self.message_user(
                    request, f"{approval_or_rejection} email sent", messages.SUCCESS
                )
                return HttpResponseRedirect(
                    reverse("admin:request_application_changelist")
                )
            except Exception as e:
                self.message_user(request, f"Email send failed: {e}", messages.ERROR)
        return HttpResponseRedirect(
            reverse(
                "admin:request_application_change", args=[request.POST.get("obj_id")]
            )
        )


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
    inlines = [ReviewInline]

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


admin.site.unregister(User)
admin.site.register(User, DomainRegistrationUserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, DomainRegistrationGroupAdmin)

admin.site.register(Application, ApplicationAdmin)
