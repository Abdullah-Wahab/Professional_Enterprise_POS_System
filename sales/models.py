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
        return "Sale ID: " + str(self.id) + " | Grand Total: " + str(self.grand_total) + " | Datetime: " + str(
            self.date_added)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Get the maximum invoice number from the existing sales
            max_invoice_number = Sale.objects.aggregate(models.Max('invoice_number'))['invoice_number__max']

            # If no sales with invoice numbers exist, start with 1, otherwise increment by 1
            self.invoice_number = 1 if max_invoice_number is None else max_invoice_number + 1
        super().save(*args, **kwargs)

        # Update the customer's balance
        customer = Customer.objects.get(id=self.customer.id)
        updated_balance = abs(self.grand_total - self.amount_payed)
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
    UNIT_CHOICE = (("Pcs", "Pcs"), ("Doz", "Doz"))
    sale = models.ForeignKey(
        Sale, models.DO_NOTHING, db_column='sale')
    product = models.ForeignKey(
        Product, models.DO_NOTHING, db_column='product')
    price = models.FloatField()
    quantity = models.IntegerField()
    unit = models.CharField(null=True, blank=True, max_length=20, choices=UNIT_CHOICE)
    total_detail = models.FloatField()

    class Meta:
        db_table = 'SaleDetails'

    def __str__(self) -> str:
        return "Detail ID: " + str(self.id) + " Sale ID: " + str(self.sale.id) + " Quantity: " + str(self.quantity)


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (  # new
        ("Beginning Balance", "Beginning Balance"),
        ("Sale", "Sale"),
        ("Party To Party [Received]", "Party To Party [Received]"),
        ("Ending Balance", "Ending Balance"),
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="customer_transactions")
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, null=True)
    transaction_type = models.CharField(max_length=40, choices=TRANSACTION_TYPE_CHOICES)
    invoice_bill_no = models.CharField(max_length=20, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Sub Total
    received_paid_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Paid Amount
    receivable_balance = models.DecimalField(max_digits=10, decimal_places=2)  # Remaining Balance - Grand Total
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.customer) + " " + self.transaction_type + " " + f"{self.invoice_bill_no or '-'}"

    class Meta:
        db_table = 'Transactions'
