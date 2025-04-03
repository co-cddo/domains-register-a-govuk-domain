import logging
from datetime import timedelta

from django.views import View
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

from request_a_govuk_domain.request.models import Application, ApplicationStatus, Review

from .email import send_approval_or_rejection_email

LOGGER = logging.getLogger(__name__)


class DecisionConfirmationView(View, admin.ModelAdmin):
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        obj = Application.objects.get(pk=request.GET.get("obj_id"))
        review = Review.objects.filter(application__id=obj.id).first()
        context = {
            "obj": obj,
            "action": request.GET.get("action"),
            "reason": review.reason,
        }
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
                send_approval_or_rejection_email(request)
                self._set_application_status(request)
                # To show the backend app user a message "[Approval/Rejection] email sent", get the type of
                # action ( i.e. whether it is Approval or Rejection )
                approval_or_rejection = request.POST["action"].capitalize()
                self.message_user(
                    request, f"{approval_or_rejection} email sent", messages.SUCCESS
                )
                obj = Application.objects.get(pk=request.GET.get("obj_id"))
                LOGGER.info(
                    f"Application {obj.reference} status set to {approval_or_rejection}"
                )
                return HttpResponseRedirect(reverse("admin:request_review_changelist"))
            except Exception as e:
                LOGGER.error("Failed to send the email")
                self.message_user(request, f"Email send failed: {e}", messages.ERROR)
        review = Review.objects.filter(
            application__id=request.POST.get("obj_id")
        ).first()
        return HttpResponseRedirect(
            reverse("admin:request_review_change", args=[review.id])
        )


class AdminDashboardView(View, admin.ModelAdmin):
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        applications = Application.objects.all()
        new_applications = applications.filter(status=ApplicationStatus.NEW)
        in_progress_applications_total_count = applications.filter(
            status=ApplicationStatus.IN_PROGRESS
        ).count()
        in_progress_applications_owner_count = applications.filter(
            status=ApplicationStatus.IN_PROGRESS
        ).count()
        seven_days_ago = timezone.now() - timedelta(days=7)
        more_information_applications_total_count = applications.filter(
            status=ApplicationStatus.MORE_INFORMATION,
        ).count()
        more_information_applications_owner_count = applications.filter(
            status=ApplicationStatus.MORE_INFORMATION, owner=request.user
        ).count()
        more_information_applications_late = applications.filter(
            status=ApplicationStatus.MORE_INFORMATION,
            time_submitted__lt=seven_days_ago,
            owner=request.user,
        )
        more_information_applications_on_schedule = applications.filter(
            status=ApplicationStatus.MORE_INFORMATION,
            time_submitted__gte=seven_days_ago,
            owner=request.user,
        )
        with_nac_applications_total_count = applications.filter(
            status=ApplicationStatus.CURRENTLY_WITH_NAC, owner=request.user
        ).count()
        with_nac_applications_owner_count = applications.filter(
            status=ApplicationStatus.CURRENTLY_WITH_NAC, owner=request.user
        ).count()
        more_information_applications_length = len(
            more_information_applications_on_schedule
        ) + len(more_information_applications_late)
        context = admin.site.each_context(request)

        context.update(
            {
                "user_id": request.user.id,
                "new_applications": new_applications,
                "in_progress_applications_total_count": in_progress_applications_total_count,
                "in_progress_applications_owner_count": in_progress_applications_owner_count,
                "more_information_applications_total_count": more_information_applications_total_count,
                "more_information_applications_owner_count": more_information_applications_owner_count,
                "more_information_applications_late": more_information_applications_late,
                "more_information_applications_on_schedule": more_information_applications_on_schedule,
                "with_nac_applications_total_count": with_nac_applications_total_count,
                "with_nac_applications_owner_count": with_nac_applications_owner_count,
                "more_information_applications_length": more_information_applications_length,
                "user_name": request.user.username,
                "is_nav_sidebar_enabled": True,
            }
        )
        return render(request, "admin/dashboard.html", context)
