from django.contrib import admin

from .models import Sale, SaleDetail, Transaction

admin.site.register(Sale)
admin.site.register(SaleDetail)


class TransactionAdmin(admin.ModelAdmin):
    def invoice_no(self, obj):
        return obj.invoice_bill_no or '-'  # Handle None value here

    def total_am(self, obj):
        return obj.total_amount or '-'

    invoice_no.short_description = 'Invoice Bill No.'
    total_am.short_description = 'Total Amount'


admin.site.register(Transaction, TransactionAdmin)
