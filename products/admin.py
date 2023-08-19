from django.contrib import admin
from .models import Category, Product
from import_export.admin import ImportExportModelAdmin


# admin.site.register(Category)
# admin.site.register(Product)

@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name', 'description', 'status')


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name', 'status', 'category', 'purchase_price', 'sale_price')
