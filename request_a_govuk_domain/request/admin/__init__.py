from django.contrib import admin
from django.contrib.auth.models import Group, User
from request_a_govuk_domain.request.models import Application, Review
from .model_admins import (
    ApplicationAdmin,
    ReviewAdmin,
    DomainRegistrationUserAdmin,
    DomainRegistrationGroupAdmin,
)


admin.site.unregister(User)
admin.site.register(User, DomainRegistrationUserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, DomainRegistrationGroupAdmin)

admin.site.register(Application, ApplicationAdmin)

admin.site.register(Review, ReviewAdmin)
