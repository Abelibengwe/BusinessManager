# Generated migration for additional performance optimization using Django indexes
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BusinessApp', '0006_add_performance_indexes'),
    ]

    operations = [
        # Add Django-style indexes for better ORM integration
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['is_active'], name='product_is_active_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['category', 'is_active'], name='product_category_active_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['stock_quantity', 'min_stock_level'], name='product_stock_level_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['-created_at'], name='product_created_at_idx'),
        ),
        
        migrations.AddIndex(
            model_name='sale',
            index=models.Index(fields=['sale_date'], name='sale_date_idx'),
        ),
        migrations.AddIndex(
            model_name='sale',
            index=models.Index(fields=['customer', 'sale_date'], name='sale_customer_date_idx'),
        ),
        migrations.AddIndex(
            model_name='sale',
            index=models.Index(fields=['-created_at'], name='sale_created_at_idx'),
        ),
        migrations.AddIndex(
            model_name='sale',
            index=models.Index(fields=['sale_type', 'sale_date'], name='sale_type_date_idx'),
        ),
        
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(fields=['is_credit_approved'], name='customer_credit_approved_idx'),
        ),
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(fields=['phone'], name='customer_phone_idx'),
        ),
        
        migrations.AddIndex(
            model_name='debt',
            index=models.Index(fields=['status'], name='debt_status_idx'),
        ),
        migrations.AddIndex(
            model_name='debt',
            index=models.Index(fields=['customer', 'status'], name='debt_customer_status_idx'),
        ),
        migrations.AddIndex(
            model_name='debt',
            index=models.Index(fields=['due_date'], name='debt_due_date_idx'),
        ),
        
        migrations.AddIndex(
            model_name='electricaldevice',
            index=models.Index(fields=['status'], name='electrical_status_idx'),
        ),
        migrations.AddIndex(
            model_name='electricaldevice',
            index=models.Index(fields=['priority'], name='electrical_priority_idx'),
        ),
        migrations.AddIndex(
            model_name='electricaldevice',
            index=models.Index(fields=['next_maintenance'], name='electrical_maintenance_idx'),
        ),
        migrations.AddIndex(
            model_name='electricaldevice',
            index=models.Index(fields=['-created_at'], name='electrical_created_at_idx'),
        ),
        
        migrations.AddIndex(
            model_name='electronicsdevice',
            index=models.Index(fields=['status'], name='electronics_status_idx'),
        ),
        migrations.AddIndex(
            model_name='electronicsdevice',
            index=models.Index(fields=['priority'], name='electronics_priority_idx'),
        ),
        migrations.AddIndex(
            model_name='electronicsdevice',
            index=models.Index(fields=['device_type'], name='electronics_type_idx'),
        ),
        migrations.AddIndex(
            model_name='electronicsdevice',
            index=models.Index(fields=['next_maintenance'], name='electronics_maintenance_idx'),
        ),
        migrations.AddIndex(
            model_name='electronicsdevice',
            index=models.Index(fields=['-created_at'], name='electronics_created_at_idx'),
        ),
        
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['expense_date'], name='expense_date_idx'),
        ),
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['category', 'expense_date'], name='expense_category_date_idx'),
        ),
        
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['status'], name='project_status_idx'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['start_date'], name='project_start_date_idx'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['end_date'], name='project_end_date_idx'),
        ),
        
        migrations.AddIndex(
            model_name='stockmovement',
            index=models.Index(fields=['product', 'movement_type'], name='stock_product_type_idx'),
        ),
        migrations.AddIndex(
            model_name='stockmovement',
            index=models.Index(fields=['-created_at'], name='stock_created_at_idx'),
        ),
        
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', 'is_read'], name='notification_user_read_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['-created_at'], name='notification_created_at_idx'),
        ),
        
        migrations.AddIndex(
            model_name='saleitem',
            index=models.Index(fields=['sale', 'product'], name='saleitem_sale_product_idx'),
        ),
        
        migrations.AddIndex(
            model_name='debtpayment',
            index=models.Index(fields=['debt'], name='debtpayment_debt_idx'),
        ),
        migrations.AddIndex(
            model_name='debtpayment',
            index=models.Index(fields=['payment_date'], name='debtpayment_date_idx'),
        ),
    ]
