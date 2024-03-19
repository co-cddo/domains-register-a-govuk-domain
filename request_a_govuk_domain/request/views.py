import json
import os
import random
import string
from datetime import datetime
from django.views.generic import TemplateView, RedirectView
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from .forms import (
    EmailForm,
    ExemptionForm,
    UploadForm,
    RegistrarForm,
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

from django.views.generic.edit import FormView

from .utils import (
    handle_uploaded_file,
    create_summary_list,
    RegistrationDataClass,
    add_to_session,
    remove_from_session,
    is_central_government,
)


def get_registration_data_to_prepopulate(request, fields, form):
    """
    Based on request we figure out if we are coming to this view
    from summary list.
    1. If coming from summary list we display back to button.
    2. We pre populate the data from registration_data dict.
    """
    params = {}
    if "change" in request.GET:
        for field in fields:
            registration_data = request.session["registration_data"]
            if registration_data:
                params[field] = registration_data.get(field, "")
        form = form(params)
    else:
        form = form()
    return form


class EmailView(FormView):
    template_name = "email.html"

    def get(self, request):
        form = get_registration_data_to_prepopulate(
            request, ["registrant_email_address"], EmailForm
        )
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = EmailForm(request.POST)
        if form.is_valid():
            add_to_session(form, request, ["registrant_email_address"])
            if "back_to_answers" in request.POST:
                return redirect("confirm")
            else:
                return redirect("registrant_type")
        return render(request, self.template_name, {"form": form})


class DomainView(FormView):
    template_name = "domain.html"

    def get(self, request):
        form = get_registration_data_to_prepopulate(
            request, ["domain_name"], DomainForm
        )
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = DomainForm(request.POST)
        if form.is_valid():
            _, registration_data = add_to_session(form, self.request, ["domain_name"])
            if "back_to_answers" in request.POST:
                return redirect("confirm")
            elif is_central_government(registration_data["registrant_type"]):
                return redirect("minister")
            else:
                return redirect("applicant_details")
        return render(request, self.template_name, {"form": form})


class ApplicantDetailsView(FormView):
    template_name = "applicant_details.html"

    def get(self, request):
        form = get_registration_data_to_prepopulate(
            request,
            ["applicant_name", "applicant_phone", "applicant_email"],
            ApplicantDetailsForm,
        )
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ApplicantDetailsForm(request.POST)
        if form.is_valid():
            _, registration_data = add_to_session(
                form,
                self.request,
                ["applicant_name", "applicant_phone", "applicant_email"],
            )
            if "back_to_answers" in request.POST:
                return redirect("confirm")
            else:
                return redirect("registrant_details")
        return render(request, self.template_name, {"form": form})


class RegistrantDetailsView(FormView):
    template_name = "registrant_details.html"

    def get(self, request):
        form = get_registration_data_to_prepopulate(
            request,
            ["registrant_full_name", "registrant_phone", "registrant_email_address"],
            RegistrantDetailsForm,
        )
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = RegistrantDetailsForm(request.POST)
        if form.is_valid():
            field_names = [
                "registrant_full_name",
                "registrant_phone",
                "registrant_email_address",
            ]
            add_to_session(form, self.request, field_names)
            if "back_to_answers" in request.POST:
                return redirect("confirm")
            else:
                return redirect("registry_details")
        return render(request, self.template_name, {"form": form})


class RegistryDetailsView(FormView):
    template_name = "registry_details.html"

    def get(self, request):
        form = get_registration_data_to_prepopulate(
            request,
            ["registrant_role", "registrant_contact_phone", "registrant_contact_email"],
            RegistryDetailsForm,
        )
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = RegistryDetailsForm(request.POST)
        if form.is_valid():
            field_names = [
                "registrant_role",
                "registrant_contact_phone",
                "registrant_contact_email",
            ]
            add_to_session(form, self.request, field_names)
            return redirect("confirm")
        return render(request, self.template_name, {"form": form})


class RegistrantTypeView(FormView):
    template_name = "registrant_type.html"

    def get(self, request):
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

    def get(self, request):
        form = get_registration_data_to_prepopulate(
            request, ["registrant_organisation_name"], RegistrantForm
        )
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = RegistrantForm(request.POST)
        if form.is_valid():
            _, registration_data = add_to_session(
                form, self.request, ["registrant_organisation_name"]
            )
            if "back_to_answers" in request.POST:
                return redirect("confirm")
            elif is_central_government(registration_data["registrant_type"]):
                return redirect("domain_purpose")
            else:
                return redirect("written_permission")
        return render(request, self.template_name, {"form": form})


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

        registration_objs = []
        for summary_item in create_summary_list(
            self.request.session["registration_data"]
        ):
            registration_obj = RegistrationDataClass(summary_item)
            registration_objs.append(registration_obj)

        # Access session data and include it in the context
        registration_data = self.request.session.get("registration_data", {})
        context["registration_data"] = registration_data
        context["registration_objs"] = registration_objs

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

    def get(self, request):
        form = get_registration_data_to_prepopulate(
            request, ["exe_radio"], ExemptionForm
        )
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ExemptionForm(request.POST)
        if form.is_valid():
            exe_radio, _ = add_to_session(form, self.request, ["exe_radio"])
            if "back_to_answers" in request.POST:
                return redirect("confirm")
            elif exe_radio == "yes":
                return redirect("exemption_upload")
            else:
                return redirect("written_permission")
        return render(request, self.template_name, {"form": form})


class MinisterView(FormView):
    template_name = "minister.html"
    form_class = MinisterForm

    def form_valid(self, form):
        minister_radios, _ = add_to_session(form, self.request, ["minister_radios"])
        if minister_radios == "yes":
            self.success_url = reverse_lazy("minister_upload")
        else:
            self.success_url = reverse_lazy("registrant_details")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["domain_name"] = self.request.session.get("domain", "")
        return context


class UploadView(FormView):
    page_type = ""

    def get(self, request):
        form = UploadForm()
        return render(request, f"{self.page_type}_upload.html", {"form": form})

    def post(self, request):
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            saved_filename = handle_uploaded_file(request.FILES["file"])
            registration_data = request.session.get("registration_data", {})
            registration_data[
                f"{self.page_type}_file_uploaded_filename"
            ] = saved_filename
            registration_data[
                f"{self.page_type}_file_original_filename"
            ] = request.FILES["file"].name
            request.session["registration_data"] = registration_data
            return render(
                request,
                f"{self.page_type}_upload_confirm.html",
                {
                    "original_filename": request.FILES["file"].name,
                    "uploaded_filename": saved_filename,
                },
            )
        return render(request, f"{self.page_type}_upload.html", {"form": form})


class ExemptionUploadView(UploadView):
    page_type = "exemption"


class MinisterUploadView(UploadView):
    page_type = "minister"


class WrittenPermissionUploadView(UploadView):
    page_type = "written_permission"


class ExemptionFailView(FormView):
    template_name = "exemption_fail.html"

    def get(self, request):
        return render(request, self.template_name)


class RegistrarView(FormView):
    template_name = "registrar.html"

    def get(self, request):
        form = get_registration_data_to_prepopulate(
            request, ["organisations_choice"], RegistrarForm
        )
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = RegistrarForm(request.POST)
        if form.is_valid():
            field_names = ["organisations_choice"]
            add_to_session(form, self.request, field_names)
            if "back_to_answers" in request.POST:
                return redirect("confirm")
            else:
                return redirect("email")
        return render(request, self.template_name, {"form": form})


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
