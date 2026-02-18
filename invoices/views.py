from rest_framework import generics
from .models import Invoice
from .serializers import InvoiceSerializer
from rest_framework.permissions import IsAuthenticated


class InvoiceListCreateView(generics.ListCreateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query_set =  Invoice.objects.filter(user = self.request.user)
    
        for invoice in query_set:
            invoice.update_overdue_status()
        
        return query_set


class InvoiceDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        query_set=  Invoice.objects.filter(user = self.request.user)
        for invoice in query_set:
            invoice.update_overdue_status()
    
