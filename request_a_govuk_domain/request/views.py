import json
import os
import random
import string
from datetime import datetime
from django.views.generic import TemplateView, RedirectView
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from .forms import (
    DomainConfirmationForm,
    RegistrarEmailForm,
    ExemptionForm,
    UploadForm,
    RegistrarDetailsForm,
    RegistrantTypeForm,
    DomainPurposeForm,
    DomainForm,
    MinisterForm,
    ApplicantDetailsForm,
    RegistrantDetailsNonCentralGovForm,
    RegistryDetailsForm,
    WrittenPermissionForm,
)
from .models.organisation import Registrar
from django.views.generic.edit import FormView

from .utils import (
    add_value_to_session,
    handle_uploaded_file,
    add_to_session,
    remove_from_session,
    is_central_government,
    route_number,
)

# ==== V2 ===


class RegistrarDetailsView(FormView):
    template_name = "registrar_details.html"
    form_class = RegistrarDetailsForm
    success_url = reverse_lazy("registrant_type")
    change = False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["change"] = getattr(self, "change")
        return kwargs

    def form_valid(self, form):
        add_to_session(form, self.request, ["registrar_organisation"])
        if "back_to_answers" in self.request.POST.keys():
            self.success_url = reverse_lazy("confirm")
        return super().form_valid(form)


class RegistrantTypeView(FormView):
    template_name = "registrant_type.html"
    success_url = reverse_lazy("domain")  # TODO: by default should be an error page
    form_class = RegistrantTypeForm

    def form_valid(self, form):
        registration_data = add_to_session(form, self.request, ["registrant_type"])
        route = route_number(registration_data)
        if route == "1":
            self.success_url = reverse_lazy("domain")
        elif route == "2":
            self.success_url = reverse_lazy("domain_purpose")
        elif route == "3":
            self.success_url = reverse_lazy("written_permission_local_gov")
        elif route == "4":
            self.success_url = reverse_lazy("registrant_type_fail")
        return super().form_valid(form)


class DomainView(FormView):
    template_name = "domain.html"
    form_class = DomainForm
    success_url = reverse_lazy("domain_confirmation")
    change = False

    def get_initial(self):
        initial = super().get_initial()
        session_data = self.request.session["registration_data"]
        initial["domain_name"] = session_data.get("domain_name", "")
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["change"] = getattr(self, "change")
        return kwargs

    def form_valid(self, form):
        registration_data = add_to_session(form, self.request, ["domain_name"])
        if "back_to_answers" in self.request.POST.keys():
            self.success_url = reverse_lazy("confirm")
        elif is_central_government(registration_data["registrant_type"]):
            self.success_url = reverse_lazy("minister")
        return super().form_valid(form)


class DomainConfirmationView(FormView):
    template_name = "domain_confirmation.html"
    form_class = DomainConfirmationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["registration_data"] = self.request.session.get("registration_data", {})
        return context

    def form_valid(self, form):
        if form.cleaned_data["domain_confirmation"] == "yes":
            route = route_number(self.request.session["registration_data"])
            if route == "1" or route == "3":
                self.success_url = reverse_lazy("registrant_details_non_central_gov")
            else:
                self.success_url = reverse_lazy("minister")
        else:
            self.success_url = reverse_lazy("domain")  # Route 12
        return super().form_valid(form)


class RegistrantDetailsNonCentralGovView(FormView):
    template_name = "registrant_details_non_central_gov.html"
    form_class = RegistrantDetailsNonCentralGovForm
    success_url = reverse_lazy("registry_details")
    change = False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["change"] = getattr(self, "change")
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        session_data = self.request.session["registration_data"]
        initial["registrant_organisation"] = session_data.get(
            "registrant_organisation", ""
        )
        initial["registrant_full_name"] = session_data.get("registrant_full_name", "")
        initial["registrant_phone"] = session_data.get("registrant_phone", "")
        initial["registrant_email"] = session_data.get("registrant_email", "")
        return initial

    def form_valid(self, form):
        add_to_session(
            form,
            self.request,
            [
                "registrant_organisation",
                "registrant_full_name",
                "registrant_phone",
                "registrant_email",
            ],
        )
        if "back_to_answers" in self.request.POST.keys():
            self.success_url = "confirm"
        return super().form_valid(form)


class RegistryDetailsView(FormView):
    template_name = "registry_details.html"
    form_class = RegistryDetailsForm
    success_url = reverse_lazy("confirm")
    change = False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["change"] = getattr(self, "change")
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        session_data = self.request.session["registration_data"]
        initial["registrant_role"] = session_data.get("registrant_role", "")
        initial["registrant_contact_phone"] = session_data.get(
            "registrant_contact_phone", ""
        )
        initial["registrant_contact_email"] = session_data.get(
            "registrant_contact_email", ""
        )
        return initial

    def form_valid(self, form):
        add_to_session(
            form,
            self.request,
            ["registrant_role", "registrant_contact_phone", "registrant_contact_email"],
        )
        return super().form_valid(form)


# ==== V1 ===


class RegistrarEmailView(FormView):
    template_name = "email.html"
    form_class = RegistrarEmailForm
    success_url = reverse_lazy("registrant_type")
    change = False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["change"] = getattr(self, "change")
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        session_data = self.request.session["registration_data"]
        initial["registrar_email_address"] = session_data.get(
            "registrar_email_address", ""
        )
        return initial

    def form_valid(self, form):
        add_to_session(form, self.request, ["registrar_email_address"])
        if "back_to_answers" in self.request.POST.keys():
            self.success_url = "confirm"
        return super().form_valid(form)


class ApplicantDetailsView(FormView):
    template_name = "applicant_details.html"
    form_class = ApplicantDetailsForm
    success_url = reverse_lazy("registrant_details")
    change = False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["change"] = getattr(self, "change")
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        session_data = self.request.session["registration_data"]
        initial["applicant_name"] = session_data.get("applicant_name", "")
        initial["applicant_phone"] = session_data.get("applicant_phone", "")
        initial["applicant_email"] = session_data.get("applicant_email", "")
        return initial

    def form_valid(self, form):
        add_to_session(
            form, self.request, ["applicant_name", "applicant_phone", "applicant_email"]
        )
        if "back_to_answers" in self.request.POST.keys():
            self.success_url = "confirm"
        return super().form_valid(form)


class RegistrantTypeFailView(TemplateView):
    template_name = "registrant_type_fail.html"


class WrittenPermissionView(FormView):
    template_name = "written_permission.html"
    form_class = WrittenPermissionForm
    success_url = reverse_lazy("written_permission_upload")
    change = False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["change"] = getattr(self, "change")
        return kwargs

    def form_valid(self, form):
        registration_data = add_to_session(form, self.request, ["written_permission"])
        # We need to store the fact that we're changing the value,
        # as we're going to have to add the "Back to the answers"
        # 2 pages later
        add_value_to_session(self.request, "change", self.change)
        if registration_data["written_permission"] == "no":
            self.success_url = reverse_lazy("written_permission_fail")
        return super().form_valid(form)


class WrittenPermissionFailView(TemplateView):
    template_name = "written_permission_fail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        registration_data = self.request.session.get("registration_data", {})

        # Set is_central_government in the context, which is used to display the relevant message
        # on the written_permission_fail.html page
        context["is_central_government"] = is_central_government(
            registration_data["registrant_type"]
        )
        return context


class UploadRemoveView(RedirectView):
    page_type = ""  # to be subclassed
    permanent = False
    query_string = True
    pattern_name = ""  # to be subclassed

    def get_redirect_url(self, *args, **kwargs):
        # delete the uploaded file
        file_name = self.request.session["registration_data"].get(
            self.page_type + "_file_uploaded_filename"
        )
        if file_name is not None:
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # delete the filenames from the session data
        remove_from_session(
            self.request.session,
            [
                self.page_type + "_file_uploaded_filename",
                self.page_type + "_file_original_filename",
            ],
        )

        return super().get_redirect_url(*args, **kwargs)


class ExemptionUploadRemoveView(UploadRemoveView):
    page_type = "exemption"
    pattern_name = "exemption_upload"


class WrittenPermissionUploadRemoveView(UploadRemoveView):
    page_type = "written_permission"
    pattern_name = "written_permission_upload"


class MinisterUploadRemoveView(UploadRemoveView):
    page_type = "minister"
    pattern_name = "minister_upload"


class ConfirmView(TemplateView):
    template_name = "confirm.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Access session data and include it in the context
        registration_data = self.request.session.get("registration_data", {})
        context["registration_data"] = registration_data

        # Registrar organisation name
        registrar_id = int(
            registration_data["registrar_organisation"].split("registrar-", 1)[1]
        )
        context["registrar_name"] = Registrar.objects.get(id=registrar_id).name

        # Domain purpose
        if is_central_government(registration_data["registrant_type"]):
            context["reason_for_request"] = registration_data["domain_purpose"]

        # Exemption
        if "registrant_type" in registration_data and is_central_government(
            registration_data["registrant_type"]
        ):
            context["central_gov"] = True

        return context


class SuccessView(View):
    def get(self, request):
        # TODO Change when requirements are finalised and add comment accordingly
        reference_number = (
            "GOVUK"
            + datetime.today().strftime("%d%m%Y")
            + "".join(random.choice(string.ascii_uppercase) for _ in range(4))
        )

        # We're finished, so clear the session data
        request.session.pop("registration_data", None)
        return render(request, "success.html", {"reference_number": reference_number})


class ExemptionView(FormView):
    template_name = "exemption.html"
    form_class = ExemptionForm

    def form_valid(self, form):
        registration_data = add_to_session(form, self.request, ["exemption"])
        exemption = registration_data["exemption"]
        if exemption == "yes":
            self.success_url = reverse_lazy("exemption_upload")
        else:
            self.success_url = reverse_lazy("exemption_fail")
        return super().form_valid(form)


class MinisterView(FormView):
    template_name = "minister.html"
    form_class = MinisterForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["registration_data"] = self.request.session.get("registration_data", {})
        return context

    def form_valid(self, form):
        registration_data = add_to_session(form, self.request, ["minister"])
        minister = registration_data["minister"]
        if minister == "yes":
            self.success_url = reverse_lazy("minister_upload")
        else:
            self.success_url = reverse_lazy("applicant_details")
        return super().form_valid(form)


class UploadView(FormView):
    page_type = ""
    template_name = ""
    success_url = None
    form_class = UploadForm

    def __init__(self):
        self.success_url = reverse_lazy(f"{self.page_type}_upload_confirm")
        self.template_name = f"{self.page_type}_upload.html"
        return super().__init__()

    def form_valid(self, form):
        saved_filename = handle_uploaded_file(self.request.FILES["file"])
        registration_data = self.request.session.get("registration_data", {})
        registration_data[f"{self.page_type}_file_uploaded_filename"] = saved_filename
        registration_data[
            f"{self.page_type}_file_original_filename"
        ] = self.request.FILES["file"].name
        self.request.session["registration_data"] = registration_data
        if "back_to_answers" in self.request.POST.keys():
            self.success_url = reverse_lazy("confirm")
        return super().form_valid(form)


class UploadConfirmView(TemplateView):
    page_type = ""
    template_name = ""

    def get_context_data(self, **kwargs):
        self.template_name = f"{self.page_type}_upload_confirm.html"
        context = super().get_context_data(**kwargs)
        context["registration_data"] = self.request.session.get("registration_data", {})
        return context


class ExemptionUploadView(UploadView):
    page_type = "exemption"


class MinisterUploadView(UploadView):
    page_type = "minister"


class WrittenPermissionUploadView(UploadView):
    page_type = "written_permission"


class ExemptionUploadConfirmView(UploadConfirmView):
    page_type = "exemption"


class MinisterUploadConfirmView(UploadConfirmView):
    page_type = "minister"


class WrittenPermissionUploadConfirmView(UploadConfirmView):
    page_type = "written_permission"


class ExemptionFailView(FormView):
    template_name = "exemption_fail.html"

    def get(self, request):
        return render(request, self.template_name)


class DomainPurposeView(FormView):
    template_name = "domain_purpose.html"
    form_class = DomainPurposeForm

    def form_valid(self, form):
        registration_data = add_to_session(form, self.request, ["domain_purpose"])
        purpose = registration_data["domain_purpose"]
        if purpose == "email-only":
            self.success_url = reverse_lazy("written_permission")
        elif purpose == "website-email":
            self.success_url = reverse_lazy("exemption")
        else:
            self.success_url = reverse_lazy("domain_purpose_fail")

        return super().form_valid(form)


class DomainPurposeFailView(FormView):
    template_name = "domain_purpose_fail.html"

    def get(self, request):
        return render(request, self.template_name)


def answers_context_processor(request):
    """Temporary for ease of development: This sends the "answers" object to each form
    so we can display the data collected so far on every page"""
    answers = request.session.get("registration_data", {})
    answers_json = json.dumps(answers, indent=4)
    return {"answers": answers_json}
