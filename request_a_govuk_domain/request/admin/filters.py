from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import User

from request_a_govuk_domain.request.models import (
    ApplicationStatus,
    Registrar,
    Registrant,
)


class ApplicationFilterSupportMixin:
    """
    Mixin to externalise the common code for all application object filters.
    This is to be used alongside the SimpleListFilter.
    """

    """
    Property path to the field to be filtered on.
    E.G.
    If we are filtering on application object's status, then this should be "status".
    If this filter is applied to any other object containing an application attribute, then the
    property path should be "application__status" for filtering by application status.
    """
    query_field = ""

    def queryset(self, _request, queryset):
        if self.value():
            return queryset.filter(**{self.query_field: self.value()})
        return queryset


class StatusFilter(ApplicationFilterSupportMixin, SimpleListFilter):
    """
    Filter records by application status
    """

    title = "Filter by status"
    parameter_name = "status"
    query_field = "status"

    def lookups(self, request, model_admin):
        return list((a.value, a.label) for a in ApplicationStatus)


class OwnerFilter(ApplicationFilterSupportMixin, SimpleListFilter):
    """
    Filter records by application owner
    """

    title = "Filter by owner"
    parameter_name = "owner"
    query_field = "owner"

    def lookups(self, request, model_admin):
        return list(u for u in User.objects.values_list("id", "username"))


class RegistrarOrgFilter(ApplicationFilterSupportMixin, SimpleListFilter):
    """
    Filter records by application registrar
    """

    title = "Filter by registrar"
    parameter_name = "registrar"
    query_field = "registrar_org"

    def lookups(self, request, model_admin):
        return list(u for u in Registrar.objects.values_list("id", "name"))


class RegistrantOrgFilter(ApplicationFilterSupportMixin, SimpleListFilter):
    """
    Filter records by application registrant
    """

    title = "Filter by registrant"
    parameter_name = "registrant"
    query_field = "registrant_org__name"

    def lookups(self, request, model_admin):
        return list(
            u for u in Registrant.objects.values_list("name", "name").distinct()
        )


def wrap_with_application_filter(filter_class):
    """
    Utility function to wrap the Base class and update the query field without having to
    statically extend each class.
    :param filter_class:
    :return:
    """

    class Wrapped(filter_class):
        # Update the query field so we look in to the application attribute first before
        # using the actual filtering value. This is because Review object has an Application 1-1 mapping.
        query_field = f"application__{filter_class.query_field}"

    return Wrapped
