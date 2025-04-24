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
                LOGGER.error("Failed to send the email", exc_info=True)
                self.message_user(request, f"Email send failed: {e}", messages.ERROR)
        review = Review.objects.filter(
            application__id=request.POST.get("obj_id")
        ).first()
        return HttpResponseRedirect(
            reverse("admin:request_review_change", args=[review.id])
        )


class ChangeStatusView(View, admin.ModelAdmin):
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_status_choices(self):
        """
        Retrieve a list of status choices for the application, excluding APPROVED and REJECTED statuses.

        This method filters out the APPROVED and REJECTED statuses from the ApplicationStatus choices
        and returns a list of dictionaries, where each dictionary contains the status value and its label.

        :return: A list of dictionaries with keys 'status' and 'label'.
        Example:
            [
                {"status": "in_progress", "label": "In Progress"},
                {"status": "ready_2i", "label": "Ready for 2i"},
                {"status": "more_information", "label": "More Information"},
                ...
            ]
        """
        excluded_statuses = [ApplicationStatus.APPROVED, ApplicationStatus.REJECTED]
        status_list = [
            {"status": status, "label": label}
            for status, label in ApplicationStatus.choices
            if status not in excluded_statuses
        ]
        return status_list

    def get(self, request):
        status_choices = self.get_status_choices()
        obj = Application.objects.get(pk=request.GET.get("obj_id"))
        review = Review.objects.filter(application__id=obj.id).first()
        context = {
            "obj": obj,
            "reason": review.reason,
            "status_choices": status_choices,
        }
        return render(request, "admin/change_status_confirmation.html", context)

    def _set_application_status(self, request):
        obj = Application.objects.get(pk=request.POST.get("obj_id"))
        status = request.POST.get("status")
        obj.status = ApplicationStatus(status)
        obj.time_decided = timezone.now()
        obj.save()

    def post(self, request):
        if "_confirm" in request.POST:
            try:
                self._set_application_status(request)
                self.message_user(
                    request, "Application status changed", messages.SUCCESS
                )
                obj = Application.objects.get(pk=request.GET.get("obj_id"))
                LOGGER.info(f"Application {obj.reference} status set to {obj.status}")
                return HttpResponseRedirect(reverse("admin:request_review_changelist"))
            except Exception as e:
                LOGGER.error("Failed to change status of application", exc_info=True)
                self.message_user(
                    request, f"Application status change failed: {e}", messages.ERROR
                )
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
        user = request.user
        applications = Application.objects.all()
        seven_days_ago = timezone.now() - timedelta(days=7)

        new_allusers_total = applications.filter(status=ApplicationStatus.NEW)
        nac_owner_total_count = applications.filter(
            status=ApplicationStatus.CURRENTLY_WITH_NAC, owner=user
        ).count()
        nac_allusers_total_count = applications.filter(
            status=ApplicationStatus.CURRENTLY_WITH_NAC
        ).count()
        context = admin.site.each_context(request)
        context.update(
            {
                "user_id": user.id,
                "new_allusers_total": new_allusers_total,
                "new_allusers_total_count": new_allusers_total.count(),
                "nac_owner_total_count": nac_owner_total_count,
                "nac_allusers_total_count": nac_allusers_total_count,
                "user_name": user.username,
                "is_nav_sidebar_enabled": True,
            }
        )

        if user.is_superuser:
            ready2i_allusers_total_count = applications.filter(
                status=ApplicationStatus.READY_2I,
            ).count()
            ready2i_owner_total_count = applications.filter(
                status=ApplicationStatus.READY_2I, owner=user
            ).count()
            ready2i_owner_late = applications.filter(
                status=ApplicationStatus.READY_2I,
                time_submitted__lt=seven_days_ago,
                owner=user,
            )
            ready2i_owner_onschedule = applications.filter(
                status=ApplicationStatus.READY_2I,
                time_submitted__gte=seven_days_ago,
                owner=user,
            )
            ready2i_all_onschedule_count = applications.filter(
                status=ApplicationStatus.READY_2I, time_submitted__gte=seven_days_ago
            ).count()
            context.update(
                {
                    "user_is_reviewer": False,
                    "ready2i_allusers_total_count": ready2i_allusers_total_count,
                    "ready2i_owner_total_count": ready2i_owner_total_count,
                    "ready2i_owner_late": ready2i_owner_late,
                    "ready2i_owner_onschedule": ready2i_owner_onschedule,
                    "ready2i_all_onschedule_count": ready2i_all_onschedule_count,
                }
            )
        else:
            inprogress_allusers_total_count = applications.filter(
                status=ApplicationStatus.IN_PROGRESS
            ).count()
            inprogress_owner_total_count = applications.filter(
                status=ApplicationStatus.IN_PROGRESS,
                owner=user,
            ).count()
            moreinfo_allusers_total_count = applications.filter(
                status=ApplicationStatus.MORE_INFORMATION,
            ).count()
            moreinfo_owner_total_count = applications.filter(
                status=ApplicationStatus.MORE_INFORMATION, owner=user
            ).count()
            moreinfo_owner_late = applications.filter(
                status=ApplicationStatus.MORE_INFORMATION,
                time_submitted__lt=seven_days_ago,
                owner=user,
            )
            moreinfo_owner_onschedule = applications.filter(
                status=ApplicationStatus.MORE_INFORMATION,
                time_submitted__gte=seven_days_ago,
                owner=user,
            )
            context.update(
                {
                    "user_is_reviewer": True,
                    "inprogress_allusers_total_count": inprogress_allusers_total_count,
                    "inprogress_owner_total_count": inprogress_owner_total_count,
                    "moreinfo_allusers_total_count": moreinfo_allusers_total_count,
                    "moreinfo_owner_total_count": moreinfo_owner_total_count,
                    "moreinfo_owner_late": moreinfo_owner_late,
                    "moreinfo_owner_onschedule": moreinfo_owner_onschedule,
                }
            )

        return render(request, "admin/dashboard.html", context)
