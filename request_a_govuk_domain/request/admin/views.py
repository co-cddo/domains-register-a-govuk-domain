import logging


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
                # send email
                send_approval_or_rejection_email(request)
                self._set_application_status(request)
                # To show the backend app user a message "[Approval/Rejection] email sent", get the type of
                # action ( i.e. whether it is Approval or Rejection )
                approval_or_rejection = request.POST["action"].capitalize()
                self.message_user(
                    request, f"{approval_or_rejection} email sent", messages.SUCCESS
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
