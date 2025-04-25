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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path

from .request.admin.views import (
    AdminDashboardView,
    ApplicationByRefView,
    ChangeStatusView,
    DecisionConfirmationView,
    ReviewByRefView,
)
from .request.views import (
    AccessibilityView,
    ConfirmView,
    CookiesPageView,
    DomainConfirmationView,
    DomainPurposeFailView,
    DomainPurposeView,
    DomainView,
    ExemptionFailView,
    ExemptionUploadConfirmView,
    ExemptionUploadRemoveView,
    ExemptionUploadView,
    ExemptionView,
    MinisterUploadConfirmView,
    MinisterUploadRemoveView,
    MinisterUploadView,
    MinisterView,
    PrivacyPolicyPageView,
    RegistrantDetailsView,
    RegistrantTypeFailView,
    RegistrantTypeView,
    RegistrarDetailsView,
    RegistryDetailsView,
    StartSessionView,
    StartView,
    SuccessView,
    TermsAndConditionsView,
    WrittenPermissionFailView,
    WrittenPermissionUploadConfirmView,
    WrittenPermissionUploadRemoveView,
    WrittenPermissionUploadView,
    WrittenPermissionView,
    bad_request_view,
    download_file,
    forbidden_view,
    page_not_found_view,
    robots_txt_view,
    security_txt_view,
    service_failure_view,
)

urlpatterns = [
    path("", StartView.as_view(), name="start"),
    path("cookies", CookiesPageView.as_view(), name="cookies_page"),
    path("accessibility", AccessibilityView.as_view(), name="accessibility_page"),
    path("privacy", PrivacyPolicyPageView.as_view(), name="privacy_policy"),
    path("terms", TermsAndConditionsView.as_view(), name="terms_and_conditions"),
    path("start-session/", StartSessionView.as_view(), name="start_session"),
    path("registrar-details/", RegistrarDetailsView.as_view(), name="registrar_details"),
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
    path(
        "admin/application_confirm/",
        DecisionConfirmationView.as_view(),
        name="application_confirm",
    ),
    path(
        "admin/change_status_view/",
        ChangeStatusView.as_view(),
        name="change_status_view",
    ),
    path(
        "admin/dashboard/",
        AdminDashboardView.as_view(),
        name="admin_dashboard",
    ),
    re_path(
        r"^admin/request/review_by_ref/(?P<ref>GOVUK.+)/$",
        ReviewByRefView.as_view(),
        name="admin_review_by_reference",
    ),
    re_path(
        r"^admin/request/application_by_ref/(?P<ref>GOVUK.+)/$",
        ApplicationByRefView.as_view(),
        name="admin_application_by_reference",
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
    path(".well-known/security.txt", security_txt_view),
    path("robots.txt", robots_txt_view),
    path("download_file/<str:file_type>", download_file, name="download_file"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler500 = service_failure_view
handler404 = page_not_found_view
handler403 = forbidden_view
handler401 = forbidden_view
handler400 = bad_request_view
