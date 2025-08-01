from django.urls import path
from .views_html import dashboard_view
from .views_html import add_product_view
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
    path('', dashboard_view, name='dashboard'),
    path('add-product/', add_product_view, name='add-product'),
    path('inventory/', CurrentInventoryAPIView.as_view(), name='current-inventory'),
]

# urlpatterns += [
#     path('html/products/', views_html.product_list_view, name='html-product-list'),
#     path('html/transactions/', views_html.transaction_list_view, name='html-transaction-list'),
#     path('html/inventory/', views_html.inventory_view, name='html-inventory'),
# ]
