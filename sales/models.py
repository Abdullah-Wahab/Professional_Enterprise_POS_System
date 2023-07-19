from django.db import models
import django.utils.timezone
from customers.models import Customer
from products.models import Product
import random


class Sale(models.Model):
    date_added = models.DateTimeField(default=django.utils.timezone.now)
    customer = models.ForeignKey(
        Customer, models.DO_NOTHING, db_column='customer')
    sub_total = models.FloatField(default=0)
    grand_total = models.FloatField(default=0)
    amount_payed = models.FloatField(default=0)
    amount_change = models.FloatField(default=0)
    invoice_number = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'Sales'

    def __str__(self) -> str:
        return "Sale ID: " + str(self.id) + " | Grand Total: " + str(self.grand_total) + " | Datetime: " + str(self.date_added)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            used_numbers = set(Sale.objects.values_list('invoice_number', flat=True))
            while True:
                invoice_number = random.randint(10000, 99999)
                if invoice_number not in used_numbers:
                    self.invoice_number = invoice_number
                    break
        super().save(*args, **kwargs)

        # Update the customer's balance
        customer = Customer.objects.get(id=self.customer.id)
        updated_balance = self.grand_total - self.amount_payed
        o_balance = customer.balance
        customer.old_balance = o_balance
        customer.balance = updated_balance
        customer.save()

    def sum_items(self):
        details = SaleDetail.objects.filter(sale=self.id)
        return sum([d.quantity for d in details])

    def previous_balance(self):
        getting_customer = Customer.objects.filter(id=self.customer.id)
        balance = getting_customer.balance
        return balance


class SaleDetail(models.Model):
    sale = models.ForeignKey(
        Sale, models.DO_NOTHING, db_column='sale')
    product = models.ForeignKey(
        Product, models.DO_NOTHING, db_column='product')
    price = models.FloatField()
    quantity = models.IntegerField()
    total_detail = models.FloatField()

    class Meta:
        db_table = 'SaleDetails'

    def __str__(self) -> str:
        return "Detail ID: " + str(self.id) + " Sale ID: " + str(self.sale.id) + " Quantity: " + str(self.quantity)
