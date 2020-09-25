from django.contrib import admin

from .models import Answers, Roles, Permissions, Messages, Countries, Questions, Surveys, RolesPermissions

admin.site.register(Answers)
admin.site.register(Roles)
admin.site.register(Permissions)
admin.site.register(Messages)
admin.site.register(Countries)
admin.site.register(Questions)
admin.site.register(Surveys)
admin.site.register(RolesPermissions)
