from django.contrib import admin
from .models import UserPreference

class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'currency')
    search_fields = ('user', 'currency')
    list_per_page = 5


admin.site.register(UserPreference, UserPreferenceAdmin)