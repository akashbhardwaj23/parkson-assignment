import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackerapp.settings')
django.setup()

from inventory.models import Product, StockTransaction, StockDetail
from django.db import transaction

print("--- Populating Mock Data ---")

with transaction.atomic():
    print("Clearing existing Product, StockTransaction, and StockDetail data...")
    StockDetail.objects.all().delete()
    StockTransaction.objects.all().delete()
    Product.objects.all().delete()
    print("Data cleared.")

    print("\nCreating Products...")
    products_data = [
        {"name": "Laptop Pro 15-inch", "sku": "LAP-PRO-15-A", "description": "High-performance laptop for professionals", "min_stock": 10, "max_stock": 100},
        {"name": "Wireless Mouse", "sku": "ACC-MOUSE-WL", "description": "Ergonomic wireless mouse with long battery life", "min_stock": 20, "max_stock": 200},
        {"name": "Mechanical Keyboard", "sku": "ACC-KEY-MECH", "description": "RGB mechanical keyboard with tactile switches", "min_stock": 5, "max_stock": 50},
        {"name": "External SSD 1TB", "sku": "STO-SSD-1TB", "description": "Portable 1TB SSD, USB-C", "min_stock": 15, "max_stock": 150},
        {"name": "Monitor 27-inch 4K", "sku": "DIS-MON-27-4K", "description": "UHD display for crisp visuals", "min_stock": 8, "max_stock": 80},
    ]

    created_products = {}
    for prod_data in products_data:
        product = Product.objects.create(**prod_data)
        created_products[product.sku] = product
        print(f"Created Product: {product.name} (ID: {product.id}, Min: {product.min_stock}, Max: {product.max_stock})")

    if not created_products:
        print("No products created. Exiting.")
        exit()

    print("\nCreating Stock Transactions...")

    def create_transaction_with_details(transaction_type, reference, notes, details_list, custom_date=None):
        transaction_instance = StockTransaction.objects.create(
            type=transaction_type,
            reference=reference,
            notes=notes,
            date=custom_date if custom_date else datetime.now()
        )
        print(f"Created {transaction_type} Transaction (ID: {transaction_instance.id})")

        for detail_data in details_list:
            product_id = detail_data['productId']
            quantity = detail_data['quantity']
            unit_price = detail_data.get('unit_price', 0.00)

            product_obj = Product.objects.get(id=product_id)


            product_to_update = Product.objects.select_for_update().get(id=product_obj.id)

            if transaction_type == 'IN':
                product_to_update.current_stock += quantity
            elif transaction_type == 'OUT':
                if product_to_update.current_stock < quantity:
                    raise Exception(f"Insufficient stock for '{product_to_update.name}' (Available: {product_to_update.current_stock}, Requested: {quantity})")
                product_to_update.current_stock -= quantity

            product_to_update.save()

            StockDetail.objects.create(
                transaction=transaction_instance,
                product=product_to_update,
                quantity=quantity,
                unit_price=unit_price
            )
        print(f"Added details for {transaction_type} Transaction {transaction_instance.id}.")
        return transaction_instance

    try:
        create_transaction_with_details(
            'IN',
            'PO2023001',
            'Initial stock arrival from vendor A',
            [
                {"productId": created_products['LAP-PRO-15-A'].id, "quantity": 50, "unit_price": 1200.00}, # Change: use .id
                {"productId": created_products['ACC-MOUSE-WL'].id, "quantity": 100, "unit_price": 25.00}, # Change: use .id
                {"productId": created_products['ACC-KEY-MECH'].id, "quantity": 30, "unit_price": 75.00}, # Change: use .id
            ]
        )
    except Exception as e:
        print(f"Error creating IN Transaction 1: {e}")

    try:
        create_transaction_with_details(
            'OUT',
            'SO2023005',
            'Sale to corporate client B',
            [
                    {"productId": created_products['LAP-PRO-15-A'].id, "quantity": 5, "unit_price": 1300.00},
                    {"productId": created_products['ACC-MOUSE-WL'].id, "quantity": 10, "unit_price": 30.00},
            ],
            custom_date=datetime.now() - timedelta(days=2)
        )
    except Exception as e:
        print(f"Error creating OUT Transaction 1: {e}")

    try:
        create_transaction_with_details(
            'IN',
            'PO2023002',
            'New SSD stock from vendor C',
            [
                {"productId": created_products['STO-SSD-1TB'].id, "quantity": 75, "unit_price": 80.00},
            ]
        )
    except Exception as e:
        print(f"Error creating IN Transaction 2: {e}")

    try:
        create_transaction_with_details(
            'IN',
            'PO2023003',
            'Monitors arrived',
            [
                {"productId": created_products['DIS-MON-27-4K'].id, "quantity": 20, "unit_price": 350.00},
            ],
            custom_date=datetime.now() - timedelta(hours=6)
        )

        create_transaction_with_details(
            'OUT',
            'SO2023008',
            'Sale of Monitor to retail customer',
            [
                {"productId": created_products['DIS-MON-27-4K'].id, "quantity": 2, "unit_price": 400.00},
            ],
            custom_date=datetime.now() - timedelta(hours=5)
        )

    except Exception as e:
        print(f"Error creating Monitor transactions: {e}")




print("\n--- Mock Data Population Complete ---")