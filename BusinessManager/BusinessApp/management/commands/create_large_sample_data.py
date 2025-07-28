from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import random
from datetime import date, timedelta
from faker import Faker
from BusinessApp.models import (
    Product, Sale, SaleItem, Expense, Project, 
    StockMovement, Notification, Category, 
    ExpenseCategory, Customer, Supplier,
    ElectricalDevice, ElectronicsDevice,
    Debt, DebtPayment
)

fake = Faker()

class Command(BaseCommand):
    help = 'Generate large amounts of sample data for performance testing (20,000+ records)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20000,
            help='Number of records to create for each model (default: 20,000)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data',
        )

    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']
        
        if clear:
            self.stdout.write('Clearing existing data...')
            self.clear_data()
        
        # Get or create admin user
        user = self.get_or_create_admin()
        
        # Create base data first
        self.stdout.write(f'Creating {count} records for each model...')
        
        # Create categories
        categories = self.create_categories()
        expense_categories = self.create_expense_categories()
        
        # Create suppliers
        suppliers = self.create_suppliers(min(count // 10, 1000))  # 10% of products or max 1000
        
        # Create customers
        customers = self.create_customers(min(count // 5, 5000))  # 20% of products or max 5000
        
        # Create products
        products = self.create_products(count, categories, suppliers)
        
        # Create sales and sale items
        sales = self.create_sales(count, customers, user)
        self.create_sale_items(sales, products)
        
        # Create expenses
        self.create_expenses(count, expense_categories, user)
        
        # Create projects
        self.create_projects(count, user)
        
        # Create stock movements
        self.create_stock_movements(count, products, user)
        
        # Create electrical devices
        self.create_electrical_devices(count, user)
        
        # Create electronics devices
        self.create_electronics_devices(count, user)
        
        # Create debts and payments
        credit_sales = [s for s in sales if s.sale_type == 'credit']
        if credit_sales:
            debts = self.create_debts(credit_sales)
            self.create_debt_payments(debts, user)
        
        # Create notifications
        self.create_notifications(count, user)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} records for each model!'))

    def clear_data(self):
        """Clear existing sample data"""
        models_to_clear = [
            DebtPayment, Debt, SaleItem, Sale, StockMovement, 
            Product, Customer, Supplier, Category, Expense, 
            ExpenseCategory, Project, ElectricalDevice, 
            ElectronicsDevice, Notification
        ]
        
        for model in models_to_clear:
            count = model.objects.count()
            if count > 0:
                model.objects.all().delete()
                self.stdout.write(f'Cleared {count} {model.__name__} records')

    def get_or_create_admin(self):
        """Get or create admin user"""
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@businessmanager.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user: admin/admin123'))
        
        return user

    def create_categories(self):
        """Create product categories"""
        category_names = [
            'Electronics', 'Electrical Components', 'Tools & Equipment', 
            'Cables & Wires', 'Lighting', 'Security Systems', 
            'Home Automation', 'Industrial Equipment', 'Solar Products',
            'HVAC Systems', 'Generators', 'Batteries', 'Switches & Sockets',
            'Motors', 'Transformers', 'Circuit Breakers', 'Conduits',
            'Smart Devices', 'Sensors', 'Control Panels'
        ]
        
        categories = []
        for name in category_names:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'description': fake.text(max_nb_chars=200)}
            )
            categories.append(category)
        
        self.stdout.write(f'Created {len(categories)} categories')
        return categories

    def create_expense_categories(self):
        """Create expense categories"""
        category_names = [
            'Office Supplies', 'Transportation', 'Utilities', 'Marketing',
            'Equipment', 'Maintenance', 'Insurance', 'Legal Fees',
            'Professional Services', 'Training', 'Software Licenses',
            'Internet & Phone', 'Rent', 'Fuel', 'Repairs'
        ]
        
        categories = []
        for name in category_names:
            category, created = ExpenseCategory.objects.get_or_create(
                name=name,
                defaults={'description': fake.text(max_nb_chars=200)}
            )
            categories.append(category)
        
        self.stdout.write(f'Created {len(categories)} expense categories')
        return categories

    def create_suppliers(self, count):
        """Create suppliers"""
        suppliers = []
        for i in range(count):
            supplier = Supplier.objects.create(
                name=fake.company(),
                email=fake.email(),
                phone=fake.phone_number()[:20],
                address=fake.address(),
            )
            suppliers.append(supplier)
            
            if (i + 1) % 1000 == 0:
                self.stdout.write(f'Created {i + 1} suppliers...')
        
        self.stdout.write(f'Created {len(suppliers)} suppliers')
        return suppliers

    def create_customers(self, count):
        """Create customers"""
        customers = []
        for i in range(count):
            customer = Customer.objects.create(
                name=fake.name(),
                email=fake.email(),
                phone=fake.phone_number()[:20],
                address=fake.address(),
                national_id=fake.ssn()[:50],
                credit_limit=Decimal(str(random.randint(0, 100000))),
                is_credit_approved=random.choice([True, False]),
            )
            customers.append(customer)
            
            if (i + 1) % 1000 == 0:
                self.stdout.write(f'Created {i + 1} customers...')
        
        self.stdout.write(f'Created {len(customers)} customers')
        return customers

    def create_products(self, count, categories, suppliers):
        """Create products"""
        products = []
        product_names = [
            'LED Bulb', 'Circuit Breaker', 'Power Cable', 'Switch', 'Socket',
            'Transformer', 'Motor', 'Generator', 'Solar Panel', 'Battery',
            'Sensor', 'Controller', 'Relay', 'Fuse', 'Conduit',
            'Wire Connector', 'Junction Box', 'Light Fixture', 'Fan',
            'Inverter', 'Stabilizer', 'Extension Cord', 'Adapter',
            'Smart Switch', 'Motion Detector', 'Thermostat', 'Timer'
        ]
        
        for i in range(count):
            base_name = random.choice(product_names)
            cost_price = Decimal(str(random.randint(10, 1000)))
            selling_price = cost_price * Decimal(str(random.uniform(1.2, 3.0)))
            
            product = Product.objects.create(
                name=f"{base_name} {fake.word().title()} {i+1}",
                description=fake.text(max_nb_chars=300),
                category=random.choice(categories),
                supplier=random.choice(suppliers) if suppliers else None,
                sku=f"SKU{i+1:06d}",
                cost_price=cost_price,
                selling_price=selling_price.quantize(Decimal('0.01')),
                stock_quantity=random.randint(0, 500),
                min_stock_level=random.randint(5, 50),
                is_active=random.choice([True, True, True, False]),  # 75% active
            )
            products.append(product)
            
            if (i + 1) % 5000 == 0:
                self.stdout.write(f'Created {i + 1} products...')
        
        self.stdout.write(f'Created {len(products)} products')
        return products

    def create_sales(self, count, customers, user):
        """Create sales"""
        sales = []
        payment_methods = ['cash', 'card', 'bank_transfer', 'mobile_money', 'credit']
        sale_types = ['cash', 'credit']
        
        for i in range(count):
            sale_type = random.choice(sale_types)
            customer = random.choice(customers) if customers and sale_type == 'credit' else None
            
            sale = Sale.objects.create(
                customer=customer,
                sale_date=fake.date_time_between(start_date='-1y', end_date='now'),
                sale_type=sale_type,
                payment_method=random.choice(payment_methods),
                total_amount=Decimal(str(random.randint(100, 50000))),
                discount=Decimal(str(random.randint(0, 5000))),
                tax=Decimal(str(random.randint(0, 2000))),
                notes=fake.text(max_nb_chars=200) if random.choice([True, False]) else '',
                created_by=user,
            )
            sales.append(sale)
            
            if (i + 1) % 5000 == 0:
                self.stdout.write(f'Created {i + 1} sales...')
        
        self.stdout.write(f'Created {len(sales)} sales')
        return sales

    def create_sale_items(self, sales, products):
        """Create sale items"""
        sale_items = []
        for i, sale in enumerate(sales):
            num_items = random.randint(1, 5)
            sale_products = random.sample(products, min(num_items, len(products)))
            
            for product in sale_products:
                quantity = random.randint(1, 10)
                unit_price = product.selling_price * Decimal(str(random.uniform(0.9, 1.1)))
                
                sale_item = SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price.quantize(Decimal('0.01')),
                )
                sale_items.append(sale_item)
            
            if (i + 1) % 5000 == 0:
                self.stdout.write(f'Created sale items for {i + 1} sales...')
        
        self.stdout.write(f'Created {len(sale_items)} sale items')

    def create_expenses(self, count, categories, user):
        """Create expenses"""
        for i in range(count):
            Expense.objects.create(
                title=fake.sentence(nb_words=4),
                description=fake.text(max_nb_chars=300),
                category=random.choice(categories),
                amount=Decimal(str(random.randint(100, 10000))),
                expense_date=fake.date_between(start_date='-1y', end_date='today'),
                created_by=user,
            )
            
            if (i + 1) % 5000 == 0:
                self.stdout.write(f'Created {i + 1} expenses...')
        
        self.stdout.write(f'Created {count} expenses')

    def create_projects(self, count, user):
        """Create projects"""
        statuses = ['planning', 'in_progress', 'completed', 'on_hold', 'cancelled']
        
        for i in range(count):
            status = random.choice(statuses)
            budget = Decimal(str(random.randint(10000, 1000000)))
            spent = budget * Decimal(str(random.uniform(0, 1.2))) if status != 'planning' else Decimal('0')
            
            Project.objects.create(
                name=f"Project {fake.bs().title()} {i+1}",
                description=fake.text(max_nb_chars=500),
                client=fake.company(),
                budget=budget,
                spent_amount=spent.quantize(Decimal('0.01')),
                start_date=fake.date_between(start_date='-2y', end_date='today'),
                end_date=fake.date_between(start_date='today', end_date='+1y') if status in ['planning', 'in_progress'] else fake.date_between(start_date='-1y', end_date='today'),
                status=status,
                progress=random.randint(0, 100),
                created_by=user,
            )
            
            if (i + 1) % 5000 == 0:
                self.stdout.write(f'Created {i + 1} projects...')
        
        self.stdout.write(f'Created {count} projects')

    def create_stock_movements(self, count, products, user):
        """Create stock movements"""
        movement_types = ['in', 'out', 'adjustment']
        
        for i in range(count):
            StockMovement.objects.create(
                product=random.choice(products),
                movement_type=random.choice(movement_types),
                quantity=random.randint(-100, 100),
                reason=fake.sentence(nb_words=6),
                created_by=user,
            )
            
            if (i + 1) % 5000 == 0:
                self.stdout.write(f'Created {i + 1} stock movements...')
        
        self.stdout.write(f'Created {count} stock movements')

    def create_electrical_devices(self, count, user):
        """Create electrical devices"""
        statuses = ['working', 'maintenance', 'repair', 'damaged', 'retired']
        priorities = ['low', 'medium', 'high', 'critical']
        
        for i in range(count):
            ElectricalDevice.objects.create(
                name=f"Electrical Device {fake.word().title()} {i+1}",
                model_number=fake.bothify(text='##??-####'),
                serial_number=fake.bothify(text='SN######'),
                manufacturer=fake.company(),
                voltage_rating=f"{random.choice([110, 220, 380, 440])}V",
                power_rating=f"{random.randint(100, 5000)}W",
                location=fake.city(),
                status=random.choice(statuses),
                priority=random.choice(priorities),
                purchase_date=fake.date_between(start_date='-5y', end_date='today'),
                warranty_expiry=fake.date_between(start_date='today', end_date='+2y'),
                last_maintenance=fake.date_between(start_date='-1y', end_date='today'),
                next_maintenance=fake.date_between(start_date='today', end_date='+6m'),
                maintenance_cost=Decimal(str(random.randint(100, 5000))),
                description=fake.text(max_nb_chars=300),
                created_by=user,
            )
            
            if (i + 1) % 5000 == 0:
                self.stdout.write(f'Created {i + 1} electrical devices...')
        
        self.stdout.write(f'Created {count} electrical devices')

    def create_electronics_devices(self, count, user):
        """Create electronics devices"""
        statuses = ['working', 'maintenance', 'repair', 'damaged', 'retired']
        priorities = ['low', 'medium', 'high', 'critical']
        device_types = ['computer', 'printer', 'scanner', 'router', 'switch', 'phone', 'tablet', 'monitor', 'projector', 'other']
        
        for i in range(count):
            ElectronicsDevice.objects.create(
                name=f"Electronics Device {fake.word().title()} {i+1}",
                device_type=random.choice(device_types),
                model_number=fake.bothify(text='##??-####'),
                serial_number=fake.bothify(text='SN######'),
                manufacturer=fake.company(),
                operating_system=random.choice(['Windows 11', 'Windows 10', 'macOS', 'Linux', 'Android', 'iOS', 'N/A']),
                specifications=fake.text(max_nb_chars=200),
                location=fake.city(),
                status=random.choice(statuses),
                priority=random.choice(priorities),
                purchase_date=fake.date_between(start_date='-5y', end_date='today'),
                warranty_expiry=fake.date_between(start_date='today', end_date='+3y'),
                last_maintenance=fake.date_between(start_date='-1y', end_date='today'),
                next_maintenance=fake.date_between(start_date='today', end_date='+1y'),
                maintenance_cost=Decimal(str(random.randint(50, 2000))),
                description=fake.text(max_nb_chars=300),
                assigned_to=fake.name(),
                created_by=user,
            )
            
            if (i + 1) % 5000 == 0:
                self.stdout.write(f'Created {i + 1} electronics devices...')
        
        self.stdout.write(f'Created {count} electronics devices')

    def create_debts(self, credit_sales):
        """Create debts for credit sales"""
        debts = []
        statuses = ['outstanding', 'partial', 'paid', 'overdue']
        
        for sale in credit_sales:
            if sale.customer:  # Only create debt if customer exists
                debt = Debt.objects.create(
                    customer=sale.customer,
                    sale=sale,
                    amount=sale.net_amount,
                    due_date=fake.date_between(start_date='today', end_date='+3m'),
                    status=random.choice(statuses),
                    interest_rate=Decimal(str(random.uniform(0, 5))),
                    notes=fake.text(max_nb_chars=200) if random.choice([True, False]) else '',
                )
                debts.append(debt)
        
        self.stdout.write(f'Created {len(debts)} debts')
        return debts

    def create_debt_payments(self, debts, user):
        """Create debt payments"""
        payment_methods = ['cash', 'bank_transfer', 'mobile_money', 'cheque', 'card']
        
        payment_count = 0
        for debt in debts:
            if debt.status in ['partial', 'paid']:
                num_payments = random.randint(1, 5)
                remaining_amount = debt.amount
                
                for i in range(num_payments):
                    if remaining_amount <= 0:
                        break
                    
                    if i == num_payments - 1 and debt.status == 'paid':
                        # Last payment for paid debt
                        payment_amount = remaining_amount
                    else:
                        # Partial payment
                        payment_amount = Decimal(str(random.uniform(float(remaining_amount * Decimal('0.1')), float(remaining_amount * Decimal('0.8')))))
                    
                    DebtPayment.objects.create(
                        debt=debt,
                        amount_paid=payment_amount.quantize(Decimal('0.01')),
                        payment_method=random.choice(payment_methods),
                        reference_number=fake.bothify(text='REF########'),
                        payment_date=fake.date_time_between(start_date=debt.created_at, end_date='now'),
                        notes=fake.text(max_nb_chars=100) if random.choice([True, False]) else '',
                        recorded_by=user,
                    )
                    
                    remaining_amount -= payment_amount
                    payment_count += 1
        
        self.stdout.write(f'Created {payment_count} debt payments')

    def create_notifications(self, count, user):
        """Create notifications"""
        notification_types = ['info', 'warning', 'success', 'error']
        
        for i in range(count):
            Notification.objects.create(
                user=user,
                title=fake.sentence(nb_words=4),
                message=fake.text(max_nb_chars=200),
                notification_type=random.choice(notification_types),
                is_read=random.choice([True, False]),
            )
            
            if (i + 1) % 5000 == 0:
                self.stdout.write(f'Created {i + 1} notifications...')
        
        self.stdout.write(f'Created {count} notifications')
