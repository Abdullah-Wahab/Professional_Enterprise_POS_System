from django.contrib import admin
from .models import Customer
from import_export.admin import ImportExportModelAdmin

# admin.site.register(Customer)


@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'phone')
