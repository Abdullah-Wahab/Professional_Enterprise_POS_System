from django.urls import path

from . import views

app_name = "sales"
urlpatterns = [
    # List sales
    path('', views.SalesListView, name='sales_list'),
    # Add sale
    path('add', views.SalesAddView, name='sales_add'),
    # Details sale
    path('details/<str:sale_id>',
         views.SalesDetailsView, name='sales_details'),
    # Sale receipt PDF
    path("pdf/<str:sale_id>",
         views.ReceiptPDFView, name="sales_receipt_pdf"),
    # To show all the transactions
    path('transactions/', views.TransactionsView, name='transactions'),
    # # To generate reports
    # path('reports/', views.ReportsView, name='reports'),
    # URL pattern to view customer transactions
    path('customer/<int:customer_id>/transactions/', views.CustomerTransactionsView, name='customer_transactions'),
    # To Add transaction manually
    path('customer/<int:customer_id>/transactions/add/', views.add_transaction, name='add_cus_transaction'),
]
