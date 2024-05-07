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
from .models import Application, ApplicationStatus, CentralGovernmentAttributes, Review
from .utils import send_email


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


class CentralGovernmentAttributesInline(
    ReviewerReadOnlyFieldsMixin, admin.StackedInline
):
    model = CentralGovernmentAttributes
    can_delete = False
    verbose_name_plural = "Central Government Attributes"

    def download_ministerial_request_evidence(self, obj):
        return self.generate_download_link(obj, "download_ministerial_request_evidence")

    def download_policy_exemption_evidence(self, obj):
        return self.generate_download_link(obj, "download_policy_exemption_evidence")

    download_ministerial_request_evidence.short_description = (  # type: ignore
        "Ministerial request evidence"
    )
    download_policy_exemption_evidence.short_description = (  # type: ignore
        "Naming policy exemption evidence"
    )


class ReviewInline(admin.StackedInline):
    model = Review
    can_delete = False
    verbose_name_plural = "Reviews"


def send_approval_or_rejection_email(request):
    """
    Sends Approval/Rejection mail depending on the action ( approval/rejection ) in the request object

    :param request: Request object
    """
    application = Application.objects.get(pk=request.POST["obj_id"])
    registrar_name = application.registrar_person.name
    registrar_email = application.registrar_person.email_address
    personalisation = {
        "first_name": registrar_name,
    }

    send_email(
        email_address=registrar_email,
        template_id=NOTIFY_TEMPLATE_ID_MAP[
            request.POST["action"]
        ],  # Notify template id of Approval/Rejection mail
        personalisation=personalisation,
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
    inlines = [CentralGovernmentAttributesInline, ReviewInline]

    def download_written_permission_evidence(self, obj):
        return self.generate_download_link(obj, "download_written_permission_evidence")

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
