from rest_framework import generics
from .models import Invoice
from .serializers import InvoiceSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import InvoiceFilter
from django.utils import timezone

class InvoiceListCreateView(generics.ListCreateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filtering_class = InvoiceFilter
    ordering_fields = ["issue_date", "due_date","grand_total", "created_at"]
    ordering = ["-created_at"]
    
    def get_queryset(self):
        # query_set =  Invoice.objects.filter(user = self.request.user)

        Invoice.objects.filter(
            user = self.request.user,
            status__in = ["draft", "sent"],
            due_date__isnull=False,
            due_date__lt = timezone.now(),
        ).update(status = "overdue")

        return Invoice.objects.filter(user = self.request.user)
    
        # for invoice in query_set:
        #     invoice.update_overdue_status()
        # status = self.request.query_params.get("status")
        # customer_id = self.request.query_params.get("customer")
        # if status:
        #     query_set = query_set.filter(status=status)
        # if customer_id:
        #     query_set = query_set.filter(customer_id=customer_id)
        # return query_set

    

class InvoiceDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):

        Invoice.objects.filter(
            user = self.request.user,
            status__in = ["draft","sent"],
            due_date__isnull=False,
            due_date__lt = timezone.now()
        ).update(status = "overdue")

        # query_set=  Invoice.objects.filter(user = self.request.user)
        # for invoice in query_set:
        #     invoice.update_overdue_status()
        # return query_set

class InvoiceSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        query_set = Invoice.objects.filter(user = self.request.user)
        filterset = InvoiceFilter(request.GET, queryset=query_set)
        query_set = filterset.qs


        # start_date = request.query_params.get("start_date")
        # end_date = request.query_params.get("end_date")
        # if start_date:
        #     query_set = query_set.filter(issue_date__date__gte = start_date)
        # if end_date:
        #     query_set = query_set.filter(issue_date__date__lte = end_date)

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
        
class SendInvoiceview(APIView):
    def post(self,request,pk):
        invoice = get_object_or_404(Invoice,pk=pk, user = request.user)

        if invoice.status != "draft":
            return Response({"detail": "Only draft invoices can be sent."}, status=status.HTTP_400_BAD_REQUEST)
        if not invoice.line_items.exists():
            return Response({"detail": "Only draft invoices can be sent."}, status=status.HTTP_400_BAD_REQUEST)
        
        invoice.status ="sent"
        invoice.save(update_fields=["status"])

        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)


        
    
