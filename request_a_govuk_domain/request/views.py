import json
import random
import string
from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from .forms import (
    EmailForm,
    ExemptionForm,
    ExemptionUploadForm,
    RegistrarForm,
    RegistrantTypeForm,
    DomainPurposeForm,
    RegistrantForm,
    DomainForm,
    MinisterForm,
    MinisterUploadForm,
    ApplicantDetailsForm,
    RegistrantDetailsForm,
    RegistryDetailsForm,
    WrittenPermissionForm,
    WrittenPermissionUploadForm,
)

from django.views.generic.edit import FormView

from .utils import handle_uploaded_file, add_to_session, is_central_government

"""
Some views are example views, please modify remove as needed
"""


class EmailView(FormView):
    template_name = "email.html"

    def get(self, request):
        params = {}
        if "change" in request.GET:
            params["registrant_email_address"] = request.session["registration_data"][
                "registrant_email_address"
            ]
            form = EmailForm(params)
        else:
            form = EmailForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = EmailForm(request.POST)
        if form.is_valid():
            add_to_session(form, request, ["registrant_email_address"])
            if "cancel" in request.POST:
                return redirect("confirm")
            else:
                return redirect("registrant_type")
        return render(request, self.template_name, {"form": form})


class DomainView(FormView):
    template_name = "domain.html"
    form_class = DomainForm

    def form_valid(self, form):
        _, registration_data = add_to_session(form, self.request, ["domain_name"])
        if is_central_government(registration_data["registrant_type"]):
            self.success_url = reverse_lazy("minister")
        else:
            self.success_url = reverse_lazy("applicant_details")

        return super().form_valid(form)


class ApplicantDetailsView(FormView):
    template_name = "applicant_details.html"
    form_class = ApplicantDetailsForm

    def form_valid(self, form):
        field_names = ["applicant_name", "applicant_phone", "applicant_email"]
        add_to_session(form, self.request, field_names)
        self.success_url = reverse_lazy("registrant_details")
        return super().form_valid(form)


class RegistrantDetailsView(FormView):
    template_name = "registrant_details.html"
    form_class = RegistrantDetailsForm

    def form_valid(self, form):
        field_names = [
            "registrant_full_name",
            "registrant_phone",
            "registrant_email_address",
        ]
        add_to_session(form, self.request, field_names)
        self.success_url = reverse_lazy("registry_details")
        return super().form_valid(form)


class RegistryDetailsView(FormView):
    template_name = "registry_details.html"
    form_class = RegistryDetailsForm

    def form_valid(self, form):
        field_names = [
            "registrant_role",
            "registrant_contact_phone",
            "registrant_contact_email",
        ]
        add_to_session(form, self.request, field_names)
        self.success_url = reverse_lazy("confirm")
        return super().form_valid(form)


class RegistrantTypeView(FormView):
    template_name = "registrant_type.html"

    def get(self, request):
        params = {}
        if "change" in request.GET:
            params["registrant_type"] = request.session["registration_data"][
                "registrant_type"
            ]
            form = RegistrantTypeForm(params)
        else:
            form = RegistrantTypeForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = RegistrantTypeForm(request.POST)
        if form.is_valid():
            registrant_type, _ = add_to_session(form, request, ["registrant_type"])
            if registrant_type == "none":
                return redirect("registrant_type_fail")
            else:
                return redirect("registrant")
        return render(request, self.template_name, {"form": form})


class RegistrantTypeFailView(TemplateView):
    template_name = "registrant_type_fail.html"


class RegistrantView(FormView):
    template_name = "registrant.html"
    form_class = RegistrantForm
    success_url = reverse_lazy("written_permission")

    def form_valid(self, form):
        _, registration_data = add_to_session(
            form, self.request, ["registrant_organisation_name"]
        )
        if is_central_government(registration_data["registrant_type"]):
            self.success_url = reverse_lazy("domain_purpose")
        return super().form_valid(form)


class WrittenPermissionView(FormView):
    template_name = "written_permission.html"
    form_class = WrittenPermissionForm
    success_url = reverse_lazy("written_permission_upload")

    def form_valid(self, form):
        written_permission, _ = add_to_session(
            form, self.request, ["written_permission"]
        )
        if written_permission == "no":
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


class ConfirmView(TemplateView):
    template_name = "confirm.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Access session data and include it in the context
        registration_data = self.request.session.get("registration_data", {})
        context["registration_data"] = registration_data

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
        exe_radio = form.cleaned_data["exe_radio"]
        exe_radio = dict(form.fields["exe_radio"].choices)[exe_radio]
        if exe_radio == "Yes":
            self.success_url = reverse_lazy("exemption_upload")
        else:
            self.success_url = reverse_lazy("exemption_fail")
        return super().form_valid(form)


class MinisterView(FormView):
    template_name = "minister.html"
    form_class = MinisterForm

    def form_valid(self, form):
        minister_radios = form.cleaned_data["minister_radios"]
        minister_radios = dict(form.fields["minister_radios"].choices)[minister_radios]
        if minister_radios == "Yes":
            self.success_url = reverse_lazy("minister_upload")
        else:
            self.success_url = reverse_lazy("registrant_details")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["domain_name"] = self.request.session.get("domain", "")
        return context


class ExemptionUploadView(FormView):
    template_name = "exemption_upload.html"

    def get(self, request):
        form = ExemptionUploadForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        """
        If the file is an image we encode using base64
        ex: b64encode(form.cleaned_data['file'].read()).decode('utf-8')
        If the file is a pdf we do not encode
        """
        form = ExemptionUploadForm(request.POST, request.FILES)

        if form.is_valid():
            handle_uploaded_file(request.FILES["file"])
            return render(
                request,
                "exemption_upload_confirm.html",
                {"file": request.FILES["file"]},
            )
        return render(request, self.template_name, {"form": form})


class MinisterUploadView(FormView):
    template_name = "minister_upload.html"

    def get(self, request):
        form = MinisterUploadForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        """
        If the file is an image we encode using base64
        ex: b64encode(form.cleaned_data['file'].read()).decode('utf-8')
        If the file is a pdf we do not encode
        """
        form = MinisterUploadForm(request.POST, request.FILES)

        if form.is_valid():
            handle_uploaded_file(request.FILES["file"])
            return render(
                request,
                "minister_upload_confirm.html",
                {"file": request.FILES["file"]},
            )
        return render(request, self.template_name, {"form": form})


class WrittenPermissionUploadView(FormView):
    template_name = "written_permission_upload.html"

    def get(self, request):
        form = WrittenPermissionUploadForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        """
        If the file is an image we encode using base64
        ex: b64encode(form.cleaned_data['file'].read()).decode('utf-8')
        If the file is a pdf we do not encode
        """
        form = WrittenPermissionUploadForm(request.POST, request.FILES)

        if form.is_valid():
            handle_uploaded_file(request.FILES["file"])
            return render(
                request,
                "written_permission_upload_confirm.html",
                {"file": request.FILES["file"]},
            )
        return render(request, self.template_name, {"form": form})


class ExemptionFailView(FormView):
    template_name = "exemption_fail.html"

    def get(self, request):
        return render(request, self.template_name)


class RegistrarView(FormView):
    template_name = "registrar.html"
    form_class = RegistrarForm
    success_url = reverse_lazy("email")

    def form_valid(self, form):
        self.request.session["registration_data"] = {
            "registrar_organisation": form.cleaned_data["organisations_choice"]
        }
        return super().form_valid(form)


class DomainPurposeView(FormView):
    template_name = "domain_purpose.html"
    form_class = DomainPurposeForm

    def form_valid(self, form):
        purpose, _ = add_to_session(form, self.request, ["domain_purpose"])

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
