from django.contrib import admin
from .models import Income, Source

class IncomeAdmin(admin.ModelAdmin):
    list_display = ('amount', 'description', 'date', 'owner', 'source')
    search_fields = ('description', 'date', 'source')
    list_per_page = 5


admin.site.register(Income, IncomeAdmin)
admin.site.register(Source)