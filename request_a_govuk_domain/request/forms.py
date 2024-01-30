from django import forms
from django.forms import CharField, DateField, BooleanField, DateTimeInput

from .base_from import FormWithLabelStyle


class NameForm(FormWithLabelStyle):
    your_name = CharField(
        label="Your name",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "govuk-input"}
        )
    )
    date = DateField(
        label="Your Birthday",
        widget=DateTimeInput(
            attrs={"class": "govuk-datetime"}
        )
    )

    yes_no = BooleanField(label="Are you good",
                          widget=forms.CheckboxInput(
                              attrs={"class": "govuk-checkbox"}
                          ))
