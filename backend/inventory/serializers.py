from rest_framework import serializers
from django.db import transaction as db_transaction
from .models import Product, StockTransaction, StockDetail


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'description', 'current_stock', 'min_stock', 'max_stock']
        read_only_fields = ('current_stock', 'created_at', 'updated_at')

class TransactionDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = StockDetail
        fields = ['id', 'product', 'product_id', 'quantity', 'unit_price']
        extra_kwargs = {
            'product_id': {'write_only': True, 'source': 'product'}
        }

class TransactionSerializer(serializers.ModelSerializer):
    details = TransactionDetailSerializer(many=True)
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = StockTransaction
        fields = ['id', 'type', 'date', 'reference', 'total_items', 'notes', 'details']
        read_only_fields = ('date', 'total_items',)

    def get_total_items(self, obj):
        return sum(detail.quantity for detail in obj.details.all())

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        with db_transaction.atomic():
            transaction_instance = StockTransaction.objects.create(**validated_data)

            for detail_data in details_data:
                product_obj = detail_data['product']
                quantity = detail_data['quantity']
                unit_price = detail_data.get('unit_price', 0.00)

                if not Product.objects.filter(id=product_obj.id).exists():
                    raise serializers.ValidationError(f"Product with ID {product_obj.id} does not exist.")
                if quantity <= 0:
                    raise serializers.ValidationError("Quantity must be greater than zero for any transaction detail.")

                product_to_update = Product.objects.select_for_update().get(id=product_obj.id)

                if transaction_instance.type == 'IN':
                    product_to_update.current_stock += quantity
                    if product_to_update.current_stock > product_to_update.max_stock:
                        print(f"Warning: Stock for {product_to_update.name} ({product_to_update.current_stock}) "
                              f"exceeded max stock ({product_to_update.max_stock}).")

                elif transaction_instance.type == 'OUT':
                    if quantity < 0:
                        raise serializers.ValidationError("Outward quantities must be positive.")

                    if product_to_update.current_stock < quantity:
                        raise serializers.ValidationError(f"Insufficient stock for product '{product_to_update.name}'. "
                                                          f"Available: {product_to_update.current_stock}, Requested: {quantity}.")
                    product_to_update.current_stock -= quantity
                    if product_to_update.current_stock < product_to_update.min_stock:
                        print(f"Warning: Stock for {product_to_update.name} ({product_to_update.current_stock}) "
                              f"fell below min stock ({product_to_update.min_stock}).")
                else:
                    raise serializers.ValidationError(f"Invalid transaction type: {transaction_instance.type}")

                product_to_update.save()

                StockDetail.objects.create(
                    transaction=transaction_instance,
                    product=product_to_update,
                    quantity=quantity,
                    unit_price=unit_price
                )

            return transaction_instance

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'current_stock', 'min_stock', 'max_stock']