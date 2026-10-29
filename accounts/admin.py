from django.contrib import admin
from django.contrib.auth.models import Group, User


admin.site.unregister(Group)
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
