from rest_framework import generics
from .models import Invoice
from .serializers import InvoiceSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from datetime import datetime
class InvoiceListCreateView(generics.ListCreateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query_set =  Invoice.objects.filter(user = self.request.user)
    
        for invoice in query_set:
            invoice.update_overdue_status()

        status = self.request.query_params.get("status")
        customer_id = self.request.query_params.get("customer")

        if status:
            query_set = query_set.filter(status=status)

        if customer_id:
            query_set = query_set.filter(customer_id=customer_id)

        return query_set


class InvoiceDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        query_set=  Invoice.objects.filter(user = self.request.user)
        for invoice in query_set:
            invoice.update_overdue_status()

class InvoiceSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        query_set = Invoice.objects.filter(user = self.request.user)
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        if start_date:
            query_set = query_set.filter(issue_date__date__gte = start_date)
        if end_date:
            query_set = query_set.filter(issue_date__date__lte = end_date)
        total_invoices = query_set.count()
        paid_count = query_set.filter(status = "paid").count()
        overdue_count = query_set.filter(status = "overdue").count()
        unpaid_count = query_set.exclude(status = "paid").count()
        total_revenue = (query_set.filter(status="paid").aggregate(Sum("grand_total"))["grand_total__sum"]) or 0
        outstanding_amount = (query_set.exclude(status = "paid" ).aggregate(Sum("grand_total"))["grand_total__sum"]) or 0

        return Response({
            "total_invoices": total_invoices,
            "paid_count" : paid_count,
            "overdue_count" : overdue_count,
            "unpaid_count" : unpaid_count,
            "total_revenue": total_revenue,
            "outstanding_amount": outstanding_amount
        })
        

    
