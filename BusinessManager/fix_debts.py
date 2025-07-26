#!/usr/bin/env python
"""
Script to create missing debt records for existing credit sales
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BusinessManager.settings')
django.setup()

from BusinessApp.models import Sale, Debt
from datetime import datetime, timedelta

def create_missing_debts():
    """Create debt records for credit sales that don't have them"""
    
    # Find credit sales without debt records
    credit_sales_without_debts = Sale.objects.filter(
        sale_type='credit'
    ).exclude(
        debt__isnull=False
    )
    
    print(f"Found {credit_sales_without_debts.count()} credit sales without debt records")
    
    created_count = 0
    for sale in credit_sales_without_debts:
        try:
            # Set due date to 30 days from sale date if not specified
            default_due_date = sale.sale_date.date() + timedelta(days=30)
            
            debt = Debt.objects.create(
                customer=sale.customer,
                sale=sale,
                amount=sale.total_amount,
                due_date=default_due_date,
                status='outstanding'
            )
            
            print(f"Created debt #{debt.id} for sale #{sale.id} - Customer: {sale.customer.name}, Amount: TSh {sale.total_amount}")
            created_count += 1
            
        except Exception as e:
            print(f"Error creating debt for sale #{sale.id}: {str(e)}")
    
    print(f"\nSuccessfully created {created_count} debt records")
    return created_count

if __name__ == '__main__':
    create_missing_debts()
