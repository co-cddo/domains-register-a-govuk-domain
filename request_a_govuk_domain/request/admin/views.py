import logging
from datetime import timedelta

from django import forms
from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import RedirectView

from request_a_govuk_domain.request.models import Application, ApplicationStatus, Review

from .email import send_approval_or_rejection_email

LOGGER = logging.getLogger(__name__)


class DecisionForm(forms.Form):
    """
    Form for confirming the decision on an application.
    """

    obj_id = forms.IntegerField(widget=forms.HiddenInput())
    action = forms.CharField(widget=forms.HiddenInput())
    status = forms.ChoiceField(choices=ApplicationStatus.choices)
    ar_reason = forms.CharField(required=False, widget=forms.Textarea)


class DecisionConfirmationView(View, admin.ModelAdmin):
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_sub_status_choices(self, action):
        """
        Retrieve a list of sub-status choices for the application
        based on the action (approval/rejection).
        :param action: sub-status choices (approval or rejection).
        :return: A list of dictionaries with keys 'status' and 'label'.
        """
        action_map = {"approval": "approved", "rejection": "rejected"}
        action = action_map[action]
        sub_status_list = [
            {"status": status, "label": label} for status, label in ApplicationStatus.choices if action in status
        ]
        # Append the "other" key-value pair
        sub_status_list.append({"status": "other", "label": "Other"})
        return sub_status_list

    def get(self, request):
        action = request.GET.get("action")
        obj = Application.objects.get(pk=request.GET.get("obj_id"))
        review = Review.objects.filter(application__id=obj.id).first()
        sub_status_choices = self.get_sub_status_choices(action)

        # Prepare choices for the DecisionForm
        status_choices = [(choice["status"], choice["label"]) for choice in sub_status_choices]

        initial_data = {
            "obj_id": obj.id,
            "action": action,
        }
        form = DecisionForm(initial=initial_data)
        form.fields["status"].choices = status_choices  # Set choices dynamically

        context = {
            "obj": obj,
            "action": action,
            "reason": review.reason,
            "sub_status_choices": sub_status_choices,
            "form": form,
        }
        return render(request, "admin/application_decision_confirmation.html", context)

    def _set_application_status(self, obj, status):
        obj.status = ApplicationStatus(status)
        obj.time_decided = timezone.now()
        obj.save()

    def post(self, request):
        form = DecisionForm(request.POST)
        if form.is_valid():
            try:
                obj = get_object_or_404(Application, pk=form.cleaned_data["obj_id"])
                send_approval_or_rejection_email(request)
                self._set_application_status(obj, form.cleaned_data["status"])
                # To show the backend app user a message "[Approval/Rejection] email sent", get the type of
                # action ( i.e. whether it is Approval or Rejection )
                approval_or_rejection = request.POST["action"].capitalize()
                self.message_user(request, f"{approval_or_rejection} email sent", messages.SUCCESS)

                # Save sanitized reason
                obj.approval_or_rejection_comment = form.cleaned_data["ar_reason"]
                obj.save()

                LOGGER.info(f"Application {obj.reference} status set to {approval_or_rejection}")
                return HttpResponseRedirect(reverse("admin:request_review_changelist"))
            except Exception as e:
                LOGGER.error("Failed to send the email", exc_info=True)
                self.message_user(request, f"Email send failed: {e}", messages.ERROR)
        else:
            action = request.POST.get("action")
            obj = get_object_or_404(Application, pk=request.POST.get("obj_id"))
            review = Review.objects.filter(application__id=obj.id).first()
            sub_status_choices = self.get_sub_status_choices(action)
            context = {
                "obj": obj,
                "action": action,
                "reason": review.reason,
                "sub_status_choices": sub_status_choices,
                "form": form,
            }
            return render(request, "admin/application_decision_confirmation.html", context)

        review = Review.objects.filter(application__id=request.POST.get("obj_id")).first()
        return HttpResponseRedirect(reverse("admin:request_review_change", args=[review.id]))


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
        excluded_statuses = [
            ApplicationStatus.APPROVED,
            ApplicationStatus.REJECTED,
            ApplicationStatus.APPROVED_2I_CHECK_ACRONYM,
            ApplicationStatus.APPROVED_2I_CHECK_REGISTRANT,
            ApplicationStatus.APPROVED_2I_CHANGE_DOMAIN_NAME,
            ApplicationStatus.APPROVED_2I_GET_PERMISSION_LETTER,
            ApplicationStatus.APPROVED_2I_CHECK_REGISTRY_DETAILS,
            ApplicationStatus.APPROVED_PARKED,
            ApplicationStatus.APPROVED_WENT_THROUGH_NAC,
            ApplicationStatus.APPROVED_DOMAINS_TEAM_DISCUSSION,
            ApplicationStatus.APPROVED_REVIEWER_CHANGE_DOMAIN_NAME_BEFORE_2I,
            ApplicationStatus.APPROVED_REVIEWER_CHECK_REGISTRANT_BEFORE_2I,
            ApplicationStatus.APPROVED_REVIEWER_CHECK_ACRONYM_BEFORE_2I,
            ApplicationStatus.APPROVED_REVIEWER_CHECK_REGISTRY_DETAILS_BEFORE_2I,
            ApplicationStatus.APPROVED_REVIEWER_CHANGE_NAME_BEFORE_2I,
            ApplicationStatus.REJECTED_WITH_NAC,
            ApplicationStatus.REJECTED_DUPLICATE_APPLICATION,
            ApplicationStatus.REJECTED_REGISTRAR_ERROR,
        ]
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
                self.message_user(request, "Application status changed", messages.SUCCESS)
                obj = Application.objects.get(pk=request.GET.get("obj_id"))
                LOGGER.info(f"Application {obj.reference} status set to {obj.status}")
                return HttpResponseRedirect(reverse("admin:request_review_changelist"))
            except Exception as e:
                LOGGER.error("Failed to change status of application", exc_info=True)
                self.message_user(request, f"Application status change failed: {e}", messages.ERROR)
        review = Review.objects.filter(application__id=request.POST.get("obj_id")).first()
        return HttpResponseRedirect(reverse("admin:request_review_change", args=[review.id]))


class AdminDashboardView(View, admin.ModelAdmin):
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        user = request.user
        applications = Application.objects.all()
        seven_days_ago = timezone.now() - timedelta(days=7)

        new_allusers_total = applications.filter(status=ApplicationStatus.NEW)
        nac_owner_total_count = applications.filter(status=ApplicationStatus.CURRENTLY_WITH_NAC, owner=user).count()
        nac_allusers_total_count = applications.filter(status=ApplicationStatus.CURRENTLY_WITH_NAC).count()
        context = admin.site.each_context(request)
        context.update(
            {
                "username": user.username,
                "userid": user.id,
                "new_allusers_total": new_allusers_total,
                "new_allusers_total_count": new_allusers_total.count(),
                "nac_owner_total_count": nac_owner_total_count,
                "nac_allusers_total_count": nac_allusers_total_count,
                "is_nav_sidebar_enabled": True,
            }
        )

        if user.is_superuser:
            ready2i_allusers_total_count = applications.filter(
                status=ApplicationStatus.READY_2I,
            ).count()
            ready2i_owner_total_count = applications.filter(status=ApplicationStatus.READY_2I, owner=user).count()
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
            inprogress_allusers_total_count = applications.filter(status=ApplicationStatus.IN_PROGRESS).count()
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


class ReviewByRefView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        try:
            application = Application.objects.get(reference=kwargs["ref"])
            review = Review.objects.get(application=application)
            return reverse("admin:request_review_change", args=[review.id])
        except Exception:
            return None


class ApplicationByRefView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        try:
            application = Application.objects.get(reference=kwargs["ref"])
            return reverse("admin:request_application_change", args=[application.id])
        except Exception:
            return None  # If the ref doesn't exist, return 410 Gone
