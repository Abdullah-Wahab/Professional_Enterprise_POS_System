from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django_pos.wsgi import *
from django_pos import settings
from customers.models import Customer
from products.models import Product
from .models import Sale, SaleDetail, Transaction
import json
from django.templatetags.static import static
from django.template.loader import get_template
from django.http import HttpResponse
import os
from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Sum

# os.add_dll_directory(r"C:\msys64\mingw64\bin") # before moving msys64 folder to D:/
os.add_dll_directory(r"D:\django_point_of_sale\msys64\mingw64\bin")
from weasyprint import HTML, CSS


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required(login_url="/accounts/login/")
def SalesListView(request):
    context = {
        "active_icon": "sales",
        "sales": Sale.objects.all()
    }
    return render(request, "sales/sales.html", context=context)


@login_required(login_url="/accounts/login/")
def SalesAddView(request):
    context = {
        "active_icon": "new_add",
        "customers": [c.to_select2() for c in Customer.objects.all()]
    }

    if request.method == 'POST':
        if is_ajax(request=request):
            # Save the POST arguements
            data = json.load(request)

            sale_attributes = {
                "customer": Customer.objects.get(id=int(data['customer'])),
                "sub_total": float(data["sub_total"]),
                "grand_total": float(data["grand_total"]),
                "amount_payed": float(data["amount_payed"]),
                "amount_change": abs(float(data["amount_change"])),
            }
            try:
                # Create the sale
                new_sale = Sale.objects.create(**sale_attributes)

                # Create the sale details
                products = data["products"]

                for product in products:
                    detail_attributes = {
                        "sale": Sale.objects.get(id=new_sale.id),
                        "product": Product.objects.get(id=int(product["id"])),
                        "price": product["price"],
                        "quantity": product["quantity"],
                        "unit": product["unit"],
                        "total_detail": product["total_product"]
                    }
                    sale_detail_new = SaleDetail.objects.create(
                        **detail_attributes)
                    sale_detail_new.save()

                print("Sale saved")

                # Add transaction for the sale
                Transaction.objects.create(
                    customer=new_sale.customer,
                    sale=new_sale,
                    transaction_type="Sale",
                    invoice_bill_no=new_sale.invoice_number,
                    total_amount=new_sale.sub_total,
                    received_paid_amount=new_sale.amount_payed,
                    receivable_balance=new_sale.amount_change,
                )

                print("Sale and Transaction saved")

                response_data = {
                    "status": "success",
                    "message": "Sale created successfully",
                    "sale_id": new_sale.id
                }
                return JsonResponse(response_data)

            except Exception as e:
                messages.success(
                    request, 'There was an error during the creation!', extra_tags="danger")

        return redirect('sales:sales_add')

    return render(request, "sales/sales_add.html", context=context)


@login_required(login_url="/accounts/login/")
def SalesDetailsView(request, sale_id):
    """
    Args:
        sale_id: ID of the sale to view
    """
    try:
        # Get the sale
        sale = Sale.objects.get(id=sale_id)

        # Get the sale details
        details = SaleDetail.objects.filter(sale=sale)

        context = {
            "active_icon": "sales",
            "sale": sale,
            "details": details,
        }
        return render(request, "sales/sales_details.html", context=context)
    except Exception as e:
        messages.success(
            request, 'There was an error getting the sale!', extra_tags="danger")
        print(e)
        return redirect('sales:sales_list')


@login_required(login_url="/accounts/login/")
def ReceiptPDFView(request, sale_id):
    from django.http import FileResponse

    """
    Args:
        sale_id: ID of the sale to view the receipt
    """
    # Get the sale
    sale = Sale.objects.get(id=sale_id)

    # Get the sale details
    details = SaleDetail.objects.filter(sale=sale)

    template = get_template("sales/sales_receipt_pdf.html")
    context = {
        "sale": sale,
        "details": details,
        "logo_url": request.build_absolute_uri(static('logo4r1.jpg')),
    }
    html_template = template.render(context)

    # CSS Bootstrap
    css_url = os.path.join(
        settings.BASE_DIR, 'static/css/receipt_pdf/bootstrap.min.css')
    # css_url = os.path.join(
    #     settings.BASE_DIR, 'static/css/invoice.css')

    # Create the pdf
    pdf = HTML(string=html_template).write_pdf(stylesheets=[CSS(css_url)])

    # # Set a custom filename for the downloaded PDF
    # filename = f"{sale.customer.get_full_name()} - Receipt.pdf"
    #
    # # Use FileResponse to return the PDF with the custom filename
    # response = HttpResponse(pdf, content_type="application/pdf")
    # response['Content-Disposition'] = f'attachment; filename="{filename}"'
    #
    # return response

    return HttpResponse(pdf, content_type="application/pdf")


# Showing all the transactions happened
@login_required(login_url="/accounts/login/")
def TransactionsView(request):
    transactions = Transaction.objects.select_related('customer').order_by('-created_at')
    context = {
        "transactions": transactions,
    }
    return render(request, "sales/transactions.html", context=context)


@login_required(login_url="/accounts/login/")
def CustomerTransactionsView(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    transactions = Transaction.objects.filter(customer=customer)

    context = {
        'customer': customer,
        'transactions': transactions,
    }
    return render(request, 'sales/customer_transactions.html', context)


@login_required(login_url="/accounts/login/")
def add_transaction(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':
        transaction_type = "Party To Party [Received]"
        received_paid_amount = Decimal(request.POST.get('received_paid_amount'))

        new_balance = customer.balance - received_paid_amount
        customer.balance = new_balance
        customer.save()

        # Create the transaction object and save it to the database
        Transaction.objects.create(
            customer=customer,
            transaction_type=transaction_type,
            received_paid_amount=received_paid_amount,
            receivable_balance=customer.balance,
        )

        # Redirect to the customer transactions page
        return redirect('sales:customer_transactions', customer_id=customer.id)

    context = {
        'customer': customer,
    }
    return render(request, 'sales/add_transaction.html', context)
