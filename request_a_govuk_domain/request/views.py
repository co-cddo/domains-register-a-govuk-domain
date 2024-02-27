from django.shortcuts import render, redirect
from django.views import View
from .forms import (
    NameForm,
    EmailForm,
    ExemptionForm,
    ExemptionUploadForm,
    RegistrarForm
)
from .models import RegistrationData
from django.views.generic.edit import FormView

from .utils import handle_uploaded_file, organisations_list


"""
All views are example views, please modify remove as needed
"""


class NameView(View):
    template_name = 'name.html'

    def get(self, request):
        form = NameForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = NameForm(request.POST)
        if form.is_valid():
            request.session['registration_data'] = {'registrant_full_name': form.cleaned_data['registrant_full_name']}
            return redirect('email')
        return render(request, self.template_name, {'form': form})


class EmailView(View):
    template_name = 'email.html'

    def get(self, request):
        form = EmailForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = EmailForm(request.POST)
        if form.is_valid():
            registration_data = request.session.get('registration_data', {})
            registration_data['registrant_email_address'] = form.cleaned_data['registrant_email_address']
            request.session['registration_data'] = registration_data
            return redirect('confirm')
        return render(request, self.template_name, {'form': form})


class ConfirmView(View):
    template_name = 'confirm.html'

    def get(self, request):
        registration_data = request.session.get('registration_data', {})
        return render(request, self.template_name, {'registration_data': registration_data})

    def post(self, request):
        registration_data = request.session.get('registration_data', {})

        # Save data to the database
        RegistrationData.objects.create(registrant_full_name=registration_data['registrant_full_name'],
                                        registrant_email_address=registration_data['registrant_email_address'])

        # Clear session data after saving
        request.session.pop('registration_data', None)

        return redirect('success')


class SuccessView(View):
    template_name = 'success.html'

    def get(self, request):
        return render(request, self.template_name, {})


class ExemptionView(FormView):
    template_name = 'exemption.html'

    def get(self, request):
        form = ExemptionForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ExemptionForm(request.POST or None)

        if form.is_valid():
            exe_radio = form.cleaned_data['exe_radio']
            exe_radio = dict(form.fields['exe_radio'].choices)[exe_radio]
            if exe_radio == 'Yes':
                return redirect('exemption_upload')
            else:
                return redirect('exemption_fail')
        return render(request, self.template_name, {'form': form})


class ExemptionUploadView(FormView):
    template_name = 'exemption_upload.html'

    def get(self, request):
        form = ExemptionUploadForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """
        If the file is an image we encode using base64
        ex: b64encode(form.cleaned_data['file'].read()).decode('utf-8')
        If the file is a pdf we do not encode
        """
        form = ExemptionUploadForm(request.POST, request.FILES)

        if form.is_valid():
            handle_uploaded_file(request.FILES["file"])
            return render(request,
                          'exemption_upload_confirm.html',
                          {'file': request.FILES["file"]})
        return render(request, self.template_name, {'form': form})


class ExemptionFailView(FormView):
    template_name = 'exemption_fail.html'

    def get(self, request):
        return render(request, 'exemption_fail.html')


class RegistrarView(View):
    template_name = 'registrar.html'

    def get(self, request):
        form = RegistrarForm()
        return render(request,
                      self.template_name,
                      {'form': form, 'organisations': organisations_list()})

    def post(self, request):
        form = RegistrarForm(None, request.POST)
        if form.is_valid():
            request.session['organisations_choice'] = {
                'organisation': form.cleaned_data['organisations_choice']
                }
            return redirect('exemption_upload')
        return render(request, self.template_name, {'form': form})
