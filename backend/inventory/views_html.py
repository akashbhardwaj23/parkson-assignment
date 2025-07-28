from .models import Product, StockTransaction
from django.shortcuts import render, redirect
from django import forms


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'description', 'min_stock', 'max_stock']

def add_product_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard') 
    else:
        form = ProductForm()
    return render(request, 'inventory/add_product.html', {'form': form})

def dashboard_view(request):
    return render(request, 'inventory/dashboard.html')

def product_list_view(request):
    products = Product.objects.all().order_by("name")
    return render(request, "inventory/product_list.html", {"products": products})

def transaction_list_view(request):
    transactions = StockTransaction.objects.all().prefetch_related("details__product")
    return render(request, "inventory/transaction_list.html", {"transactions": transactions})

def inventory_view(request):
    products = Product.objects.all().order_by("name")
    inventory = [
        {
            "name": product.name,
            "sku": product.sku,
            "current_stock": product.current_stock
        }
        for product in products
    ]
    return render(request, "inventory/inventory_view.html", {"inventory": inventory})
