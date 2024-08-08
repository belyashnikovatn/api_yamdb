from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User

UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('bio', 'role')}),
)
UserAdmin.list_display += ('role',)
UserAdmin.list_editable += ('role',)

admin.site.register(User, UserAdmin)
