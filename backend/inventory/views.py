from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product, StockTransaction, StockDetail
from .serializers import ProductSerializer, TransactionSerializer, InventorySerializer

class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by('name')
    serializer_class = ProductSerializer

class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class TransactionListCreateAPIView(generics.ListCreateAPIView):
    queryset = StockTransaction.objects.all().prefetch_related('details__product')
    serializer_class = TransactionSerializer

class TransactionRetrieveAPIView(generics.RetrieveAPIView):
    queryset = StockTransaction.objects.all().prefetch_related('details__product')
    serializer_class = TransactionSerializer

class CurrentInventoryAPIView(generics.ListAPIView):
    queryset = Product.objects.all().order_by('name')
    serializer_class = InventorySerializer
