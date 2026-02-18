from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Customer
from .serializers import CustomerSerializer

class CustomerListCreatedView(generics.ListCreateAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Customer.objects.filter(user = self.request.user)
    def perform_create(self, serializer):
        serializer.save(user = self.request.user)
       

class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomerSerializer
    permission_classes  = [IsAuthenticated]


    def get_queryset(self):
        return Customer.objects.filter(user = self.request.user)
    
         
 
 

  