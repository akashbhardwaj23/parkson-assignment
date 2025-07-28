# inventory/models.py
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Unique name for the product")
    sku = models.CharField(max_length=50, unique=True, help_text="Stock Keeping Unit, unique identifier")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

class StockTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('IN', 'Inward'),
        ('OUT', 'Outward'),
    ]

    transaction_type = models.CharField(
        max_length=3,
        choices=TRANSACTION_TYPE_CHOICES,
        help_text="Type of transaction: Inward (IN) or Outward (OUT)"
    )
    transaction_date = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True,
                                        help_text="Optional reference number for the transaction (e.g., PO, SO)")
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_type} Transaction on {self.transaction_date.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Stock Transaction"
        verbose_name_plural = "Stock Transactions"
        ordering = ['-transaction_date']

class StockDetail(models.Model):
    transaction = models.ForeignKey(StockTransaction, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.PROTECT) # Don't delete product if part of transaction history
    quantity = models.IntegerField(help_text="Quantity of the product in this transaction detail")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in transaction {self.transaction.id}"

    class Meta:
        verbose_name = "Stock Detail"
        verbose_name_plural = "Stock Details"
        unique_together = ('transaction', 'product')