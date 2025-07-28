# inventory/serializers.py
from rest_framework import serializers
from .models import Product, StockTransaction, StockDetail

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class StockDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)

    class Meta:
        model = StockDetail
        fields = ['product', 'product_name', 'product_sku', 'quantity']
        # 'product' is for writing (ID), 'product_name' and 'product_sku' for reading

class StockTransactionSerializer(serializers.ModelSerializer):
    details = StockDetailSerializer(many=True) # Nested serializer for stock details

    class Meta:
        model = StockTransaction
        fields = ['id', 'transaction_type', 'transaction_date', 'reference_number', 'notes', 'details']
        read_only_fields = ('transaction_date',)

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        transaction = StockTransaction.objects.create(**validated_data)

        for detail_data in details_data:
            product = detail_data['product']
            quantity = detail_data['quantity']

            if transaction.transaction_type == 'OUT' and quantity < 0:
                raise serializers.ValidationError("Outward transactions cannot have negative quantities.")
            if transaction.transaction_type == 'IN' and quantity <= 0:
                 raise serializers.ValidationError("Inward transactions must have positive quantities.")


            # Basic validation: ensure product exists and quantity is positive for IN, or non-negative for OUT
            if not Product.objects.filter(id=product.id).exists():
                raise serializers.ValidationError(f"Product with ID {product.id} does not exist.")
            if quantity == 0:
                raise serializers.ValidationError("Quantity cannot be zero for any transaction.")


            if transaction.transaction_type == 'OUT':
                current_stock = self.get_current_stock_for_product(product.id)
                if current_stock < quantity:
                    raise serializers.ValidationError(f"Insufficient stock for product '{product.name}'. "
                                                      f"Available: {current_stock}, Requested: {quantity}")

            StockDetail.objects.create(transaction=transaction, **detail_data)

        return transaction

    # Get the current stock of the product
    def get_current_stock_for_product(self, product_id):
        in_quantity = StockDetail.objects.filter(
            product_id=product_id,
            transaction__transaction_type='IN'
        ).aggregate(total=serializers.Sum('quantity'))['total'] or 0

        out_quantity = StockDetail.objects.filter(
            product_id=product_id,
            transaction__transaction_type='OUT'
        ).aggregate(total=serializers.Sum('quantity'))['total'] or 0

        return in_quantity - out_quantity

class InventorySerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    product_sku = serializers.CharField()
    current_stock = serializers.IntegerField()