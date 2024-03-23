from functools import partial

from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db.models import FileField
from django.http import HttpResponse
from django.urls import path, reverse
from django.utils.html import format_html

from .models import Application, CentralGovernmentAttributes, Review


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
            return self._get_field_names()

    def _get_field_names(self):
        return [
            field.name
            for field in self.model._meta.fields
            if type(field) != FileField
        ] + ["download_" + field.attname
             for field in self.model._meta.fields
             if type(field) == FileField]

    def get_fields(self, request, obj=None):
        return self._get_field_names()

    def get_urls(self):
        urls = super().get_urls()
        all_fields = []
        all_fields.extend(self.model._meta.fields)
        for inline in self.inlines:
            all_fields.extend(inline.model._meta.fields)
        extra_urls = [
            path(
                f"<int:object_id>/download_{field.attname}/",
                self.admin_site.admin_view(partial(self.download_file, field_name=field.attname)),
                name="download_" + field.attname,
            )
            for field in all_fields
            if type(field) == FileField
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
                f'<a href="{{}}" download="{getattr(obj, field_name).name}">{{}}</a>', link, "Download File"
            )
        else:
            return "--"

    def download_file(self, request, field_name, object_id):
        """
        Override this method in the child class to provide the implementation
        :param request: Http request
        :param field_name: Name of the file field
        :param object_id: object id to retrieve
        :return:
        """
        raise NotImplementedError("Override this method in your model admin to get the file")


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

    def download_gds_exemption_evidence(self, obj):
        return self.generate_download_link(obj, "download_gds_exemption_evidence")

    def download_file(self, request, field_name, object_id):
        return HttpResponse(f"{object_id}- {field_name}")

    download_ministerial_request_evidence.short_description = "Ministerial request evidence"
    download_gds_exemption_evidence.short_description = "GDS exemption evidence"


class ReviewInline(admin.StackedInline):
    model = Review
    can_delete = False
    verbose_name_plural = "Reviews"


class ApplicationAdmin(ReviewerReadOnlyFieldsMixin, admin.ModelAdmin):
    model = Application
    inlines = [CentralGovernmentAttributesInline, ReviewInline]

    def download_written_permission_evidence(self, obj):
        return self.generate_download_link(obj, "download_written_permission_evidence")

    def download_file(self, request, field_name, object_id):
        return HttpResponse(f"{object_id}- {field_name}")

    download_written_permission_evidence.short_description = "Written permission evidence"


admin.site.unregister(User)
admin.site.register(User, DomainRegistrationUserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, DomainRegistrationGroupAdmin)

admin.site.register(Application, ApplicationAdmin)
