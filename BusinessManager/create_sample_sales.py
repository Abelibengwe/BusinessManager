#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BusinessManager.settings')
django.setup()

from BusinessApp.models import Sale, Product, Customer, Category
from django.contrib.auth.models import User
from django.utils import timezone

def create_sample_sales():
    print("Creating sample sales data...")
    
    # Get or create a user (admin)
    try:
        user = User.objects.get(username='admin')
    except User.DoesNotExist:
        user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Created admin user")
    
    # Get or create a category
    category, created = Category.objects.get_or_create(
        name='General',
        defaults={'description': 'General category for products'}
    )
    if created:
        print("Created default category")
    
    # Get or create a customer
    customer, created = Customer.objects.get_or_create(
        name='Walk-in Customer',
        defaults={
            'email': 'walkin@example.com',
            'phone': '123-456-7890',
            'address': 'N/A'
        }
    )
    if created:
        print("Created default customer")
    
    # Get or create some products
    products = []
    sample_products = [
        {'name': 'Sample Product 1', 'sku': 'SP001', 'price': 25000, 'cost': 15000},
        {'name': 'Sample Product 2', 'sku': 'SP002', 'price': 45000, 'cost': 30000},
        {'name': 'Sample Product 3', 'sku': 'SP003', 'price': 15000, 'cost': 8000},
    ]
    
    for prod_data in sample_products:
        product, created = Product.objects.get_or_create(
            sku=prod_data['sku'],
            defaults={
                'name': prod_data['name'],
                'category': category,
                'selling_price': Decimal(str(prod_data['price'])),
                'cost_price': Decimal(str(prod_data['cost'])),
                'stock_quantity': 100,
                'min_stock_level': 10,
                'is_active': True
            }
        )
        products.append(product)
        if created:
            print(f"Created product: {product.name}")
    
    # Create sample sales for the last 30 days
    today = timezone.now().date()
    sales_created = 0
    
    for i in range(30):
        sale_date = today - timedelta(days=i)
        
        # Create 1-3 random sales per day (some days might have no sales)
        import random
        num_sales = random.choice([0, 1, 1, 2, 2, 3])  # Some days with no sales
        
        for j in range(num_sales):
            # Random sale amount between 15,000 and 100,000 Tsh
            total_amount = Decimal(str(random.randint(15000, 100000)))
            discount = Decimal('0')
            tax = total_amount * Decimal('0.18')  # 18% tax
            
            sale = Sale.objects.create(
                customer=customer,
                sale_date=timezone.make_aware(datetime.combine(sale_date, datetime.min.time())),
                total_amount=total_amount,
                discount=discount,
                tax=tax,
                payment_method='cash',
                notes=f'Sample sale #{sales_created + 1}',
                created_by=user
            )
            sales_created += 1
    
    print(f"Created {sales_created} sample sales")
    print("Sample sales data creation completed!")

if __name__ == '__main__':
    create_sample_sales()
