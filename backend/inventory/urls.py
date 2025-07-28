from django.urls import path
from .views import (
    ProductListCreateAPIView, ProductRetrieveUpdateDestroyAPIView,
    TransactionListCreateAPIView, TransactionRetrieveAPIView,
    CurrentInventoryAPIView
)

urlpatterns = [
    path('products/', ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyAPIView.as_view(), name='product-detail'),

    path('transactions/', TransactionListCreateAPIView.as_view(), name='transaction-list-create'),
    path('transactions/<int:pk>/', TransactionRetrieveAPIView.as_view(), name='transaction-detail'),

    path('inventory/', CurrentInventoryAPIView.as_view(), name='current-inventory'),
]