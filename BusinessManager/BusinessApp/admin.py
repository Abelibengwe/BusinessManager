from django.contrib import admin
from .models import (
    Category, Supplier, Product, Customer, Sale, SaleItem,
    ExpenseCategory, Expense, Project, StockMovement, Notification,
    Debt, DebtPayment
)

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'created_at']
    search_fields = ['name', 'email']
    ordering = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'selling_price', 'stock_quantity', 'is_active']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'sku', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'credit_limit', 'is_credit_approved', 'current_debt', 'created_at']
    list_filter = ['is_credit_approved', 'created_at']
    search_fields = ['name', 'email', 'phone', 'national_id']
    ordering = ['name']
    readonly_fields = ['current_debt', 'available_credit']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'phone', 'address', 'national_id')
        }),
        ('Credit Information', {
            'fields': ('credit_limit', 'is_credit_approved', 'current_debt', 'available_credit')
        }),
    )

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'sale_date', 'total_amount', 'payment_method', 'created_by']
    list_filter = ['payment_method', 'sale_date', 'created_at']
    search_fields = ['customer__name', 'notes']
    ordering = ['-created_at']
    inlines = [SaleItemInline]

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'amount', 'expense_date', 'created_by']
    list_filter = ['category', 'expense_date', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['-created_at']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'client', 'status', 'budget', 'progress', 'start_date', 'end_date']
    list_filter = ['status', 'start_date', 'end_date']
    search_fields = ['name', 'client', 'description']
    ordering = ['-created_at']

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'reason', 'created_by', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['product__name', 'reason']
    ordering = ['-created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    ordering = ['-created_at']

class DebtPaymentInline(admin.TabularInline):
    model = DebtPayment
    extra = 0
    readonly_fields = ['created_at']

@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ['customer', 'amount', 'remaining_balance', 'due_date', 'status', 'is_overdue', 'days_overdue']
    list_filter = ['status', 'due_date', 'created_at']
    search_fields = ['customer__name', 'sale__id']
    ordering = ['-created_at']
    readonly_fields = ['amount_paid', 'remaining_balance', 'is_overdue', 'days_overdue']
    inlines = [DebtPaymentInline]
    
    fieldsets = (
        ('Debt Information', {
            'fields': ('customer', 'sale', 'amount', 'due_date', 'status')
        }),
        ('Additional Details', {
            'fields': ('interest_rate', 'notes', 'amount_paid', 'remaining_balance', 'is_overdue', 'days_overdue')
        }),
    )

@admin.register(DebtPayment)
class DebtPaymentAdmin(admin.ModelAdmin):
    list_display = ['debt', 'amount_paid', 'payment_method', 'payment_date', 'recorded_by']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['debt__customer__name', 'reference_number']
    ordering = ['-payment_date']
