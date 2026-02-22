from django.urls import path
from .views import InvoiceListCreateView, InvoiceDetailView,InvoiceSummaryView,SendInvoiceview

urlpatterns = [
    path("", InvoiceListCreateView.as_view(), name="invoice-list-create"),
    path("<int:pk>/", InvoiceDetailView.as_view(), name="invoice-detail"),
    path("<int:pk>/send/", SendInvoiceview.as_view(), name="invoice-send"),
    path("summary/",InvoiceSummaryView.as_view(), name =  "invoice-summary")
]
