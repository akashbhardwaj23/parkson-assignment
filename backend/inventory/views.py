from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, F

from .models import Product, StockTransaction, StockDetail
from .serializers import ProductSerializer, StockTransactionSerializer, InventorySerializer

class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by('name')
    serializer_class = ProductSerializer
   
class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class StockTransactionListCreateAPIView(generics.ListCreateAPIView):
    queryset = StockTransaction.objects.all().prefetch_related('details__product')
    serializer_class = StockTransactionSerializer

class StockTransactionRetrieveAPIView(generics.RetrieveAPIView):
    queryset = StockTransaction.objects.all().prefetch_related('details__product')
    serializer_class = StockTransactionSerializer

class CurrentInventoryAPIView(APIView):
    def get(self, request, *args, **kwargs):
        inventory_data = []
        products = Product.objects.all().order_by('name')

        for product in products:
            in_quantity = StockDetail.objects.filter(
                product=product,
                transaction__transaction_type='IN'
            ).aggregate(total=Sum('quantity'))['total'] or 0

            out_quantity = StockDetail.objects.filter(
                product=product,
                transaction__transaction_type='OUT'
            ).aggregate(total=Sum('quantity'))['total'] or 0

            current_stock = in_quantity - out_quantity

            inventory_data.append({
                'product_id': product.id,
                'product_name': product.name,
                'product_sku': product.sku,
                'current_stock': current_stock
            })

        serializer = InventorySerializer(inventory_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)