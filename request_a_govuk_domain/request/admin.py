from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from .models import Application, CentralGovernmentAttributes, Review

class ReviewerReadOnlyFieldsMixin:
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        else:
            return [field.name for field in self.model._meta.fields]


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


class CentralGovernmentAttributesInline(ReviewerReadOnlyFieldsMixin, admin.StackedInline):
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




admin.site.unregister(User)
admin.site.register(User, DomainRegistrationUserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, DomainRegistrationGroupAdmin)

admin.site.register(Application, ApplicationAdmin)
