from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import path, reverse
from django.utils.html import format_html

from .models import Application, CentralGovernmentAttributes, Review


class ReviewerReadOnlyFieldsMixin:

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        else:
            return [
                field.name
                for field in self.model._meta.fields
                if field.name != "written_permission_evidence"
            ] + ["written_permission"]

    def get_fields(self, request, obj=None):
        return [
            field.name
            for field in self.model._meta.fields
            if field.name != "written_permission_evidence"
        ] + ["written_permission"]

    def written_permission(self, obj):
        link = reverse(
            "admin:view_permission_evidence",
            args=[obj.written_permission_evidence.name],
        )
        return format_html(
            '<a href="{}">{}</a>', link, "View written permission evidence"
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


class ReviewInline(admin.StackedInline):
    model = Review
    can_delete = False
    verbose_name_plural = "Reviews"


class ApplicationAdmin(ReviewerReadOnlyFieldsMixin, admin.ModelAdmin):
    model = Application
    inlines = [CentralGovernmentAttributesInline, ReviewInline]

    def get_form(self, request, obj=None, **kwargs):
        _form = super().get_form(request, obj, **kwargs)
        return _form

    def get_urls(self):
        urls = super().get_urls()
        extra_urls = [
            path(
                "view_permission_evidence/<str:file_name>",
                self.admin_site.admin_view(self.view_permission_evidence),
                name="view_permission_evidence",
            )
        ]
        # NOTE! Our custom urls have to go before the default urls, because they
        # default ones match anything.
        return extra_urls + urls

    def view_permission_evidence(self, request, file_name):
        return HttpResponse(f"Hello from {file_name}")


admin.site.unregister(User)
admin.site.register(User, DomainRegistrationUserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, DomainRegistrationGroupAdmin)

admin.site.register(Application, ApplicationAdmin)
