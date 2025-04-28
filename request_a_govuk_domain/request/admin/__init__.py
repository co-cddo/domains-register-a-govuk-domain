from django.contrib import admin
from django.contrib.auth.models import Group, User

from request_a_govuk_domain.request.models import (
    Application,
    Registrant,
    RegistrantPerson,
    Registrar,
    RegistrarPerson,
    RegistryPublishedPerson,
    Review,
)

from .model_admins import (
    ApplicationAdmin,
    DomainRegistrationGroupAdmin,
    DomainRegistrationUserAdmin,
    RegistrantAdmin,
    RegistrantPersonAdmin,
    RegistrarAdmin,
    RegistrarPersonAdmin,
    RegistryPublishedPersonAdmin,
    ReviewAdmin,
)

admin.site.unregister(User)
admin.site.register(User, DomainRegistrationUserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, DomainRegistrationGroupAdmin)

admin.site.register(Application, ApplicationAdmin)

admin.site.register(Review, ReviewAdmin)

admin.site.register(RegistrantPerson, RegistrantPersonAdmin)

admin.site.register(RegistrarPerson, RegistrarPersonAdmin)

admin.site.register(RegistryPublishedPerson, RegistryPublishedPersonAdmin)

admin.site.register(Registrant, RegistrantAdmin)

admin.site.register(Registrar, RegistrarAdmin)
