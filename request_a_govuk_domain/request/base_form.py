from typing import Dict, Any

from django import forms
from django.forms import BoundField


class BoundFieldWithLabelClass(BoundField):
    """
    Custom bound field that provides the label styling
    """

    def __init__(self, label_style: str, *args):
        self.label_style = label_style
        super().__init__(*args)

    def label_tag(self, contents: str = "", attrs: Dict[str, Any] = {}, label_suffix: str = "", tag: str = ""):
        """
        Override the label generation so we can add the style
        :param contents:
        :param attrs:
        :param label_suffix:
        :param tag:
        :return:
        """
        if attrs is None:
            attrs = {}
        if self.label_style:
            attrs["class"] = self.label_style
        return super().label_tag(contents, attrs, label_suffix, tag)


class FieldProxy(object):
    """
    Proxy that wraps any Field object and provide
    an instance of BoundFieldWithLabelClass on the
    return value of get_bound_field
    """

    def __init__(self, proxied: forms.Field, label_style: str):
        """
        Wrapper for a form.Field, tht will add label styles to the bound field.
        :param proxied:
        :param label_style:
        """
        self.proxied = proxied
        self.label_style = label_style

    def __getattr__(self, item: str):
        """
        Proxy any property access to the proxied object
        :param item:
        :return:
        """
        return getattr(self.proxied, item)

    def get_bound_field(self, form: forms.Form, field_name: str):
        """
        Overridden method to get the bound field, that supports the label styling
        :param form:
        :param field_name:
        :return:
        """
        # Intercept the bound field and return the proxy that supports label styles
        return BoundFieldWithLabelClass(self.label_style, form, self.proxied, field_name, )


class FormWithLabelStyle(forms.Form):
    """
    Custom class that updated the fields so that we can apply style
    attributes to the labels as it is not supported by default.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        proxied_fields = dict()
        for field_name in self.fields:
            proxied_fields[field_name] = FieldProxy(self.fields[field_name], "govuk-label")
        # Replace the fields with the proxies, that provide the label styling.
        self.fields = proxied_fields
