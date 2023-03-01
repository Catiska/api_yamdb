from django.contrib import admin

from .models import User


class Admin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email', 'role')
    search_fields = ('username', 'email',)
    ordering = ('email',)


admin.site.register(Admin, User)
