import json
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from .forms import (
    NameForm,
    EmailForm,
    ExemptionForm,
    ExemptionUploadForm,
    RegistrarForm,
    ConfirmForm,
    RegistrantTypeForm,
    DomainPurposeForm,
    RegistrantForm,
    DomainForm,
    MinisterForm,
    ApplicantDetailsForm,
    RegistrantDetailsForm,
    RegistryDetailsForm,
    WrittenPermissionForm,
)
from .models import RegistrationData
from django.views.generic.edit import FormView

from .utils import handle_uploaded_file


"""
Some views are example views, please modify remove as needed
"""


class NameView(FormView):
    template_name = "name.html"

    def get(self, request):
        params = {}
        if "change" in request.GET:
            params["registrant_full_name"] = request.session["registration_data"][
                "registrant_full_name"
            ]
            form = NameForm(params)
        else:
            form = NameForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = NameForm(request.POST)
        if form.is_valid():
            registration_data = request.session.get("registration_data", {})
            registration_data["registrant_full_name"] = form.cleaned_data[
                "registrant_full_name"
            ]
            request.session["registration_data"] = registration_data
            if "cancel" in request.POST:
                return redirect("confirm")
            else:
                return redirect("email")
        return render(request, self.template_name, {"form": form})


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
            registration_data = request.session.get("registration_data", {})
            registration_data["registrant_email_address"] = form.cleaned_data[
                "registrant_email_address"
            ]
            request.session["registration_data"] = registration_data
            if "cancel" in request.POST:
                return redirect("confirm")
            else:
                return redirect("registrant_type")
        return render(request, self.template_name, {"form": form})


class DomainView(FormView):
    template_name = "domain.html"
    form_class = DomainForm

    def form_valid(self, form):
        registration_data = self.request.session.get("registration_data", {})
        registration_data["domain_name"] = form.cleaned_data["domain_name"]
        self.request.session["registration_data"] = registration_data

        if registration_data["registrant_type"] == "central_gov":
            self.success_url = reverse_lazy("minister")
        else:
            self.success_url = reverse_lazy("applicant_details")

        return super().form_valid(form)


class ApplicantDetailsView(FormView):
    template_name = "applicant_details.html"
    form_class = ApplicantDetailsForm

    def form_valid(self, form):
        registration_data = self.request.session.get("registration_data", {})
        registration_data["applicant_name"] = form.cleaned_data["applicant_name"]
        registration_data["applicant_telephone_number"] = form.cleaned_data[
            "applicant_telephone_number"
        ]
        registration_data["applicant_email_address"] = form.cleaned_data[
            "applicant_email_address"
        ]
        self.request.session["registration_data"] = registration_data
        self.success_url = reverse_lazy("registrant_details")
        return super().form_valid(form)


class RegistrantDetailsView(FormView):
    template_name = "registrant_details.html"
    form_class = RegistrantDetailsForm

    def form_valid(self, form):
        registration_data = self.request.session.get("registration_data", {})
        registration_data["registrant_name"] = form.cleaned_data["registrant_name"]
        registration_data["registrant_telephone_number"] = form.cleaned_data[
            "registrant_telephone_number"
        ]
        registration_data["registrant_email_address"] = form.cleaned_data[
            "registrant_email_address"
        ]
        self.request.session["registration_data"] = registration_data
        self.success_url = reverse_lazy("registry_details")
        return super().form_valid(form)


class RegistryDetailsView(FormView):
    template_name = "registry_details.html"
    form_class = RegistryDetailsForm

    def form_valid(self, form):
        registration_data = self.request.session.get("registration_data", {})
        registration_data["registrant_role"] = form.cleaned_data["registrant_role"]
        registration_data["registrant_contact_details"] = form.cleaned_data[
            "registrant_contact_details"
        ]
        self.request.session["registration_data"] = registration_data
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
            registration_data = request.session.get("registration_data", {})
            registration_data["registrant_type"] = form.cleaned_data["registrant_type"]
            request.session["registration_data"] = registration_data
            if form.cleaned_data["registrant_type"] == "none":
                return redirect("registrant_type_fail")
            else:
                return redirect("confirm")
        return render(request, self.template_name, {"form": form})


class RegistrantTypeFailView(TemplateView):
    template_name = "registrant_type_fail.html"


class RegistrantView(FormView):
    template_name = "registrant.html"
    form_class = RegistrantForm
    success_url = reverse_lazy("written_permission")

    def form_valid(self, form):
        registration_data = self.request.session.get("registration_data", {})
        registration_data["registrant_organisation_name"] = form.cleaned_data[
            "registrant_organisation_name"
        ]
        self.request.session["registration_data"] = registration_data
        if registration_data["registrant_type"] == "central_gov":
            self.success_url = reverse_lazy("domain_purpose")
        return super().form_valid(form)


class WrittenPermissionView(FormView):
    template_name = "written_permission.html"
    form_class = WrittenPermissionForm
    success_url = reverse_lazy("confirm")

    def form_valid(self, form):
        registration_data = self.request.session.get("registration_data", {})
        written_permission = form.cleaned_data["written_permission"]
        registration_data["written_permission"] = written_permission
        self.request.session["registration_data"] = registration_data
        if written_permission == "no":
            self.success_url = reverse_lazy("written_permission_fail")
        return super().form_valid(form)


class WrittenPermissionFailView(TemplateView):
    template_name = "written_permission_fail.html"


class ConfirmView(FormView):
    template_name = "confirm.html"
    form_class = ConfirmForm
    success_url = reverse_lazy("success")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Access session data and include it in the context
        registration_data = self.request.session.get("registration_data", {})
        context["registration_data"] = registration_data

        return context

    def form_valid(self, form):
        registration_data = self.request.session.get("registration_data", {})

        # Save data to the database
        RegistrationData.objects.create(
            registrant_full_name=registration_data["registrant_full_name"],
            registrant_email_address=registration_data["registrant_email_address"],
        )

        # Clear session data after saving
        self.request.session.pop("registration_data", None)

        return super().form_valid(form)


class SuccessView(TemplateView):
    template_name = "success.html"


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
        exe_radio = form.cleaned_data["exe_radio"]
        exe_radio = dict(form.fields["exe_radio"].choices)[exe_radio]
        if exe_radio == "Yes":
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
        purpose = form.cleaned_data["domain_purpose"]
        registration_data = self.request.session.get("registration_data", {})
        registration_data["domain_purpose"] = purpose
        self.request.session["registration_data"] = registration_data

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
