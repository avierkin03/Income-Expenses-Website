from django.contrib import admin
from .models import Expense, Category


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('amount', 'description', 'date', 'owner', 'category')
    search_fields = ('description', 'date', 'category')
    list_per_page = 5


admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Category)