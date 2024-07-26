from django.contrib import admin
from django.contrib.auth.models import Group, User
from request_a_govuk_domain.request.models import (
    Application,
    Review,
    RegistrantPerson,
    RegistrarPerson,
    RegistryPublishedPerson,
    Registrant,
    Registrar,
    TimeFlag,
)
from .model_admins import (
    ApplicationAdmin,
    ReviewAdmin,
    DomainRegistrationUserAdmin,
    DomainRegistrationGroupAdmin,
    RegistrantPersonAdmin,
    RegistrarPersonAdmin,
    RegistryPublishedPersonAdmin,
    RegistrantAdmin,
    RegistrarAdmin,
    TimeFlagAdmin,
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

admin.site.register(TimeFlag, TimeFlagAdmin)
