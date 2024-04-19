"""
URL configuration for request_a_govuk_domain project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from .request.views import (
    StartView,
    RegistrarDetailsView,
    RegistrantTypeView,
    DomainView,
    DomainConfirmationView,
    RegistrantDetailsView,
    RegistryDetailsView,
    RegistrantTypeFailView,
    WrittenPermissionView,
    WrittenPermissionFailView,
    ExemptionUploadRemoveView,
    WrittenPermissionUploadRemoveView,
    MinisterUploadRemoveView,
    ConfirmView,
    SuccessView,
    ExemptionView,
    MinisterView,
    ExemptionUploadView,
    MinisterUploadView,
    WrittenPermissionUploadView,
    ExemptionUploadConfirmView,
    MinisterUploadConfirmView,
    WrittenPermissionUploadConfirmView,
    ExemptionFailView,
    DomainPurposeView,
    DomainPurposeFailView,
    ServiceFailureView,
)

urlpatterns = [
    path("", StartView.as_view(), name="start"),
    path(
        "registrar-details/", RegistrarDetailsView.as_view(), name="registrar_details"
    ),
    path(
        "change-registrar-details/",
        RegistrarDetailsView.as_view(change=True),
        name="change_registrar_details",
    ),
    path("registrant-type/", RegistrantTypeView.as_view(), name="registrant_type"),
    path("domain/", DomainView.as_view(), name="domain"),
    path(
        "domain-confirmation/",
        DomainConfirmationView.as_view(),
        name="domain_confirmation",
    ),
    path(
        "registrant-details/",
        RegistrantDetailsView.as_view(),
        name="registrant_details",
    ),
    path(
        "change-registrant-details/",
        RegistrantDetailsView.as_view(change=True),
        name="change_registrant_details",
    ),
    path(
        "registry-details/",
        RegistryDetailsView.as_view(),
        name="registry_details",
    ),
    path(
        "change-registry-details",
        RegistryDetailsView.as_view(change=True),
        name="change_registry_details",
    ),
    path("domain-purpose/", DomainPurposeView.as_view(), name="domain_purpose"),
    path(
        "domain-purpose-fail/",
        DomainPurposeFailView.as_view(),
        name="domain_purpose_fail",
    ),
    path("exemption/", ExemptionView.as_view(), name="exemption"),
    path("exemption-upload/", ExemptionUploadView.as_view(), name="exemption_upload"),
    path(
        "exemption-upload-confirm/",
        ExemptionUploadConfirmView.as_view(),
        name="exemption_upload_confirm",
    ),
    path(
        "written-permission/",
        WrittenPermissionView.as_view(),
        name="written_permission",
    ),
    path(
        "written-permission-upload/",
        WrittenPermissionUploadView.as_view(),
        name="written_permission_upload",
    ),
    path(
        "written-permission-upload-confirm/",
        WrittenPermissionUploadConfirmView.as_view(),
        name="written_permission_upload_confirm",
    ),
    path("admin/", admin.site.urls),
    path(
        "registrant-type-fail/",
        RegistrantTypeFailView.as_view(),
        name="registrant_type_fail",
    ),
    path("confirm/", ConfirmView.as_view(), name="confirm"),
    path("success/", SuccessView.as_view(), name="success"),
    path(
        "exemption-upload-remove/",
        ExemptionUploadRemoveView.as_view(),
        name="exemption_upload_remove",
    ),
    path("exemption_fail/", ExemptionFailView.as_view(), name="exemption_fail"),
    path("minister/", MinisterView.as_view(), name="minister"),
    path(
        "written-permission-upload-remove/",
        WrittenPermissionUploadRemoveView.as_view(),
        name="written_permission_upload_remove",
    ),
    path(
        "minister-upload/",
        MinisterUploadView.as_view(),
        name="minister_upload",
    ),
    path(
        "minister-upload-confirm/",
        MinisterUploadConfirmView.as_view(),
        name="minister_upload_confirm",
    ),
    path(
        "minister-upload-remove/",
        MinisterUploadRemoveView.as_view(),
        name="minister_upload_remove",
    ),
    path(
        "written-permission-fail/",
        WrittenPermissionFailView.as_view(),
        name="written_permission_fail",
    ),
    path(
        "change-domain",
        DomainView.as_view(change=True),
        name="change_domain",
    ),
    path(
        "change-exemption",
        ExemptionView.as_view(change=True),
        name="change_exemption",
    ),
    path(
        "change-minister",
        MinisterView.as_view(change=True),
        name="change_minister",
    ),
    path(
        "change-written-permission",
        WrittenPermissionView.as_view(change=True),
        name="change_written_permission",
    ),
    path(
        "service-failure/",
        ServiceFailureView.as_view(),
        name="service_failure",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
