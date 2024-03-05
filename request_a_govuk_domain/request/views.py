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
)
from .models import RegistrationData
from django.views.generic.edit import FormView

from .utils import handle_uploaded_file


"""
Some views are example views, please modify remove as needed
"""


class NameView(FormView):
    template_name = "name.html"
    form_class = NameForm
    success_url = reverse_lazy("email")

    def form_valid(self, form):
        self.request.session["registration_data"] = {
            "registrant_full_name": form.cleaned_data["registrant_full_name"]
        }
        return super().form_valid(form)


class EmailView(FormView):
    template_name = "email.html"
    form_class = EmailForm
    success_url = reverse_lazy("registrant_type")

    def form_valid(self, form):
        registration_data = self.request.session.get("registration_data", {})
        registration_data["registrant_email_address"] = form.cleaned_data[
            "registrant_email_address"
        ]
        self.request.session["registration_data"] = registration_data
        return super().form_valid(form)


class RegistrantTypeView(FormView):
    template_name = "registrant_type.html"
    form_class = RegistrantTypeForm
    success_url = reverse_lazy("confirm")

    def form_valid(self, form):
        registration_data = self.request.session.get("registration_data", {})
        registration_data["registrant_type"] = form.cleaned_data["registrant_type"]
        self.request.session["registration_data"] = registration_data
        if form.cleaned_data["registrant_type"] == "none":
            self.success_url = reverse_lazy("registrant_type_fail")
        return super().form_valid(form)


class RegistrantTypeFailView(TemplateView):
    template_name = "registrant_type_fail.html"


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

    def get(self, request):
        form = ExemptionForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ExemptionForm(request.POST or None)

        if form.is_valid():
            exe_radio = form.cleaned_data["exe_radio"]
            exe_radio = dict(form.fields["exe_radio"].choices)[exe_radio]
            if exe_radio == "Yes":
                return redirect("exemption_upload")
            else:
                return redirect("exemption_fail")
        return render(request, self.template_name, {"form": form})


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
        return render(request, "exemption_fail.html")


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
        # TBC: this is generic for now, but routing needs to be added
        registration_data = self.request.session.get("registration_data", {})
        registration_data["domain_purpose"] = form.cleaned_data["domain_purpose"]
        self.request.session["registration_data"] = registration_data
        self.success_url = reverse_lazy("exemption")
        return super().form_valid(form)


def answers_context_processor(request):
    """Temporary for ease of development: This sends the "answers" object to each form
    so we can display the data collected so far on every page"""
    answers = request.session.get("registration_data", {})
    answers_json = json.dumps(answers, indent=4)
    return {"answers": answers_json}
