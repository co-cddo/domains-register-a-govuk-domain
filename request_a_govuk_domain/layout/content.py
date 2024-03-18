from crispy_forms_gds.layout import HTML
from django.utils.safestring import mark_safe


class DomainsHTML(HTML):
    """
    This subclasses the HTML class from crispy-forms-gds to override the warning method to match the GOV.UK Design
    System.
    """

    @classmethod
    def warning(cls, content):
        """
        Note: This overrides method that implements GOV.UK Design System Warning text.
        crispy-forms-gds does have a warning method, but it is not up-to-date with the GOV.UK Design System - it shows
        the word "Warning" in the text, which is not part of the GOV.UK Design System.

        This overridden method has just one change, it changes the span class from "govuk-warning-text__assistive" to
        "govuk-visually-hidden" to match the GOV.UK Design System.

        Original docstring from crispy-forms-gds is below:

        .. _Warning text: https://design-system.service.gov.uk/components/warning-text/

        Generate the layout for an `Warning text`_ component.

        Args:
            content: the message that is displayed as a warning.

        """
        snippet = """
                <div class="govuk-warning-text">
                  <span class="govuk-warning-text__icon" aria-hidden="true">!</span>
                  <strong class="govuk-warning-text__text">
                    <span class="govuk-visually-hidden">Warning</span>
                    %s
                  </strong>
                </div>
            """ % (
            mark_safe(content),
        )
        return HTML(snippet)
