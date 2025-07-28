# Migration to add performance indexes after tables are created
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('BusinessApp', '0005_remove_debt_original_amount_and_more'),
    ]

    operations = [
        # Product indexes for better query performance
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_product_is_active ON BusinessApp_product(is_active);",
            reverse_sql="DROP INDEX IF EXISTS idx_product_is_active;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_product_category_active ON BusinessApp_product(category_id, is_active);",
            reverse_sql="DROP INDEX IF EXISTS idx_product_category_active;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_product_supplier_active ON BusinessApp_product(supplier_id, is_active);",
            reverse_sql="DROP INDEX IF EXISTS idx_product_supplier_active;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_product_sku ON BusinessApp_product(sku);",
            reverse_sql="DROP INDEX IF EXISTS idx_product_sku;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_product_name ON BusinessApp_product(name);",
            reverse_sql="DROP INDEX IF EXISTS idx_product_name;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_product_stock_level ON BusinessApp_product(stock_quantity, min_stock_level);",
            reverse_sql="DROP INDEX IF EXISTS idx_product_stock_level;"
        ),

        # Sale indexes for date-based queries and customer lookups
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_sale_date ON BusinessApp_sale(sale_date);",
            reverse_sql="DROP INDEX IF EXISTS idx_sale_date;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_sale_customer_date ON BusinessApp_sale(customer_id, sale_date);",
            reverse_sql="DROP INDEX IF EXISTS idx_sale_customer_date;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_sale_created_by ON BusinessApp_sale(created_by_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_sale_created_by;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_sale_type_date ON BusinessApp_sale(sale_type, sale_date);",
            reverse_sql="DROP INDEX IF EXISTS idx_sale_type_date;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_sale_created_at ON BusinessApp_sale(created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_sale_created_at;"
        ),

        # SaleItem indexes for better joins with products and sales
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_saleitem_sale_product ON BusinessApp_saleitem(sale_id, product_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_saleitem_sale_product;"
        ),

        # Customer indexes for search and credit queries
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_customer_name ON BusinessApp_customer(name);",
            reverse_sql="DROP INDEX IF EXISTS idx_customer_name;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_customer_phone ON BusinessApp_customer(phone);",
            reverse_sql="DROP INDEX IF EXISTS idx_customer_phone;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_customer_email ON BusinessApp_customer(email);",
            reverse_sql="DROP INDEX IF EXISTS idx_customer_email;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_customer_credit_approved ON BusinessApp_customer(is_credit_approved);",
            reverse_sql="DROP INDEX IF EXISTS idx_customer_credit_approved;"
        ),

        # Debt indexes for status and date queries
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_debt_status ON BusinessApp_debt(status);",
            reverse_sql="DROP INDEX IF EXISTS idx_debt_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_debt_customer_status ON BusinessApp_debt(customer_id, status);",
            reverse_sql="DROP INDEX IF EXISTS idx_debt_customer_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_debt_due_date ON BusinessApp_debt(due_date);",
            reverse_sql="DROP INDEX IF EXISTS idx_debt_due_date;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_debt_status_due_date ON BusinessApp_debt(status, due_date);",
            reverse_sql="DROP INDEX IF EXISTS idx_debt_status_due_date;"
        ),

        # DebtPayment indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_debtpayment_debt ON BusinessApp_debtpayment(debt_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_debtpayment_debt;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_debtpayment_date ON BusinessApp_debtpayment(payment_date);",
            reverse_sql="DROP INDEX IF EXISTS idx_debtpayment_date;"
        ),

        # ElectricalDevice indexes for status and maintenance queries
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_electrical_status ON BusinessApp_electricaldevice(status);",
            reverse_sql="DROP INDEX IF EXISTS idx_electrical_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_electrical_priority ON BusinessApp_electricaldevice(priority);",
            reverse_sql="DROP INDEX IF EXISTS idx_electrical_priority;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_electrical_location ON BusinessApp_electricaldevice(location);",
            reverse_sql="DROP INDEX IF EXISTS idx_electrical_location;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_electrical_next_maintenance ON BusinessApp_electricaldevice(next_maintenance);",
            reverse_sql="DROP INDEX IF EXISTS idx_electrical_next_maintenance;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_electrical_name ON BusinessApp_electricaldevice(name);",
            reverse_sql="DROP INDEX IF EXISTS idx_electrical_name;"
        ),

        # ElectronicsDevice indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_electronics_status ON BusinessApp_electronicsdevice(status);",
            reverse_sql="DROP INDEX IF EXISTS idx_electronics_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_electronics_priority ON BusinessApp_electronicsdevice(priority);",
            reverse_sql="DROP INDEX IF EXISTS idx_electronics_priority;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_electronics_device_type ON BusinessApp_electronicsdevice(device_type);",
            reverse_sql="DROP INDEX IF EXISTS idx_electronics_device_type;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_electronics_location ON BusinessApp_electronicsdevice(location);",
            reverse_sql="DROP INDEX IF EXISTS idx_electronics_location;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_electronics_next_maintenance ON BusinessApp_electronicsdevice(next_maintenance);",
            reverse_sql="DROP INDEX IF EXISTS idx_electronics_next_maintenance;"
        ),

        # Expense indexes for date and category queries
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_expense_date ON BusinessApp_expense(expense_date);",
            reverse_sql="DROP INDEX IF EXISTS idx_expense_date;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_expense_category_date ON BusinessApp_expense(category_id, expense_date);",
            reverse_sql="DROP INDEX IF EXISTS idx_expense_category_date;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_expense_created_by ON BusinessApp_expense(created_by_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_expense_created_by;"
        ),

        # Project indexes for status and date queries
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_project_status ON BusinessApp_project(status);",
            reverse_sql="DROP INDEX IF EXISTS idx_project_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_project_start_date ON BusinessApp_project(start_date);",
            reverse_sql="DROP INDEX IF EXISTS idx_project_start_date;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_project_end_date ON BusinessApp_project(end_date);",
            reverse_sql="DROP INDEX IF EXISTS idx_project_end_date;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_project_created_by ON BusinessApp_project(created_by_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_project_created_by;"
        ),

        # StockMovement indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_stockmovement_product ON BusinessApp_stockmovement(product_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_stockmovement_product;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_stockmovement_type_date ON BusinessApp_stockmovement(movement_type, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_stockmovement_type_date;"
        ),

        # Notification indexes for user and read status
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_notification_user_read ON BusinessApp_notification(user_id, is_read);",
            reverse_sql="DROP INDEX IF EXISTS idx_notification_user_read;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_notification_created_at ON BusinessApp_notification(created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_notification_created_at;"
        ),

        # Category and Supplier indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_category_name ON BusinessApp_category(name);",
            reverse_sql="DROP INDEX IF EXISTS idx_category_name;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_supplier_name ON BusinessApp_supplier(name);",
            reverse_sql="DROP INDEX IF EXISTS idx_supplier_name;"
        ),

        # Composite indexes for common query patterns
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_product_category_stock ON BusinessApp_product(category_id, stock_quantity, is_active);",
            reverse_sql="DROP INDEX IF EXISTS idx_product_category_stock;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_sale_customer_type_date ON BusinessApp_sale(customer_id, sale_type, sale_date);",
            reverse_sql="DROP INDEX IF EXISTS idx_sale_customer_type_date;"
        ),
    ]
