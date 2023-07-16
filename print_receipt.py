import os
from django.template.loader import get_template
from xhtml2pdf import pisa


def print_receipt():
    template = get_template("sales/receipt_pdf.html")
    context = {"name": "Jorge"}
    html_template = template.render(context)

    # Create the PDF file path
    pdf_path = os.path.join(settings.BASE_DIR, "receipt.pdf")

    # Generate the PDF
    with open(pdf_path, "w+b") as pdf_file:
        pisa.CreatePDF(html_template, dest=pdf_file)

    return pdf_path


print_receipt()
