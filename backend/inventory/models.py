from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Unique name for the product")
    sku = models.CharField(max_length=50, unique=True, help_text="Stock Keeping Unit, unique identifier")
    description = models.TextField(blank=True, null=True)
    current_stock = models.IntegerField(default=0, help_text="Current quantity in stock (managed by transactions)")
    min_stock = models.IntegerField(default=0, help_text="Minimum desired stock level for alerts")
    max_stock = models.IntegerField(default=1000, help_text="Maximum desired stock level/warehouse capacity")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.sku}) - Stock: {self.current_stock}"

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

class StockTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('IN', 'Inward'),
        ('OUT', 'Outward'),
    ]

    type = models.CharField(
        max_length=3,
        choices=TRANSACTION_TYPE_CHOICES,
        help_text="Type of transaction: Inward (IN) or Outward (OUT)"
    )
    date = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=100, blank=True, null=True,
                                 help_text="Optional reference number for the transaction (e.g., PO, SO)")

    notes = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"{self.type} Transaction on {self.date.strftime('%Y-%m-%d %H:%M')} (Ref: {self.reference or 'N/A'})"

    class Meta:
        verbose_name = "Stock Transaction"
        verbose_name_plural = "Stock Transactions"
        ordering = ['-date']

class StockDetail(models.Model):
    transaction = models.ForeignKey(StockTransaction, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(help_text="Quantity of the product in this transaction detail")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Unit price at the time of transaction")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} @ {self.unit_price} in transaction {self.transaction.id}"

    class Meta:
        verbose_name = "Stock Detail"
        verbose_name_plural = "Stock Details"
        unique_together = ('transaction', 'product')