import django_filters
from django_filters import rest_framework as filters
from .models import Invoice


class InvoiceFilter(filters.FilterSet):
    start_date = filters.DateFilter(
        field_name="issue_date",
        lookup_expr="date__gte"
    )

    end_date = filters.DateFilter(
        field_name="issue_date",
        lookup_expr="date__lte"
    )

    class Meta:
        model = Invoice
        fields = ["status", "customer"]