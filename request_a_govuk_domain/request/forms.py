from django import forms

from .base_form import FormWithLabelStyle


class NameForm(FormWithLabelStyle):
    """
    Example form, please modify/ remove this when the actual requirements are clear
    This is only created to test the ui with gov uk design is working
    """
    registrant_full_name = forms.CharField(label='Registrant Full Name', max_length=100,
                                           widget=forms.TextInput(attrs={"class": "govuk-input"}))


class EmailForm(FormWithLabelStyle):
    """
    Another example form
    """
    registrant_email_address = forms.EmailField(label='Registrant Email Address', max_length=100,
                                                widget=forms.TextInput(attrs={"class": "govuk-input"}))
