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
    help = 'Generate massive amounts of sample data using bulk operations for maximum performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50000,
            help='Number of records to create for each model (default: 50,000)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Batch size for bulk operations (default: 1000)',
        )

    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']
        batch_size = options['batch_size']
        
        if clear:
            self.stdout.write('Clearing existing data...')
            self.clear_data()
        
        # Get or create admin user
        user = self.get_or_create_admin()
        
        # Create base data first
        self.stdout.write(f'Creating {count} records for each model using batch size {batch_size}...')
        
        # Create categories
        categories = self.create_categories()
        expense_categories = self.create_expense_categories()
        
        # Create suppliers
        suppliers = self.create_suppliers_bulk(min(count // 10, 5000), batch_size)
        
        # Create customers
        customers = self.create_customers_bulk(min(count // 5, 10000), batch_size)
        
        # Create products
        products = self.create_products_bulk(count, categories, suppliers, batch_size)
        
        # Create sales
        sales = self.create_sales_bulk(count, customers, user, batch_size)
        
        # Create sale items
        self.create_sale_items_bulk(sales, products, batch_size)
        
        # Create expenses
        self.create_expenses_bulk(count, expense_categories, user, batch_size)
        
        # Create projects
        self.create_projects_bulk(count, user, batch_size)
        
        # Create stock movements
        self.create_stock_movements_bulk(count, products, user, batch_size)
        
        # Create electrical devices
        self.create_electrical_devices_bulk(count, user, batch_size)
        
        # Create electronics devices
        self.create_electronics_devices_bulk(count, user, batch_size)
        
        # Create debts and payments
        credit_sales = [s for s in sales if s.sale_type == 'credit']
        if credit_sales:
            debts = self.create_debts_bulk(credit_sales, batch_size)
            self.create_debt_payments_bulk(debts, user, batch_size)
        
        # Create notifications
        self.create_notifications_bulk(count, user, batch_size)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} records for each model!'))

    def generate_name(self):
        """Generate a random name"""
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'James', 'Lisa', 'Robert', 'Mary', 'William', 'Patricia', 'Richard', 'Jennifer', 'Joseph', 'Linda', 'Thomas', 'Elizabeth', 'Christopher', 'Barbara', 'Daniel', 'Helen', 'Matthew', 'Nancy', 'Anthony', 'Betty', 'Mark', 'Dorothy', 'Donald', 'Sandra']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson']
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    def generate_company(self):
        """Generate a random company name"""
        prefixes = ['Tech', 'Global', 'Smart', 'Advanced', 'Prime', 'Elite', 'Dynamic', 'Innovative', 'Superior', 'Professional', 'Digital', 'Modern', 'Future', 'Next', 'Ultra']
        suffixes = ['Solutions', 'Systems', 'Industries', 'Corporation', 'Enterprises', 'Group', 'International', 'Technologies', 'Services', 'Partners', 'Ltd', 'Inc', 'Co', 'Dynamics', 'Works']
        return f"{random.choice(prefixes)} {random.choice(suffixes)}"

    def generate_email(self, name=None):
        """Generate a random email"""
        if name:
            username = name.lower().replace(' ', '.')
        else:
            username = ''.join(random.choices(string.ascii_lowercase, k=8))
        domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'company.com', 'business.co.tz', 'hotmail.com', 'live.com']
        return f"{username}@{random.choice(domains)}"

    def generate_phone(self):
        """Generate a random phone number"""
        prefixes = ['+255700', '+255701', '+255702', '+255703', '+255704', '+255705', '+255706', '+255707', '+255708', '+255709']
        return f"{random.choice(prefixes)}{random.randint(100000, 999999)}"

    def generate_address(self):
        """Generate a random address"""
        streets = ['Main St', 'Oak Ave', 'Pine Rd', 'Elm St', 'Cedar Ave', 'Maple Dr', 'First St', 'Second Ave', 'Park Rd', 'Hill St', 'Church St', 'School Rd', 'Market St', 'High St', 'King St']
        cities = ['Dar es Salaam', 'Arusha', 'Mwanza', 'Dodoma', 'Mbeya', 'Tanga', 'Morogoro', 'Tabora', 'Kigoma', 'Iringa', 'Moshi', 'Bukoba', 'Musoma', 'Singida', 'Songea']
        return f"{random.randint(1, 999)} {random.choice(streets)}, {random.choice(cities)}"

    def generate_text(self, max_words=20):
        """Generate random text"""
        words = ['business', 'management', 'system', 'quality', 'service', 'professional', 'excellent', 'reliable', 'efficient', 'modern', 'innovative', 'advanced', 'comprehensive', 'complete', 'perfect', 'outstanding', 'superior', 'premium', 'standard', 'basic', 'technical', 'industrial', 'commercial', 'residential', 'electrical', 'electronic', 'digital', 'automated', 'smart', 'intelligent']
        min_words = min(3, max_words)
        return ' '.join(random.choices(words, k=random.randint(min_words, max_words)))

    def generate_random_date(self, start_days_ago=365, end_days_ago=0):
        """Generate a random date"""
        start_date = timezone.now().date() - timedelta(days=start_days_ago)
        end_date = timezone.now().date() - timedelta(days=end_days_ago)
        time_between = end_date - start_date
        days_between = time_between.days
        if days_between <= 0:
            return start_date
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
            'Smart Devices', 'Sensors', 'Control Panels', 'Power Supplies',
            'Network Equipment', 'Computer Hardware', 'Mobile Devices', 'Accessories'
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
            'Internet & Phone', 'Rent', 'Fuel', 'Repairs', 'Consulting',
            'Travel', 'Entertainment', 'Subscriptions', 'Taxes'
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

    def create_suppliers_bulk(self, count, batch_size):
        """Create suppliers using bulk operations"""
        suppliers = []
        suppliers_to_create = []
        
        for i in range(count):
            company_name = self.generate_company()
            supplier = Supplier(
                name=company_name,
                email=self.generate_email(),
                phone=self.generate_phone(),
                address=self.generate_address(),
            )
            suppliers_to_create.append(supplier)
            
            if len(suppliers_to_create) >= batch_size:
                created_suppliers = Supplier.objects.bulk_create(suppliers_to_create)
                suppliers.extend(created_suppliers)
                suppliers_to_create = []
                self.stdout.write(f'Created {len(suppliers)} suppliers...')
        
        if suppliers_to_create:
            created_suppliers = Supplier.objects.bulk_create(suppliers_to_create)
            suppliers.extend(created_suppliers)
        
        self.stdout.write(f'Created {len(suppliers)} suppliers total')
        return suppliers

    def create_customers_bulk(self, count, batch_size):
        """Create customers using bulk operations"""
        customers = []
        customers_to_create = []
        
        for i in range(count):
            name = self.generate_name()
            customer = Customer(
                name=name,
                email=self.generate_email(name),
                phone=self.generate_phone(),
                address=self.generate_address(),
                national_id=f"ID{random.randint(10000000, 99999999)}",
                credit_limit=Decimal(str(random.randint(0, 200000))),
                is_credit_approved=random.choice([True, False]),
            )
            customers_to_create.append(customer)
            
            if len(customers_to_create) >= batch_size:
                created_customers = Customer.objects.bulk_create(customers_to_create)
                customers.extend(created_customers)
                customers_to_create = []
                self.stdout.write(f'Created {len(customers)} customers...')
        
        if customers_to_create:
            created_customers = Customer.objects.bulk_create(customers_to_create)
            customers.extend(created_customers)
        
        self.stdout.write(f'Created {len(customers)} customers total')
        return customers

    def create_products_bulk(self, count, categories, suppliers, batch_size):
        """Create products using bulk operations"""
        products = []
        products_to_create = []
        
        product_names = [
            'LED Bulb', 'Circuit Breaker', 'Power Cable', 'Switch', 'Socket',
            'Transformer', 'Motor', 'Generator', 'Solar Panel', 'Battery',
            'Sensor', 'Controller', 'Relay', 'Fuse', 'Conduit',
            'Wire Connector', 'Junction Box', 'Light Fixture', 'Fan',
            'Inverter', 'Stabilizer', 'Extension Cord', 'Adapter',
            'Smart Switch', 'Motion Detector', 'Thermostat', 'Timer',
            'Router', 'Computer', 'Monitor', 'Keyboard', 'Mouse'
        ]
        
        for i in range(count):
            base_name = random.choice(product_names)
            cost_price = Decimal(str(random.randint(10, 2000)))
            selling_price = cost_price * Decimal(str(random.uniform(1.2, 4.0)))
            
            product = Product(
                name=f"{base_name} Model {i+1}",
                description=self.generate_text(20),
                category=random.choice(categories),
                supplier=random.choice(suppliers) if suppliers else None,
                sku=f"SKU{i+1:08d}",
                cost_price=cost_price,
                selling_price=selling_price.quantize(Decimal('0.01')),
                stock_quantity=random.randint(0, 1000),
                min_stock_level=random.randint(5, 100),
                is_active=random.choice([True, True, True, False]),  # 75% active
            )
            products_to_create.append(product)
            
            if len(products_to_create) >= batch_size:
                created_products = Product.objects.bulk_create(products_to_create)
                products.extend(created_products)
                products_to_create = []
                self.stdout.write(f'Created {len(products)} products...')
        
        if products_to_create:
            created_products = Product.objects.bulk_create(products_to_create)
            products.extend(created_products)
        
        self.stdout.write(f'Created {len(products)} products total')
        return products

    def create_sales_bulk(self, count, customers, user, batch_size):
        """Create sales using bulk operations"""
        sales = []
        sales_to_create = []
        
        payment_methods = ['cash', 'card', 'bank_transfer', 'mobile_money', 'credit']
        sale_types = ['cash', 'credit']
        
        for i in range(count):
            sale_type = random.choice(sale_types)
            customer = random.choice(customers) if customers and sale_type == 'credit' else None
            
            sale = Sale(
                customer=customer,
                sale_date=timezone.make_aware(
                    timezone.datetime.combine(
                        self.generate_random_date(365, 0),
                        timezone.datetime.min.time()
                    )
                ),
                sale_type=sale_type,
                payment_method=random.choice(payment_methods),
                total_amount=Decimal(str(random.randint(100, 100000))),
                discount=Decimal(str(random.randint(0, 10000))),
                tax=Decimal(str(random.randint(0, 5000))),
                notes=self.generate_text(15) if random.choice([True, False]) else '',
                created_by=user,
            )
            sales_to_create.append(sale)
            
            if len(sales_to_create) >= batch_size:
                created_sales = Sale.objects.bulk_create(sales_to_create)
                sales.extend(created_sales)
                sales_to_create = []
                self.stdout.write(f'Created {len(sales)} sales...')
        
        if sales_to_create:
            created_sales = Sale.objects.bulk_create(sales_to_create)
            sales.extend(created_sales)
        
        self.stdout.write(f'Created {len(sales)} sales total')
        return sales

    def create_sale_items_bulk(self, sales, products, batch_size):
        """Create sale items using bulk operations"""
        sale_items_to_create = []
        total_items = 0
        
        for i, sale in enumerate(sales):
            num_items = random.randint(1, 8)
            sale_products = random.sample(products, min(num_items, len(products)))
            
            for product in sale_products:
                quantity = random.randint(1, 15)
                unit_price = product.selling_price * Decimal(str(random.uniform(0.8, 1.2)))
                
                sale_item = SaleItem(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price.quantize(Decimal('0.01')),
                )
                sale_items_to_create.append(sale_item)
            
            if len(sale_items_to_create) >= batch_size:
                SaleItem.objects.bulk_create(sale_items_to_create)
                total_items += len(sale_items_to_create)
                sale_items_to_create = []
                self.stdout.write(f'Created {total_items} sale items...')
        
        if sale_items_to_create:
            SaleItem.objects.bulk_create(sale_items_to_create)
            total_items += len(sale_items_to_create)
        
        self.stdout.write(f'Created {total_items} sale items total')

    def create_expenses_bulk(self, count, categories, user, batch_size):
        """Create expenses using bulk operations"""
        expenses_to_create = []
        
        for i in range(count):
            expense = Expense(
                title=f"Expense {self.generate_text(3)}",
                description=self.generate_text(15),
                category=random.choice(categories),
                amount=Decimal(str(random.randint(100, 20000))),
                expense_date=self.generate_random_date(365, 0),
                created_by=user,
            )
            expenses_to_create.append(expense)
            
            if len(expenses_to_create) >= batch_size:
                Expense.objects.bulk_create(expenses_to_create)
                expenses_to_create = []
                self.stdout.write(f'Created {i + 1} expenses...')
        
        if expenses_to_create:
            Expense.objects.bulk_create(expenses_to_create)
        
        self.stdout.write(f'Created {count} expenses total')

    def create_projects_bulk(self, count, user, batch_size):
        """Create projects using bulk operations"""
        projects_to_create = []
        statuses = ['planning', 'in_progress', 'completed', 'on_hold', 'cancelled']
        
        for i in range(count):
            status = random.choice(statuses)
            budget = Decimal(str(random.randint(10000, 2000000)))
            spent = budget * Decimal(str(random.uniform(0, 1.3))) if status != 'planning' else Decimal('0')
            
            project = Project(
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
            projects_to_create.append(project)
            
            if len(projects_to_create) >= batch_size:
                Project.objects.bulk_create(projects_to_create)
                projects_to_create = []
                self.stdout.write(f'Created {i + 1} projects...')
        
        if projects_to_create:
            Project.objects.bulk_create(projects_to_create)
        
        self.stdout.write(f'Created {count} projects total')

    def create_stock_movements_bulk(self, count, products, user, batch_size):
        """Create stock movements using bulk operations"""
        movements_to_create = []
        movement_types = ['in', 'out', 'adjustment']
        
        for i in range(count):
            movement = StockMovement(
                product=random.choice(products),
                movement_type=random.choice(movement_types),
                quantity=random.randint(-200, 200),
                reason=self.generate_text(6),
                created_by=user,
            )
            movements_to_create.append(movement)
            
            if len(movements_to_create) >= batch_size:
                StockMovement.objects.bulk_create(movements_to_create)
                movements_to_create = []
                self.stdout.write(f'Created {i + 1} stock movements...')
        
        if movements_to_create:
            StockMovement.objects.bulk_create(movements_to_create)
        
        self.stdout.write(f'Created {count} stock movements total')

    def create_electrical_devices_bulk(self, count, user, batch_size):
        """Create electrical devices using bulk operations"""
        devices_to_create = []
        statuses = ['working', 'maintenance', 'repair', 'damaged', 'retired']
        priorities = ['low', 'medium', 'high', 'critical']
        locations = ['Main Office', 'Warehouse', 'Factory Floor', 'Server Room', 'Workshop', 'Building A', 'Building B', 'Generator Room', 'Electrical Room', 'Control Room']
        
        for i in range(count):
            device = ElectricalDevice(
                name=f"Electrical Device {i+1}",
                model_number=f"ED{random.randint(1000, 9999)}-{i}",
                serial_number=f"SN{random.randint(100000, 999999)}",
                manufacturer=self.generate_company(),
                voltage_rating=f"{random.choice([110, 220, 380, 440, 480, 600])}V",
                power_rating=f"{random.randint(100, 10000)}W",
                location=random.choice(locations),
                status=random.choice(statuses),
                priority=random.choice(priorities),
                purchase_date=self.generate_random_date(1825, 0),
                warranty_expiry=self.generate_random_date(-30, -730),
                last_maintenance=self.generate_random_date(365, 0),
                next_maintenance=self.generate_random_date(-30, -180),
                maintenance_cost=Decimal(str(random.randint(100, 10000))),
                description=self.generate_text(15),
                created_by=user,
            )
            devices_to_create.append(device)
            
            if len(devices_to_create) >= batch_size:
                ElectricalDevice.objects.bulk_create(devices_to_create)
                devices_to_create = []
                self.stdout.write(f'Created {i + 1} electrical devices...')
        
        if devices_to_create:
            ElectricalDevice.objects.bulk_create(devices_to_create)
        
        self.stdout.write(f'Created {count} electrical devices total')

    def create_electronics_devices_bulk(self, count, user, batch_size):
        """Create electronics devices using bulk operations"""
        devices_to_create = []
        statuses = ['working', 'maintenance', 'repair', 'damaged', 'retired']
        priorities = ['low', 'medium', 'high', 'critical']
        device_types = ['computer', 'printer', 'scanner', 'router', 'switch', 'phone', 'tablet', 'monitor', 'projector', 'other']
        locations = ['Main Office', 'IT Department', 'Reception', 'Conference Room', 'Finance Dept', 'HR Department', 'Sales Office', 'Marketing', 'Operations', 'Security']
        operating_systems = ['Windows 11', 'Windows 10', 'macOS', 'Linux', 'Android', 'iOS', 'N/A', 'Embedded', 'FreeBSD']
        
        for i in range(count):
            device = ElectronicsDevice(
                name=f"Electronics Device {i+1}",
                device_type=random.choice(device_types),
                model_number=f"EL{random.randint(1000, 9999)}-{i}",
                serial_number=f"SN{random.randint(100000, 999999)}",
                manufacturer=self.generate_company(),
                operating_system=random.choice(operating_systems),
                specifications=self.generate_text(10),
                location=random.choice(locations),
                status=random.choice(statuses),
                priority=random.choice(priorities),
                purchase_date=self.generate_random_date(1825, 0),
                warranty_expiry=self.generate_random_date(-30, -1095),
                last_maintenance=self.generate_random_date(365, 0),
                next_maintenance=self.generate_random_date(-30, -365),
                maintenance_cost=Decimal(str(random.randint(50, 5000))),
                description=self.generate_text(15),
                assigned_to=self.generate_name(),
                created_by=user,
            )
            devices_to_create.append(device)
            
            if len(devices_to_create) >= batch_size:
                ElectronicsDevice.objects.bulk_create(devices_to_create)
                devices_to_create = []
                self.stdout.write(f'Created {i + 1} electronics devices...')
        
        if devices_to_create:
            ElectronicsDevice.objects.bulk_create(devices_to_create)
        
        self.stdout.write(f'Created {count} electronics devices total')

    def create_debts_bulk(self, credit_sales, batch_size):
        """Create debts for credit sales using bulk operations"""
        debts = []
        debts_to_create = []
        statuses = ['outstanding', 'partial', 'paid', 'overdue']
        
        for sale in credit_sales:
            if sale.customer:  # Only create debt if customer exists
                debt = Debt(
                    customer=sale.customer,
                    sale=sale,
                    amount=sale.net_amount,
                    due_date=self.generate_random_date(-30, -90),
                    status=random.choice(statuses),
                    interest_rate=Decimal(str(random.uniform(0, 8))),
                    notes=self.generate_text(10) if random.choice([True, False]) else '',
                )
                debts_to_create.append(debt)
                
                if len(debts_to_create) >= batch_size:
                    created_debts = Debt.objects.bulk_create(debts_to_create)
                    debts.extend(created_debts)
                    debts_to_create = []
                    self.stdout.write(f'Created {len(debts)} debts...')
        
        if debts_to_create:
            created_debts = Debt.objects.bulk_create(debts_to_create)
            debts.extend(created_debts)
        
        self.stdout.write(f'Created {len(debts)} debts total')
        return debts

    def create_debt_payments_bulk(self, debts, user, batch_size):
        """Create debt payments using bulk operations"""
        payments_to_create = []
        payment_methods = ['cash', 'bank_transfer', 'mobile_money', 'cheque', 'card']
        total_payments = 0
        
        for debt in debts:
            if debt.status in ['partial', 'paid']:
                num_payments = random.randint(1, 6)
                remaining_amount = debt.amount
                
                for i in range(num_payments):
                    if remaining_amount <= 0:
                        break
                    
                    if i == num_payments - 1 and debt.status == 'paid':
                        # Last payment for paid debt
                        payment_amount = remaining_amount
                    else:
                        # Partial payment
                        payment_amount = Decimal(str(random.uniform(float(remaining_amount * Decimal('0.1')), float(remaining_amount * Decimal('0.9')))))
                    
                    payment = DebtPayment(
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
                    payments_to_create.append(payment)
                    remaining_amount -= payment_amount
                    
                    if len(payments_to_create) >= batch_size:
                        DebtPayment.objects.bulk_create(payments_to_create)
                        total_payments += len(payments_to_create)
                        payments_to_create = []
                        self.stdout.write(f'Created {total_payments} debt payments...')
        
        if payments_to_create:
            DebtPayment.objects.bulk_create(payments_to_create)
            total_payments += len(payments_to_create)
        
        self.stdout.write(f'Created {total_payments} debt payments total')

    def create_notifications_bulk(self, count, user, batch_size):
        """Create notifications using bulk operations"""
        notifications_to_create = []
        notification_types = ['info', 'warning', 'success', 'error']
        
        for i in range(count):
            notification = Notification(
                user=user,
                title=self.generate_text(4),
                message=self.generate_text(20),
                notification_type=random.choice(notification_types),
                is_read=random.choice([True, False]),
            )
            notifications_to_create.append(notification)
            
            if len(notifications_to_create) >= batch_size:
                Notification.objects.bulk_create(notifications_to_create)
                notifications_to_create = []
                self.stdout.write(f'Created {i + 1} notifications...')
        
        if notifications_to_create:
            Notification.objects.bulk_create(notifications_to_create)
        
        self.stdout.write(f'Created {count} notifications total')
