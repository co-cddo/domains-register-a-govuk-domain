from django.shortcuts import render, redirect
from django.views import View
from .forms import NameForm, EmailForm
from .models import RegistrationData

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
