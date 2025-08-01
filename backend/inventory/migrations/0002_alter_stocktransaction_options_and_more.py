# Generated by Django 5.2.4 on 2025-07-28 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stocktransaction',
            options={'ordering': ['-date'], 'verbose_name': 'Stock Transaction', 'verbose_name_plural': 'Stock Transactions'},
        ),
        migrations.RenameField(
            model_name='stocktransaction',
            old_name='transaction_date',
            new_name='date',
        ),
        migrations.RenameField(
            model_name='stocktransaction',
            old_name='reference_number',
            new_name='reference',
        ),
        migrations.RenameField(
            model_name='stocktransaction',
            old_name='transaction_type',
            new_name='type',
        ),
        migrations.AddField(
            model_name='product',
            name='current_stock',
            field=models.IntegerField(default=0, help_text='Current quantity in stock (managed by transactions)'),
        ),
        migrations.AddField(
            model_name='product',
            name='max_stock',
            field=models.IntegerField(default=1000, help_text='Maximum desired stock level/warehouse capacity'),
        ),
        migrations.AddField(
            model_name='product',
            name='min_stock',
            field=models.IntegerField(default=0, help_text='Minimum desired stock level for alerts'),
        ),
        migrations.AddField(
            model_name='stockdetail',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Unit price at the time of transaction', max_digits=10),
        ),
    ]
