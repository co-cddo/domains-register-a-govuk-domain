from functools import partial
from django.db.models import FileField
from django.urls import path, reverse
from django.utils.html import format_html


class ReviewerReadOnlyFieldsMixin:
    """
    This will convert any file fields to a link pointing to a view named admin:download_file. Which enables the user
    to download the file for viewing. This view has to be implemented by the model admin that uses this mixin.

    The ModelAdmin will need to implement a method prefixed with download_<file field attribute>
    for each file field available in the model and call the generate_download_link function in it.
    Following code shows how it is done for a model which contains a file field called 'gds_exemption_evidence'

        def download_gds_exemption_evidence(self, obj):
            return self.generate_download_link(obj.gds_exemption_evidence.name)

        # Set the short description attribute on the method so it will be used as the label in the form
        download_gds_exemption_evidence.short_description = "GDS exemption evidence"

    """

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        else:
            return self._get_field_names(not request.user.is_superuser) + [
                "time_decided"
            ]

    def get_fields(self, request, obj=None):
        return self._get_field_names(not request.user.is_superuser)

    def get_urls(self):
        urls = super().get_urls()
        all_fields = []
        all_fields.extend(self.model._meta.fields)
        for inline in self.inlines:
            all_fields.extend(inline.model._meta.fields)
        extra_urls = [
            path(
                f"<int:object_id>/download_{field.attname}/",
                self.admin_site.admin_view(
                    partial(self.download_file, field_name=field.attname)
                ),
                name="download_" + field.attname,
            )
            for field in all_fields
            if isinstance(field, FileField)
        ]
        # NOTE! Our custom urls have to go before the default urls, because they
        # default ones match anything.
        return extra_urls + urls

    def generate_download_link(self, obj, field):
        field_name = field.replace("download_", "")
        if getattr(obj, field_name):
            link = reverse(
                f"admin:{field}",
                args=[obj.id],
            )
            return format_html(
                f'<a href="{{}}" download="{getattr(obj, field_name).name}">{{}}</a>',
                link,
                "Download File",
            )
        else:
            return "--"

    def download_file(self, request, field_name, object_id):
        """
        Override this method in the child class to provide the implementation. Note that for inline admin classes
        this must be overriden in the 'parent' class (the class which inherits from admin.ModelAdmin) and not
        the inline class (inherits from StackedInline or TabularInline). Any method in the inline classes is
        ignored

        :param request: Http request
        :param field_name: Name of the file field
        :param object_id: object id to retrieve
        :return:
        """
        raise NotImplementedError(
            "Override this method in your model admin to get the file"
        )

    def _get_field_names(self, add_download_fields=False):
        """
        Get the list of field names to show on the admin screen depending on the flag provided.
        This will add extra attribute starting with "download_" replacing any FileFields
        that exist in the model if add_add_download_fields set to true. Will return unmodified
        list of field names (excluding the id) if the flag is set to false.
        :param add_download_fields: set to true if the FileFields should be replaced with download links
        :return: list of field names applicable for the current view.
        """
        return [
            field.name
            for field in self.model._meta.fields
            if not isinstance(field, FileField) and field.name != "id"
        ] + (
            [
                "download_" + field.attname
                for field in self.model._meta.fields
                if isinstance(field, FileField)
            ]
            if add_download_fields
            else [
                field.name
                for field in self.model._meta.fields
                if isinstance(field, FileField)
            ]
        )
