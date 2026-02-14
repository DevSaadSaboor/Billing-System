from django.urls import path
from .views import CustomerListCreatedView,CustomerDetailView

urlpatterns = [
    path("", CustomerListCreatedView.as_view(), name="customer-list-create"),
    path("<int:pk>/", CustomerDetailView.as_view(), name="customer-detail"),
]