from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True)
    sku = models.CharField(max_length=50, unique=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    min_stock_level = models.PositiveIntegerField(default=10)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def profit_margin(self):
        if self.cost_price:
            return ((self.selling_price - self.cost_price) / self.cost_price) * 100
        return 0
    
    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.min_stock_level

class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    national_id = models.CharField(max_length=50, blank=True, help_text="National ID or passport number")
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Maximum debt allowed")
    is_credit_approved = models.BooleanField(default=False, help_text="Can this customer buy on credit?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def current_debt(self):
        """Calculate current outstanding debt"""
        from django.db.models import Sum
        debts = self.debts.filter(status__in=['outstanding', 'partial', 'overdue'])
        total_debt = Decimal('0')
        for debt in debts:
            total_debt += debt.remaining_balance
        return total_debt
    
    @property
    def available_credit(self):
        """Calculate available credit limit"""
        return self.credit_limit - self.current_debt
    
    def can_buy_on_credit(self, amount=Decimal('0')):
        """Check if customer can buy on credit for a specific amount"""
        if not self.is_credit_approved:
            return False
        return (self.current_debt + amount) <= self.credit_limit

class Sale(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('credit', 'Credit/Debt'),
    ]
    
    SALE_TYPE_CHOICES = [
        ('cash', 'Cash Sale'),
        ('credit', 'Credit Sale'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    sale_date = models.DateTimeField(default=timezone.now)
    sale_type = models.CharField(max_length=10, choices=SALE_TYPE_CHOICES, default='cash')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Sale #{self.id} - {self.sale_date.strftime('%Y-%m-%d')}"
    
    @property
    def net_amount(self):
        return self.total_amount - self.discount + self.tax
    
    @property
    def is_credit_sale(self):
        return self.sale_type == 'credit'

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Expense Categories"
    
    def __str__(self):
        return self.name

class Expense(models.Model):
    title = models.CharField(max_length=200, default='General Expense')
    description = models.TextField(blank=True)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField(default=timezone.now)
    receipt_image = models.ImageField(upload_to='receipts/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - ${self.amount}"

class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    client = models.CharField(max_length=200, default='Unknown Client')
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    spent_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    progress = models.PositiveIntegerField(default=0, help_text="Progress percentage (0-100)")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    @property
    def remaining_budget(self):
        return self.budget - self.spent_amount
    
    @property
    def is_over_budget(self):
        return self.spent_amount > self.budget

class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Adjustment'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    reason = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.movement_type} - {self.quantity}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('error', 'Error'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']

class ElectricalDevice(models.Model):
    STATUS_CHOICES = [
        ('working', 'Working'),
        ('maintenance', 'Under Maintenance'),
        ('repair', 'Needs Repair'),
        ('damaged', 'Damaged'),
        ('retired', 'Retired'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    name = models.CharField(max_length=200)
    model_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    voltage_rating = models.CharField(max_length=50, blank=True)
    power_rating = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=200, default='Main Office')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='working')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    purchase_date = models.DateField(null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    last_maintenance = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    maintenance_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.model_number}"
    
    @property
    def is_due_maintenance(self):
        if self.next_maintenance:
            return timezone.now().date() >= self.next_maintenance
        return False

class ElectronicsDevice(models.Model):
    STATUS_CHOICES = [
        ('working', 'Working'),
        ('maintenance', 'Under Maintenance'),
        ('repair', 'Needs Repair'),
        ('damaged', 'Damaged'),
        ('retired', 'Retired'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    DEVICE_TYPES = [
        ('computer', 'Computer'),
        ('printer', 'Printer'),
        ('scanner', 'Scanner'),
        ('router', 'Router'),
        ('switch', 'Switch'),
        ('phone', 'Phone'),
        ('tablet', 'Tablet'),
        ('monitor', 'Monitor'),
        ('projector', 'Projector'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES, default='other')
    model_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    operating_system = models.CharField(max_length=100, blank=True)
    specifications = models.TextField(blank=True)
    location = models.CharField(max_length=200, default='Main Office')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='working')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    purchase_date = models.DateField(null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    last_maintenance = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    maintenance_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    assigned_to = models.CharField(max_length=200, blank=True, help_text="Person or department assigned to")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.device_type}"
    
    @property
    def is_due_maintenance(self):
        if self.next_maintenance:
            return timezone.now().date() >= self.next_maintenance
        return False

class Debt(models.Model):
    DEBT_STATUS_CHOICES = [
        ('outstanding', 'Outstanding'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
        ('overdue', 'Overdue'),
        ('written_off', 'Written Off'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='debts')
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE, related_name='debt')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Original debt amount")
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=DEBT_STATUS_CHOICES, default='outstanding')
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Monthly interest rate %")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.customer.name} - TSh {self.remaining_balance}"
    
    @property
    def total_amount(self):
        """Total debt amount (alias for amount)"""
        return self.amount
    
    @property
    def amount_paid(self):
        """Calculate total amount paid from payments"""
        from django.db.models import Sum
        total_paid = self.payments.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0')
        return total_paid
    
    @property
    def remaining_balance(self):
        """Calculate remaining balance"""
        return self.amount - self.amount_paid
    
    @property
    def is_overdue(self):
        """Check if debt is overdue"""
        if self.due_date:
            return timezone.now().date() > self.due_date and self.remaining_balance > 0
        return False
    
    @property
    def days_overdue(self):
        """Calculate days overdue"""
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0
    
    def update_status(self):
        """Update debt status based on remaining amount and due date"""
        remaining = self.remaining_balance
        if remaining <= 0:
            self.status = 'paid'
        elif remaining < self.amount:
            if self.is_overdue:
                self.status = 'overdue'
            else:
                self.status = 'partial'
        elif self.is_overdue:
            self.status = 'overdue'
        else:
            self.status = 'outstanding'
        self.save()

class DebtPayment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('cheque', 'Cheque'),
        ('card', 'Card Payment'),
    ]
    
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    reference_number = models.CharField(max_length=100, blank=True, help_text="Transaction reference")
    payment_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.debt.customer.name} - TSh {self.amount_paid} on {self.payment_date.date()}"
    
    @property
    def remaining_balance_after(self):
        """Calculate remaining balance after this payment"""
        return self.debt.remaining_balance
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update debt status after payment
        self.debt.update_status()
