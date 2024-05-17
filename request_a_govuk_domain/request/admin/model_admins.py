from django.contrib import admin, messages
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.http import HttpResponseRedirect
from django.http import FileResponse
from django.urls import reverse

from request_a_govuk_domain.request.models import Application, Review
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


class ReviewInline(admin.StackedInline):
    model = Review
    can_delete = False
    verbose_name_plural = "Reviews"


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
