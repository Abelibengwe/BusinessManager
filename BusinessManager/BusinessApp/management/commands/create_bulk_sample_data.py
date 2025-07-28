from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import random
import string
from datetime import date, timedelta
from BusinessApp.models import (
    Product, Sale, SaleItem, Expense, Project, 
    StockMovement, Notification, Category, 
    ExpenseCategory, Customer, Supplier,
    ElectricalDevice, ElectronicsDevice,
    Debt, DebtPayment
)

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

    def generate_name(self):
        """Generate a random name"""
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'James', 'Lisa', 'Robert', 'Mary', 'William', 'Patricia', 'Richard', 'Jennifer', 'Joseph', 'Linda', 'Thomas', 'Elizabeth', 'Christopher', 'Barbara']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin']
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    def generate_company(self):
        """Generate a random company name"""
        prefixes = ['Tech', 'Global', 'Smart', 'Advanced', 'Prime', 'Elite', 'Dynamic', 'Innovative', 'Superior', 'Professional']
        suffixes = ['Solutions', 'Systems', 'Industries', 'Corporation', 'Enterprises', 'Group', 'International', 'Technologies', 'Services', 'Partners']
        return f"{random.choice(prefixes)} {random.choice(suffixes)}"

    def generate_email(self, name=None):
        """Generate a random email"""
        if name:
            username = name.lower().replace(' ', '.')
        else:
            username = ''.join(random.choices(string.ascii_lowercase, k=8))
        domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'company.com', 'business.co.tz']
        return f"{username}@{random.choice(domains)}"

    def generate_phone(self):
        """Generate a random phone number"""
        return f"+255{random.randint(700000000, 799999999)}"

    def generate_address(self):
        """Generate a random address"""
        streets = ['Main St', 'Oak Ave', 'Pine Rd', 'Elm St', 'Cedar Ave', 'Maple Dr', 'First St', 'Second Ave', 'Park Rd', 'Hill St']
        cities = ['Dar es Salaam', 'Arusha', 'Mwanza', 'Dodoma', 'Mbeya', 'Tanga', 'Morogoro', 'Tabora', 'Kigoma', 'Iringa']
        return f"{random.randint(1, 999)} {random.choice(streets)}, {random.choice(cities)}"

    def generate_text(self, max_words=20):
        """Generate random text"""
        words = ['business', 'management', 'system', 'quality', 'service', 'professional', 'excellent', 'reliable', 'efficient', 'modern', 'innovative', 'advanced', 'comprehensive', 'complete', 'perfect', 'outstanding', 'superior', 'premium', 'standard', 'basic']
        return ' '.join(random.choices(words, k=random.randint(5, max_words)))

    def generate_random_date(self, start_days_ago=365, end_days_ago=0):
        """Generate a random date"""
        start_date = timezone.now().date() - timedelta(days=start_days_ago)
        end_date = timezone.now().date() - timedelta(days=end_days_ago)
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randrange(days_between + 1)
        return start_date + timedelta(days=random_days)

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
                defaults={'description': self.generate_text(15)}
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
                defaults={'description': self.generate_text(10)}
            )
            categories.append(category)
        
        self.stdout.write(f'Created {len(categories)} expense categories')
        return categories

    def create_suppliers(self, count):
        """Create suppliers"""
        suppliers = []
        for i in range(count):
            company_name = self.generate_company()
            supplier = Supplier.objects.create(
                name=company_name,
                email=self.generate_email(),
                phone=self.generate_phone(),
                address=self.generate_address(),
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
            name = self.generate_name()
            customer = Customer.objects.create(
                name=name,
                email=self.generate_email(name),
                phone=self.generate_phone(),
                address=self.generate_address(),
                national_id=f"ID{random.randint(10000000, 99999999)}",
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
                name=f"{base_name} Model {i+1}",
                description=self.generate_text(20),
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
                sale_date=timezone.make_aware(
                    timezone.datetime.combine(
                        self.generate_random_date(365, 0),
                        timezone.datetime.min.time()
                    )
                ),
                sale_type=sale_type,
                payment_method=random.choice(payment_methods),
                total_amount=Decimal(str(random.randint(100, 50000))),
                discount=Decimal(str(random.randint(0, 5000))),
                tax=Decimal(str(random.randint(0, 2000))),
                notes=self.generate_text(15) if random.choice([True, False]) else '',
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
                title=f"Expense {self.generate_text(3)}",
                description=self.generate_text(15),
                category=random.choice(categories),
                amount=Decimal(str(random.randint(100, 10000))),
                expense_date=self.generate_random_date(365, 0),
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
                name=f"Project {self.generate_text(3)} {i+1}",
                description=self.generate_text(25),
                client=self.generate_company(),
                budget=budget,
                spent_amount=spent.quantize(Decimal('0.01')),
                start_date=self.generate_random_date(730, 0),
                end_date=self.generate_random_date(0, -365) if status in ['planning', 'in_progress'] else self.generate_random_date(365, 0),
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
                reason=self.generate_text(6),
                created_by=user,
            )
            
            if (i + 1) % 5000 == 0:
                self.stdout.write(f'Created {i + 1} stock movements...')
        
        self.stdout.write(f'Created {count} stock movements')

    def create_electrical_devices(self, count, user):
        """Create electrical devices"""
        statuses = ['working', 'maintenance', 'repair', 'damaged', 'retired']
        priorities = ['low', 'medium', 'high', 'critical']
        locations = ['Main Office', 'Warehouse', 'Factory Floor', 'Server Room', 'Workshop', 'Building A', 'Building B']
        
        for i in range(count):
            ElectricalDevice.objects.create(
                name=f"Electrical Device {i+1}",
                model_number=f"ED{random.randint(1000, 9999)}",
                serial_number=f"SN{random.randint(100000, 999999)}",
                manufacturer=self.generate_company(),
                voltage_rating=f"{random.choice([110, 220, 380, 440])}V",
                power_rating=f"{random.randint(100, 5000)}W",
                location=random.choice(locations),
                status=random.choice(statuses),
                priority=random.choice(priorities),
                purchase_date=self.generate_random_date(1825, 0),
                warranty_expiry=self.generate_random_date(-30, -730),
                last_maintenance=self.generate_random_date(365, 0),
                next_maintenance=self.generate_random_date(-30, -180),
                maintenance_cost=Decimal(str(random.randint(100, 5000))),
                description=self.generate_text(15),
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
        locations = ['Main Office', 'IT Department', 'Reception', 'Conference Room', 'Finance Dept', 'HR Department']
        
        for i in range(count):
            ElectronicsDevice.objects.create(
                name=f"Electronics Device {i+1}",
                device_type=random.choice(device_types),
                model_number=f"EL{random.randint(1000, 9999)}",
                serial_number=f"SN{random.randint(100000, 999999)}",
                manufacturer=self.generate_company(),
                operating_system=random.choice(['Windows 11', 'Windows 10', 'macOS', 'Linux', 'Android', 'iOS', 'N/A']),
                specifications=self.generate_text(10),
                location=random.choice(locations),
                status=random.choice(statuses),
                priority=random.choice(priorities),
                purchase_date=self.generate_random_date(1825, 0),
                warranty_expiry=self.generate_random_date(-30, -1095),
                last_maintenance=self.generate_random_date(365, 0),
                next_maintenance=self.generate_random_date(-30, -365),
                maintenance_cost=Decimal(str(random.randint(50, 2000))),
                description=self.generate_text(15),
                assigned_to=self.generate_name(),
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
                    due_date=self.generate_random_date(-30, -90),
                    status=random.choice(statuses),
                    interest_rate=Decimal(str(random.uniform(0, 5))),
                    notes=self.generate_text(10) if random.choice([True, False]) else '',
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
                        reference_number=f"REF{random.randint(10000000, 99999999)}",
                        payment_date=timezone.make_aware(
                            timezone.datetime.combine(
                                self.generate_random_date(30, 0),
                                timezone.datetime.min.time()
                            )
                        ),
                        notes=self.generate_text(5) if random.choice([True, False]) else '',
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
                title=self.generate_text(4),
                message=self.generate_text(20),
                notification_type=random.choice(notification_types),
                is_read=random.choice([True, False]),
            )
            
            if (i + 1) % 5000 == 0:
                self.stdout.write(f'Created {i + 1} notifications...')
        
        self.stdout.write(f'Created {count} notifications')
