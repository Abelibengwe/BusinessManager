from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import (
    Product, Sale, SaleItem, Expense, Project, 
    StockMovement, Notification, Category, 
    ExpenseCategory, Customer, Supplier,
    ElectricalDevice, ElectronicsDevice
)

# Create your views here.

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    # Get current date and time periods
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    sixty_days_ago = today - timedelta(days=60)
    
    # Basic statistics
    total_products = Product.objects.filter(is_active=True).count()
    total_sales = Sale.objects.filter(sale_date__date__gte=thirty_days_ago).count()
    
    # Calculate revenue using net_amount (total_amount - discount + tax)
    # This month's revenue
    sales_data = Sale.objects.filter(sale_date__date__gte=thirty_days_ago)
    total_revenue = 0
    total_cogs = 0  # Cost of Goods Sold
    
    for sale in sales_data:
        total_revenue += sale.net_amount
        # Calculate COGS for this sale
        sale_items = SaleItem.objects.filter(sale=sale).select_related('product')
        for item in sale_items:
            total_cogs += (item.product.cost_price * item.quantity)
    
    # Last month's revenue and COGS for comparison
    last_month_sales = Sale.objects.filter(
        sale_date__date__gte=sixty_days_ago,
        sale_date__date__lt=thirty_days_ago
    )
    last_month_revenue = 0
    last_month_cogs = 0
    
    for sale in last_month_sales:
        last_month_revenue += sale.net_amount
        # Calculate COGS for last month
        sale_items = SaleItem.objects.filter(sale=sale).select_related('product')
        for item in sale_items:
            last_month_cogs += (item.product.cost_price * item.quantity)
    
    # Today's revenue and COGS
    today_sales = Sale.objects.filter(sale_date__date=today)
    today_revenue = 0
    today_cogs = 0
    
    for sale in today_sales:
        today_revenue += sale.net_amount
        # Calculate today's COGS
        sale_items = SaleItem.objects.filter(sale=sale).select_related('product')
        for item in sale_items:
            today_cogs += (item.product.cost_price * item.quantity)
    
    # Calculate total expenses
    total_expenses = Expense.objects.filter(expense_date__gte=thirty_days_ago).aggregate(
        total=Sum('amount'))['total'] or 0
    
    # Last month's expenses for comparison
    last_month_expenses = Expense.objects.filter(
        expense_date__gte=sixty_days_ago,
        expense_date__lt=thirty_days_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate profit (revenue - COGS - operating expenses)
    # Gross Profit = Revenue - COGS
    gross_profit = total_revenue - total_cogs
    last_month_gross_profit = last_month_revenue - last_month_cogs
    
    # Net Profit = Gross Profit - Operating Expenses
    net_profit = gross_profit - total_expenses
    last_month_net_profit = last_month_gross_profit - last_month_expenses
    
    # Today's profit calculations
    today_gross_profit = today_revenue - today_cogs
    
    # Calculate percentage changes
    revenue_change = 0
    profit_change = 0
    gross_profit_change = 0
    
    if last_month_revenue > 0:
        revenue_change = ((total_revenue - last_month_revenue) / last_month_revenue) * 100
    if last_month_net_profit != 0:
        profit_change = ((net_profit - last_month_net_profit) / abs(last_month_net_profit)) * 100
    if last_month_gross_profit > 0:
        gross_profit_change = ((gross_profit - last_month_gross_profit) / last_month_gross_profit) * 100
    
    # Low stock products
    low_stock_products = Product.objects.filter(
        stock_quantity__lte=F('min_stock_level'),
        is_active=True
    )[:5]
    
    # Recent sales
    recent_sales = Sale.objects.select_related('customer').order_by('-created_at')[:5]
    
    # Recent projects
    recent_projects = Project.objects.order_by('-created_at')[:5]
    
    # Create automatic notifications for important alerts
    # Low stock notifications
    low_stock_products = Product.objects.filter(
        stock_quantity__lte=F('min_stock_level'),
        is_active=True
    )
    
    for product in low_stock_products:
        # Check if notification already exists to avoid duplicates (check both read and unread)
        existing_notification = Notification.objects.filter(
            user=request.user,
            title=f"Low Stock Alert: {product.name}",
            created_at__date=timezone.now().date()  # Only check today's notifications
        ).first()
        
        if not existing_notification:
            Notification.objects.create(
                user=request.user,
                title=f"Low Stock Alert: {product.name}",
                message=f"{product.name} is low in stock ({product.stock_quantity} remaining). Minimum level is {product.min_stock_level}. Please restock soon.",
                notification_type='warning'
            )
    
    # Electrical devices maintenance notifications
    electrical_maintenance_due = ElectricalDevice.objects.filter(
        next_maintenance__lte=timezone.now().date(),
        status='working'
    )
    
    for device in electrical_maintenance_due:
        existing_notification = Notification.objects.filter(
            user=request.user,
            title=f"Maintenance Due: {device.name}",
            created_at__date=timezone.now().date()  # Only check today's notifications
        ).first()
        
        if not existing_notification:
            Notification.objects.create(
                user=request.user,
                title=f"Maintenance Due: {device.name}",
                message=f"Electrical device '{device.name}' requires maintenance. Due date: {device.next_maintenance}",
                notification_type='warning'
            )
    
    # Electronics devices maintenance notifications
    electronics_maintenance_due = ElectronicsDevice.objects.filter(
        next_maintenance__lte=timezone.now().date(),
        status='working'
    )
    
    for device in electronics_maintenance_due:
        existing_notification = Notification.objects.filter(
            user=request.user,
            title=f"Electronics Maintenance Due: {device.name}",
            created_at__date=timezone.now().date()  # Only check today's notifications
        ).first()
        
        if not existing_notification:
            Notification.objects.create(
                user=request.user,
                title=f"Electronics Maintenance Due: {device.name}",
                message=f"Electronics device '{device.name}' requires maintenance. Due date: {device.next_maintenance}",
                notification_type='warning'
            )
    
    # Critical device alerts
    critical_electrical = ElectricalDevice.objects.filter(
        priority='critical',
        status__in=['maintenance', 'repair', 'faulty']
    )
    
    for device in critical_electrical:
        existing_notification = Notification.objects.filter(
            user=request.user,
            title=f"Critical Device Alert: {device.name}",
            created_at__date=timezone.now().date()  # Only check today's notifications
        ).first()
        
        if not existing_notification:
            Notification.objects.create(
                user=request.user,
                title=f"Critical Device Alert: {device.name}",
                message=f"Critical electrical device '{device.name}' is {device.status}. Immediate attention required!",
                notification_type='error'
            )
    
    critical_electronics = ElectronicsDevice.objects.filter(
        priority='critical',
        status__in=['maintenance', 'repair', 'faulty']
    )
    
    for device in critical_electronics:
        existing_notification = Notification.objects.filter(
            user=request.user,
            title=f"Critical Electronics Alert: {device.name}",
            created_at__date=timezone.now().date()  # Only check today's notifications
        ).first()
        
        if not existing_notification:
            Notification.objects.create(
                user=request.user,
                title=f"Critical Electronics Alert: {device.name}",
                message=f"Critical electronics device '{device.name}' is {device.status}. Immediate attention required!",
                notification_type='error'
            )
    
    # Project deadline notifications (projects ending within 7 days)
    upcoming_deadline = timezone.now().date() + timedelta(days=7)
    projects_deadline = Project.objects.filter(
        end_date__lte=upcoming_deadline,
        end_date__gte=today,
        status='in_progress'
    )
    
    for project in projects_deadline:
        existing_notification = Notification.objects.filter(
            user=request.user,
            title=f"Project Deadline Approaching: {project.name}",
            created_at__date=timezone.now().date()  # Only check today's notifications
        ).first()
        
        if not existing_notification:
            days_remaining = (project.end_date - today).days
            Notification.objects.create(
                user=request.user,
                title=f"Project Deadline Approaching: {project.name}",
                message=f"Project '{project.name}' for {project.client} is due in {days_remaining} days ({project.end_date})",
                notification_type='info'
            )
    
    # High expense alerts (expenses above a threshold in the last 7 days)
    week_ago = today - timedelta(days=7)
    high_expenses = Expense.objects.filter(
        expense_date__gte=week_ago,
        amount__gte=1000  # Threshold for high expenses
    )
    
    for expense in high_expenses:
        existing_notification = Notification.objects.filter(
            user=request.user,
            title=f"High Expense Alert: {expense.title}",
            created_at__date=timezone.now().date()  # Only check today's notifications
        ).first()
        
        if not existing_notification:
            Notification.objects.create(
                user=request.user,
                title=f"High Expense Alert: {expense.title}",
                message=f"Large expense recorded: {expense.title} - ${expense.amount} on {expense.expense_date}",
                notification_type='warning'
            )
    
    # Calculate profit margins
    gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
    net_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    cogs_percentage = (total_cogs / total_revenue * 100) if total_revenue > 0 else 0
    
    # Services statistics for electrical and electronics devices
    total_electrical_devices = ElectricalDevice.objects.count()
    total_electronics_devices = ElectronicsDevice.objects.count()
    total_services_devices = total_electrical_devices + total_electronics_devices
    
    # Working devices
    working_electrical = ElectricalDevice.objects.filter(status='working').count()
    working_electronics = ElectronicsDevice.objects.filter(status='working').count()
    total_working_devices = working_electrical + working_electronics
    
    # Devices in maintenance or repair
    maintenance_electrical = ElectricalDevice.objects.filter(status__in=['maintenance', 'repair']).count()
    maintenance_electronics = ElectronicsDevice.objects.filter(status__in=['maintenance', 'repair']).count()
    total_maintenance_devices = maintenance_electrical + maintenance_electronics
    
    # Critical devices
    critical_electrical = ElectricalDevice.objects.filter(priority='critical').count()
    critical_electronics = ElectronicsDevice.objects.filter(priority='critical').count()
    total_critical_devices = critical_electrical + critical_electronics
    
    # Devices due for maintenance (next_maintenance <= today)
    due_electrical = ElectricalDevice.objects.filter(
        next_maintenance__lte=today,
        status='working'
    ).count()
    due_electronics = ElectronicsDevice.objects.filter(
        next_maintenance__lte=today,
        status='working'
    ).count()
    total_due_maintenance = due_electrical + due_electronics
    
    # Calculate separate maintenance costs for electrical and electronics
    electrical_maintenance_cost = ElectricalDevice.objects.filter(
        status__in=['maintenance', 'repair']
    ).aggregate(total=Sum('maintenance_cost'))['total'] or 0
    
    electronics_maintenance_cost = ElectronicsDevice.objects.filter(
        status__in=['maintenance', 'repair']
    ).aggregate(total=Sum('maintenance_cost'))['total'] or 0
    
    total_maintenance_cost = electrical_maintenance_cost + electronics_maintenance_cost
    
    # Calculate project budget (active projects)
    active_projects_budget = Project.objects.filter(
        status__in=['planning', 'in_progress']
    ).aggregate(total=Sum('budget'))['total'] or 0
    
    # Calculate total active projects count
    total_active_projects = Project.objects.filter(
        status__in=['planning', 'in_progress']
    ).count()
    
    # Services uptime percentage
    services_uptime = (total_working_devices / total_services_devices * 100) if total_services_devices > 0 else 100
    
    # Check if user has admin access for sensitive data
    is_staff_user = request.user.is_staff
    admin_verified = request.session.get('admin_verified', False) if not is_staff_user else True
    
    context = {
        'total_products': total_products,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'total_expenses': total_expenses,
        'total_cogs': total_cogs,
        'gross_profit': gross_profit,
        'net_profit': net_profit,
        'profit': net_profit,  # Keep for backward compatibility
        'gross_margin': gross_margin,
        'net_margin': net_margin,
        'cogs_percentage': cogs_percentage,
        'revenue_change': revenue_change,
        'profit_change': profit_change,
        'gross_profit_change': gross_profit_change,
        'low_stock_products': low_stock_products,
        'recent_sales': recent_sales,
        'recent_projects': recent_projects,
        # Services statistics
        'total_services_devices': total_services_devices,
        'total_electrical_devices': total_electrical_devices,
        'total_electronics_devices': total_electronics_devices,
        'total_working_devices': total_working_devices,
        'total_maintenance_devices': total_maintenance_devices,
        'total_critical_devices': total_critical_devices,
        'total_due_maintenance': total_due_maintenance,
        'total_maintenance_cost': total_maintenance_cost,
        'electrical_maintenance_cost': electrical_maintenance_cost,
        'electronics_maintenance_cost': electronics_maintenance_cost,
        'active_projects_budget': active_projects_budget,
        'total_active_projects': total_active_projects,
        'services_uptime': services_uptime,
        # Admin access control
        'is_staff_user': is_staff_user,
        'admin_verified': admin_verified,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def product_list(request):
    products = Product.objects.filter(is_active=True).select_related('category', 'supplier')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    return render(request, 'products/list.html', {'products': products})

@login_required
def product_add(request):
    if request.method == 'POST':
        try:
            # Get or create category
            category_name = request.POST.get('category')
            category, created = Category.objects.get_or_create(name=category_name)
            
            # Get or create supplier if provided
            supplier = None
            supplier_name = request.POST.get('supplier')
            if supplier_name:
                supplier, created = Supplier.objects.get_or_create(name=supplier_name)
            
            product = Product.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description', ''),
                category=category,
                supplier=supplier,
                sku=request.POST.get('sku'),
                cost_price=Decimal(request.POST.get('cost_price')),
                selling_price=Decimal(request.POST.get('selling_price')),
                stock_quantity=int(request.POST.get('stock_quantity', 0)),
                min_stock_level=int(request.POST.get('min_stock_level', 10)),
            )
            
            messages.success(request, f'Product "{product.name}" added successfully!')
            return redirect('product_list')
            
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
    
    categories = Category.objects.all()
    suppliers = Supplier.objects.all()
    return render(request, 'products/add.html', {
        'categories': categories,
        'suppliers': suppliers
    })

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        try:
            # Get or create category
            category_name = request.POST.get('category')
            category, created = Category.objects.get_or_create(name=category_name)
            
            # Get or create supplier if provided
            supplier = None
            supplier_name = request.POST.get('supplier')
            if supplier_name:
                supplier, created = Supplier.objects.get_or_create(name=supplier_name)
            
            product.name = request.POST.get('name')
            product.description = request.POST.get('description', '')
            product.category = category
            product.supplier = supplier
            product.sku = request.POST.get('sku')
            product.cost_price = Decimal(request.POST.get('cost_price'))
            product.selling_price = Decimal(request.POST.get('selling_price'))
            product.stock_quantity = int(request.POST.get('stock_quantity', 0))
            product.min_stock_level = int(request.POST.get('min_stock_level', 10))
            product.save()
            
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('product_list')
            
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
    
    categories = Category.objects.all()
    suppliers = Supplier.objects.all()
    return render(request, 'products/edit.html', {
        'product': product,
        'categories': categories,
        'suppliers': suppliers
    })

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product.is_active = False
        product.save()
        messages.success(request, f'Product "{product.name}" deleted successfully!')
        return redirect('product_list')
    
    return render(request, 'products/delete.html', {'product': product})

@login_required
def sale_list(request):
    from django.db.models import Sum, Count
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    sales = Sale.objects.select_related('customer', 'created_by').order_by('-created_at')
    
    # Calculate statistics
    now = timezone.now()
    today = now.date()
    current_month_start = today.replace(day=1)
    
    # Today's revenue
    today_revenue = Sale.objects.filter(
        sale_date__date=today
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # This month's revenue
    month_revenue = Sale.objects.filter(
        sale_date__date__gte=current_month_start
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Total sales count
    total_sales = sales.count()
    
    # Pending orders (assuming we might add status field later, for now show 0)
    pending_orders = 0
    
    # Pagination
    paginator = Paginator(sales, 20)
    page_number = request.GET.get('page')
    sales_page = paginator.get_page(page_number)
    
    context = {
        'sales': sales_page,
        'today_revenue': today_revenue,
        'month_revenue': month_revenue,
        'total_sales': total_sales,
        'pending_orders': pending_orders,
    }
    
    return render(request, 'sales/list.html', context)

@login_required
def sale_add(request):
    if request.method == 'POST':
        try:
            # Get or create customer if provided
            customer = None
            customer_name = request.POST.get('customer_name')
            if customer_name:
                customer, created = Customer.objects.get_or_create(
                    name=customer_name,
                    defaults={
                        'email': request.POST.get('customer_email', ''),
                        'phone': request.POST.get('customer_phone', ''),
                    }
                )
            
            # Create sale
            sale = Sale.objects.create(
                customer=customer,
                payment_method=request.POST.get('payment_method', 'cash'),
                total_amount=Decimal(request.POST.get('total_amount')),
                discount=Decimal(request.POST.get('discount', 0)),
                tax=Decimal(request.POST.get('tax', 0)),
                notes=request.POST.get('notes', ''),
                created_by=request.user
            )
            
            # Add sale items
            products_data = json.loads(request.POST.get('products', '[]'))
            for item_data in products_data:
                product = Product.objects.get(id=item_data['product_id'])
                quantity = int(item_data['quantity'])
                unit_price = Decimal(item_data['unit_price'])
                
                # Create sale item
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price
                )
                
                # Update product stock
                product.stock_quantity -= quantity
                product.save()
                
                # Create stock movement record
                StockMovement.objects.create(
                    product=product,
                    movement_type='out',
                    quantity=-quantity,
                    reason=f'Sale #{sale.id}',
                    created_by=request.user
                )
            
            messages.success(request, f'Sale #{sale.id} created successfully!')
            return redirect('sale_list')
            
        except Exception as e:
            messages.error(request, f'Error creating sale: {str(e)}')
    
    products = Product.objects.filter(is_active=True, stock_quantity__gt=0)
    return render(request, 'sales/add.html', {'products': products})

@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    sale_items = SaleItem.objects.filter(sale=sale).select_related('product')
    
    return render(request, 'sales/detail.html', {
        'sale': sale,
        'sale_items': sale_items
    })

@login_required
def expense_list(request):
    expenses = Expense.objects.select_related('category', 'created_by').order_by('-created_at')
    
    # Calculate statistics
    now = timezone.now()
    today = now.date()
    current_month_start = today.replace(day=1)
    current_year_start = today.replace(month=1, day=1)
    
    # Today's expenses
    today_expenses = Expense.objects.filter(
        expense_date=today
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # This month's expenses
    month_expenses = Expense.objects.filter(
        expense_date__gte=current_month_start
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # This year's expenses
    year_expenses = Expense.objects.filter(
        expense_date__gte=current_year_start
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Total expense count
    total_expenses_count = expenses.count()
    
    # Expenses by category (top 5)
    category_expenses = Expense.objects.filter(
        expense_date__gte=current_month_start
    ).values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')[:5]
    
    # Pagination
    paginator = Paginator(expenses, 20)
    page_number = request.GET.get('page')
    expenses_page = paginator.get_page(page_number)
    
    context = {
        'expenses': expenses_page,
        'today_expenses': today_expenses,
        'month_expenses': month_expenses,
        'year_expenses': year_expenses,
        'total_expenses_count': total_expenses_count,
        'category_expenses': category_expenses,
    }
    
    return render(request, 'expenses/list.html', context)

@login_required
def expense_add(request):
    if request.method == 'POST':
        try:
            # Get or create category
            category_name = request.POST.get('category')
            category, created = ExpenseCategory.objects.get_or_create(name=category_name)
            
            expense = Expense.objects.create(
                title=request.POST.get('title'),
                description=request.POST.get('description', ''),
                category=category,
                amount=Decimal(request.POST.get('amount')),
                expense_date=request.POST.get('expense_date'),
                created_by=request.user
            )
            
            messages.success(request, f'Expense "{expense.title}" added successfully!')
            return redirect('expense_list')
            
        except Exception as e:
            messages.error(request, f'Error adding expense: {str(e)}')
    
    categories = ExpenseCategory.objects.all()
    today = timezone.now().date()
    return render(request, 'expenses/add.html', {
        'categories': categories,
        'today': today
    })

@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    
    if request.method == 'POST':
        try:
            category_name = request.POST.get('category')
            category, created = ExpenseCategory.objects.get_or_create(name=category_name)
            
            expense.title = request.POST.get('title')
            expense.description = request.POST.get('description', '')
            expense.category = category
            expense.amount = Decimal(request.POST.get('amount'))
            expense.expense_date = request.POST.get('expense_date')
            expense.save()
            
            messages.success(request, f'Expense "{expense.title}" updated successfully!')
            return redirect('expense_list')
            
        except Exception as e:
            messages.error(request, f'Error updating expense: {str(e)}')
    
    categories = ExpenseCategory.objects.all()
    return render(request, 'expenses/edit.html', {
        'expense': expense,
        'categories': categories
    })

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    
    if request.method == 'POST':
        expense.delete()
        messages.success(request, f'Expense "{expense.title}" deleted successfully!')
        return redirect('expense_list')
    
    return render(request, 'expenses/delete.html', {'expense': expense})

@login_required
def project_list(request):
    projects = Project.objects.select_related('created_by').order_by('-created_at')
    
    # Search and filter functionality
    search_query = request.GET.get('search')
    status_filter = request.GET.get('status')
    sort_by = request.GET.get('sort', 'name')
    
    if search_query:
        projects = projects.filter(
            Q(name__icontains=search_query) |
            Q(client__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if status_filter:
        projects = projects.filter(status=status_filter)
    
    # Sorting
    if sort_by == 'client':
        projects = projects.order_by('client')
    elif sort_by == 'start_date':
        projects = projects.order_by('-start_date')
    elif sort_by == 'budget':
        projects = projects.order_by('-budget')
    elif sort_by == 'progress':
        projects = projects.order_by('-progress')
    else:  # default to name
        projects = projects.order_by('name')
    
    # Calculate statistics
    all_projects = Project.objects.all()
    stats = {
        'total_projects': all_projects.count(),
        'planning_projects': all_projects.filter(status='planning').count(),
        'in_progress_projects': all_projects.filter(status='in_progress').count(),
        'completed_projects': all_projects.filter(status='completed').count(),
        'on_hold_projects': all_projects.filter(status='on_hold').count(),
        'total_budget': all_projects.aggregate(total=Sum('budget'))['total'] or 0,
    }
    
    # Pagination
    paginator = Paginator(projects, 20)
    page_number = request.GET.get('page')
    projects_page = paginator.get_page(page_number)
    
    return render(request, 'projects/list.html', {
        'projects': projects_page,
        'stats': stats
    })

@login_required
def project_add(request):
    if request.method == 'POST':
        try:
            project = Project.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description'),
                client=request.POST.get('client'),
                budget=Decimal(request.POST.get('budget')),
                start_date=request.POST.get('start_date'),
                end_date=request.POST.get('end_date'),
                status=request.POST.get('status', 'planning'),
                progress=int(request.POST.get('progress', 0)),
                created_by=request.user
            )
            
            messages.success(request, f'Project "{project.name}" added successfully!')
            return redirect('project_list')
            
        except Exception as e:
            messages.error(request, f'Error adding project: {str(e)}')
    
    return render(request, 'projects/add.html')

@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        try:
            project.name = request.POST.get('name')
            project.description = request.POST.get('description')
            project.client = request.POST.get('client')
            project.budget = Decimal(request.POST.get('budget'))
            project.start_date = request.POST.get('start_date')
            project.end_date = request.POST.get('end_date')
            project.status = request.POST.get('status', 'planning')
            project.progress = int(request.POST.get('progress', 0))
            project.save()
            
            messages.success(request, f'Project "{project.name}" updated successfully!')
            return redirect('project_list')
            
        except Exception as e:
            messages.error(request, f'Error updating project: {str(e)}')
    
    return render(request, 'projects/edit.html', {'project': project})

@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, f'Project "{project.name}" deleted successfully!')
        return redirect('project_list')
    
    return render(request, 'projects/delete.html', {'project': project})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Calculate project metrics
    days_elapsed = 0
    days_remaining = 0
    project_duration = 0
    
    if project.start_date:
        start_date = project.start_date
        current_date = timezone.now().date()
        days_elapsed = (current_date - start_date).days
        
        if project.end_date:
            project_duration = (project.end_date - start_date).days
            days_remaining = (project.end_date - current_date).days
        
    # Calculate budget utilization
    budget_utilization = 0
    if project.budget > 0:
        budget_utilization = (project.spent_amount / project.budget) * 100
    
    # Determine project health based on progress vs budget utilization
    project_health = 'good'
    if budget_utilization > project.progress + 20:
        project_health = 'over_budget'
    elif project.progress < 50 and days_elapsed > project_duration * 0.6:
        project_health = 'behind_schedule'
    elif budget_utilization > 90 and project.progress < 90:
        project_health = 'warning'
    
    # Get related expenses (if any)
    related_expenses = Expense.objects.filter(
        description__icontains=project.name
    ).order_by('-expense_date')[:5]
    
    # Get recent stock movements related to this project (if any)
    project_stock_movements = StockMovement.objects.filter(
        reason__icontains=project.name
    ).select_related('product').order_by('-created_at')[:5]
    
    context = {
        'project': project,
        'days_elapsed': max(0, days_elapsed),
        'days_remaining': days_remaining,
        'project_duration': project_duration,
        'budget_utilization': round(budget_utilization, 1),
        'project_health': project_health,
        'related_expenses': related_expenses,
        'project_stock_movements': project_stock_movements,
    }
    
    return render(request, 'projects/detail.html', context)

@login_required
def stock_in_list(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    
    # Calculate stock values for each product
    products_with_values = []
    for product in products:
        product.stock_value = product.stock_quantity * product.cost_price
        products_with_values.append(product)
    
    stock_movements = StockMovement.objects.select_related('product', 'created_by').order_by('-created_at')[:20]
    
    # Calculate absolute quantity for each movement
    movements_with_abs = []
    for movement in stock_movements:
        movement.abs_quantity = abs(movement.quantity)
        movements_with_abs.append(movement)
    
    return render(request, 'stock/list.html', {
        'products': products_with_values,
        'stock_movements': movements_with_abs
    })

@login_required
def stock_movement(request):
    if request.method == 'POST':
        try:
            product = Product.objects.get(id=request.POST.get('product_id'))
            movement_type = request.POST.get('movement_type')
            quantity = int(request.POST.get('quantity'))
            reason = request.POST.get('reason')
            
            # Create stock movement
            StockMovement.objects.create(
                product=product,
                movement_type=movement_type,
                quantity=quantity if movement_type == 'in' else -quantity,
                reason=reason,
                created_by=request.user
            )
            
            # Update product stock
            if movement_type == 'in':
                product.stock_quantity += quantity
            elif movement_type == 'out':
                product.stock_quantity = max(0, product.stock_quantity - quantity)
            elif movement_type == 'adjustment':
                product.stock_quantity = quantity
            
            product.save()
            
            messages.success(request, f'Stock movement for "{product.name}" recorded successfully!')
            return redirect('stock_in_list')
            
        except Exception as e:
            messages.error(request, f'Error recording stock movement: {str(e)}')
    
    return redirect('stock_in_list')

@login_required
def reports(request):
    # Date range (last 30 days by default, but can be customized)
    today = timezone.now().date()
    days_back = int(request.GET.get('days', 30))
    start_date = today - timedelta(days=days_back)
    
    # Also get comparison period (previous same period)
    comparison_start = start_date - timedelta(days=days_back)
    comparison_end = start_date
    
    # Sales analytics
    sales_data = Sale.objects.filter(sale_date__date__gte=start_date)
    total_sales = sales_data.count()
    total_revenue = 0
    total_cost = 0
    
    # Calculate revenue and cost for current period
    for sale in sales_data:
        total_revenue += sale.net_amount
        # Calculate cost of goods sold for this sale
        sale_items = SaleItem.objects.filter(sale=sale).select_related('product')
        for item in sale_items:
            total_cost += (item.product.cost_price * item.quantity)
    
    # Comparison period sales
    comparison_sales_data = Sale.objects.filter(
        sale_date__date__gte=comparison_start,
        sale_date__date__lt=comparison_end
    )
    comparison_sales = comparison_sales_data.count()
    comparison_revenue = 0
    for sale in comparison_sales_data:
        comparison_revenue += sale.net_amount
    
    # Expense analytics
    expense_data = Expense.objects.filter(expense_date__gte=start_date)
    total_expenses = expense_data.aggregate(total=Sum('amount'))['total'] or 0
    
    # Comparison expenses
    comparison_expenses = Expense.objects.filter(
        expense_date__gte=comparison_start,
        expense_date__lt=comparison_end
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate profits
    gross_profit = total_revenue - total_cost
    net_profit = gross_profit - total_expenses
    comparison_net_profit = comparison_revenue - comparison_expenses
    
    # Calculate percentage changes
    sales_change = 0
    revenue_change = 0
    expense_change = 0
    profit_change = 0
    
    if comparison_sales > 0:
        sales_change = ((total_sales - comparison_sales) / comparison_sales) * 100
    if comparison_revenue > 0:
        revenue_change = ((total_revenue - comparison_revenue) / comparison_revenue) * 100
    if comparison_expenses > 0:
        expense_change = ((total_expenses - comparison_expenses) / comparison_expenses) * 100
    if comparison_net_profit != 0:
        profit_change = ((net_profit - comparison_net_profit) / abs(comparison_net_profit)) * 100
    
    # Product analytics
    top_products = Product.objects.filter(is_active=True).annotate(
        total_sold=Sum('saleitem__quantity', filter=Q(saleitem__sale__sale_date__date__gte=start_date))
    ).order_by('-total_sold')[:10]
    
    # Low stock products
    low_stock_products = Product.objects.filter(
        stock_quantity__lte=F('min_stock_level'),
        is_active=True
    ).count()
    
    # Expense by category
    expense_categories = Expense.objects.filter(
        expense_date__gte=start_date
    ).values('category__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')[:10]
    
    # Customer analytics
    top_customers = Customer.objects.annotate(
        total_purchases=Sum('sale__total_amount', filter=Q(sale__sale_date__date__gte=start_date)),
        purchase_count=Count('sale', filter=Q(sale__sale_date__date__gte=start_date))
    ).filter(total_purchases__gt=0).order_by('-total_purchases')[:10]
    
    # Project analytics
    active_projects = Project.objects.filter(status='in_progress').count()
    completed_projects = Project.objects.filter(status='completed').count()
    total_project_budget = Project.objects.filter(status='in_progress').aggregate(
        total=Sum('budget')
    )['total'] or 0
    
    # Monthly trends (last 12 months)
    monthly_data = []
    for i in range(12):
        month_start = today.replace(day=1) - timedelta(days=i*30)
        month_end = month_start + timedelta(days=30)
        
        month_sales_total = 0
        month_sales_qs = Sale.objects.filter(
            sale_date__date__gte=month_start,
            sale_date__date__lt=month_end
        )
        
        # Calculate net amount manually for each sale
        for sale in month_sales_qs:
            month_sales_total += sale.net_amount
        
        month_expenses = Expense.objects.filter(
            expense_date__gte=month_start,
            expense_date__lt=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'sales': float(month_sales_total),
            'expenses': float(month_expenses),
            'profit': float(month_sales_total - month_expenses)
        })
    
    # Calculate percentages
    gross_margin_percent = (gross_profit * 100 / total_revenue) if total_revenue > 0 else 0
    net_margin_percent = (net_profit * 100 / total_revenue) if total_revenue > 0 else 0
    cost_percentage = (total_cost * 100 / total_revenue) if total_revenue > 0 else 0
    
    context = {
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'total_cost': total_cost,
        'gross_profit': gross_profit,
        'net_profit': net_profit,
        'profit': net_profit,  # Keep for backward compatibility
        'sales_change': sales_change,
        'revenue_change': revenue_change,
        'expense_change': expense_change,
        'profit_change': profit_change,
        'gross_margin_percent': gross_margin_percent,
        'net_margin_percent': net_margin_percent,
        'cost_percentage': cost_percentage,
        'top_products': top_products,
        'low_stock_products': low_stock_products,
        'expense_categories': expense_categories,
        'top_customers': top_customers,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'total_project_budget': total_project_budget,
        'monthly_data': list(reversed(monthly_data)),
        'days_back': days_back,
        'start_date': start_date,
        'comparison_period': f"{comparison_start} to {comparison_end}",
    }
    
    return render(request, 'reports/analytics.html', context)

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)
    
    return render(request, 'notifications/list.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    
    return JsonResponse({'success': True})

@login_required
def notification_count_api(request):
    """API endpoint to get unread notification count"""
    try:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return JsonResponse({
            'count': count,
            'success': True
        })
    except Exception as e:
        return JsonResponse({
            'count': 0,
            'success': False,
            'error': str(e)
        })

@login_required
def notification_dropdown_api(request):
    """API endpoint to get notifications for dropdown"""
    from django.utils.timesince import timesince
    
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:10]
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'notification_type': notification.notification_type,
            'time_ago': timesince(notification.created_at) + " ago"
        })
    
    return JsonResponse({
        'notifications': notifications_data,
        'count': len(notifications_data)
    })

# API endpoints for AJAX requests
@login_required
def dashboard_data_api(request):
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Sales data for the last 30 days
    sales_data = []
    for i in range(30):
        date = today - timedelta(days=i)
        daily_sales = Sale.objects.filter(sale_date__date=date).aggregate(
            total=Sum('total_amount'))['total'] or 0
        sales_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'sales': float(daily_sales)
        })
    
    return JsonResponse({
        'sales_data': list(reversed(sales_data)),
        'low_stock_count': Product.objects.filter(
            stock_quantity__lte=F('min_stock_level'),
            is_active=True
        ).count()
    })

@login_required
def sales_chart_api(request):
    try:
        today = timezone.now().date()
        days = int(request.GET.get('days', 30))
        start_date = today - timedelta(days=days)
        
        sales_data = []
        total_sales = 0
        total_transactions = 0
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            try:
                daily_sales_qs = Sale.objects.filter(sale_date__date=date)
                daily_amount = 0
                daily_count = daily_sales_qs.count()
                
                # Calculate net amount manually for each sale
                for sale in daily_sales_qs:
                    daily_amount += sale.net_amount
                
                sales_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'sales': daily_amount,
                    'transactions': daily_count
                })
                
                total_sales += daily_amount
                total_transactions += daily_count
            except Exception as e:
                # If there's an error with a specific date, add zero values
                sales_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'sales': 0,
                    'transactions': 0
                })
        
        # Calculate additional statistics
        avg_daily_sales = total_sales / days if days > 0 else 0
        sales_amounts = [item['sales'] for item in sales_data]
        max_daily_sales = max(sales_amounts) if sales_amounts else 0
        
        return JsonResponse({
            'data': sales_data,
            'summary': {
                'total_sales': total_sales,
                'total_transactions': total_transactions,
                'avg_daily_sales': avg_daily_sales,
                'max_daily_sales': max_daily_sales,
                'period_days': days
            }
        })
    except Exception as e:
        # Return error response for debugging
        return JsonResponse({
            'error': str(e),
            'data': [],
            'summary': {
                'total_sales': 0,
                'total_transactions': 0,
                'avg_daily_sales': 0,
                'max_daily_sales': 0,
                'period_days': days
            }
        }, status=200)  # Return 200 to avoid triggering error handlers

@login_required
def product_search_api(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(sku__icontains=query),
        is_active=True,
        stock_quantity__gt=0
    )[:10]
    
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'price': float(product.selling_price),
            'stock': product.stock_quantity
        })
    
    return JsonResponse({'results': results})

# Electrical Maintenance Views
@login_required
def electrical_list(request):
    devices = ElectricalDevice.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        devices = devices.filter(
            Q(name__icontains=search_query) |
            Q(model_number__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(manufacturer__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        devices = devices.filter(status=status_filter)
    
    # Filter by priority
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        devices = devices.filter(priority=priority_filter)
    
    # Statistics
    total_devices = devices.count()
    working_devices = devices.filter(status='working').count()
    maintenance_devices = devices.filter(status__in=['maintenance', 'repair']).count()
    critical_devices = devices.filter(priority='critical').count()
    due_maintenance = devices.filter(next_maintenance__lte=timezone.now().date()).count()
    
    # Pagination
    paginator = Paginator(devices, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'devices': page_obj,
        'total_devices': total_devices,
        'working_devices': working_devices,
        'maintenance_devices': maintenance_devices,
        'critical_devices': critical_devices,
        'due_maintenance': due_maintenance,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'status_choices': ElectricalDevice.STATUS_CHOICES,
        'priority_choices': ElectricalDevice.PRIORITY_CHOICES,
    }
    return render(request, 'electrical/list.html', context)

@login_required
def electrical_add(request):
    if request.method == 'POST':
        try:
            device = ElectricalDevice(
                name=request.POST.get('name'),
                model_number=request.POST.get('model_number', ''),
                serial_number=request.POST.get('serial_number', ''),
                manufacturer=request.POST.get('manufacturer', ''),
                voltage_rating=request.POST.get('voltage_rating', ''),
                power_rating=request.POST.get('power_rating', ''),
                location=request.POST.get('location', 'Main Office'),
                status=request.POST.get('status', 'working'),
                priority=request.POST.get('priority', 'medium'),
                maintenance_cost=request.POST.get('maintenance_cost', 0),
                description=request.POST.get('description', ''),
                created_by=request.user
            )
            
            # Handle date fields
            purchase_date = request.POST.get('purchase_date')
            if purchase_date:
                device.purchase_date = purchase_date
            
            warranty_expiry = request.POST.get('warranty_expiry')
            if warranty_expiry:
                device.warranty_expiry = warranty_expiry
            
            last_maintenance = request.POST.get('last_maintenance')
            if last_maintenance:
                device.last_maintenance = last_maintenance
            
            next_maintenance = request.POST.get('next_maintenance')
            if next_maintenance:
                device.next_maintenance = next_maintenance
            
            device.save()
            messages.success(request, f'Electrical device "{device.name}" has been added successfully!')
            return redirect('electrical_list')
        except Exception as e:
            messages.error(request, f'Error adding device: {str(e)}')
    
    context = {
        'status_choices': ElectricalDevice.STATUS_CHOICES,
        'priority_choices': ElectricalDevice.PRIORITY_CHOICES,
    }
    return render(request, 'electrical/add.html', context)

@login_required
def electrical_edit(request, device_id):
    device = get_object_or_404(ElectricalDevice, id=device_id)
    
    if request.method == 'POST':
        try:
            device.name = request.POST.get('name')
            device.model_number = request.POST.get('model_number', '')
            device.serial_number = request.POST.get('serial_number', '')
            device.manufacturer = request.POST.get('manufacturer', '')
            device.voltage_rating = request.POST.get('voltage_rating', '')
            device.power_rating = request.POST.get('power_rating', '')
            device.location = request.POST.get('location', 'Main Office')
            device.status = request.POST.get('status', 'working')
            device.priority = request.POST.get('priority', 'medium')
            device.maintenance_cost = request.POST.get('maintenance_cost', 0)
            device.description = request.POST.get('description', '')
            
            # Handle date fields
            purchase_date = request.POST.get('purchase_date')
            device.purchase_date = purchase_date if purchase_date else None
            
            warranty_expiry = request.POST.get('warranty_expiry')
            device.warranty_expiry = warranty_expiry if warranty_expiry else None
            
            last_maintenance = request.POST.get('last_maintenance')
            device.last_maintenance = last_maintenance if last_maintenance else None
            
            next_maintenance = request.POST.get('next_maintenance')
            device.next_maintenance = next_maintenance if next_maintenance else None
            
            device.save()
            messages.success(request, f'Electrical device "{device.name}" has been updated successfully!')
            return redirect('electrical_list')
        except Exception as e:
            messages.error(request, f'Error updating device: {str(e)}')
    
    context = {
        'device': device,
        'status_choices': ElectricalDevice.STATUS_CHOICES,
        'priority_choices': ElectricalDevice.PRIORITY_CHOICES,
    }
    return render(request, 'electrical/edit.html', context)

@login_required
def electrical_delete(request, device_id):
    device = get_object_or_404(ElectricalDevice, id=device_id)
    
    if request.method == 'POST':
        device_name = device.name
        device.delete()
        messages.success(request, f'Electrical device "{device_name}" has been deleted successfully!')
        return redirect('electrical_list')
    
    return render(request, 'electrical/delete.html', {'device': device})

# Electronics Maintenance Views
@login_required
def electronics_list(request):
    devices = ElectronicsDevice.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        devices = devices.filter(
            Q(name__icontains=search_query) |
            Q(model_number__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(manufacturer__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(assigned_to__icontains=search_query)
        )
    
    # Filter by device type
    type_filter = request.GET.get('device_type', '')
    if type_filter:
        devices = devices.filter(device_type=type_filter)
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        devices = devices.filter(status=status_filter)
    
    # Filter by priority
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        devices = devices.filter(priority=priority_filter)
    
    # Statistics
    total_devices = devices.count()
    working_devices = devices.filter(status='working').count()
    maintenance_devices = devices.filter(status__in=['maintenance', 'repair']).count()
    critical_devices = devices.filter(priority='critical').count()
    due_maintenance = devices.filter(next_maintenance__lte=timezone.now().date()).count()
    
    # Device type breakdown
    device_type_stats = {}
    for device_type, display_name in ElectronicsDevice.DEVICE_TYPES:
        count = devices.filter(device_type=device_type).count()
        if count > 0:
            device_type_stats[display_name] = count
    
    # Pagination
    paginator = Paginator(devices, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'devices': page_obj,
        'total_devices': total_devices,
        'working_devices': working_devices,
        'maintenance_devices': maintenance_devices,
        'critical_devices': critical_devices,
        'due_maintenance': due_maintenance,
        'device_type_stats': device_type_stats,
        'search_query': search_query,
        'type_filter': type_filter,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'device_types': ElectronicsDevice.DEVICE_TYPES,
        'status_choices': ElectronicsDevice.STATUS_CHOICES,
        'priority_choices': ElectronicsDevice.PRIORITY_CHOICES,
    }
    return render(request, 'electronics/list.html', context)

@login_required
def electronics_add(request):
    if request.method == 'POST':
        try:
            device = ElectronicsDevice(
                name=request.POST.get('name'),
                device_type=request.POST.get('device_type', 'other'),
                model_number=request.POST.get('model_number', ''),
                serial_number=request.POST.get('serial_number', ''),
                manufacturer=request.POST.get('manufacturer', ''),
                operating_system=request.POST.get('operating_system', ''),
                specifications=request.POST.get('specifications', ''),
                location=request.POST.get('location', 'Main Office'),
                status=request.POST.get('status', 'working'),
                priority=request.POST.get('priority', 'medium'),
                maintenance_cost=request.POST.get('maintenance_cost', 0),
                description=request.POST.get('description', ''),
                assigned_to=request.POST.get('assigned_to', ''),
                created_by=request.user
            )
            
            # Handle date fields
            purchase_date = request.POST.get('purchase_date')
            if purchase_date:
                device.purchase_date = purchase_date
            
            warranty_expiry = request.POST.get('warranty_expiry')
            if warranty_expiry:
                device.warranty_expiry = warranty_expiry
            
            last_maintenance = request.POST.get('last_maintenance')
            if last_maintenance:
                device.last_maintenance = last_maintenance
            
            next_maintenance = request.POST.get('next_maintenance')
            if next_maintenance:
                device.next_maintenance = next_maintenance
            
            device.save()
            messages.success(request, f'Electronics device "{device.name}" has been added successfully!')
            return redirect('electronics_list')
        except Exception as e:
            messages.error(request, f'Error adding device: {str(e)}')
    
    context = {
        'device_types': ElectronicsDevice.DEVICE_TYPES,
        'status_choices': ElectronicsDevice.STATUS_CHOICES,
        'priority_choices': ElectronicsDevice.PRIORITY_CHOICES,
    }
    return render(request, 'electronics/add.html', context)

@login_required
def electronics_edit(request, device_id):
    device = get_object_or_404(ElectronicsDevice, id=device_id)
    
    if request.method == 'POST':
        try:
            device.name = request.POST.get('name')
            device.device_type = request.POST.get('device_type', 'other')
            device.model_number = request.POST.get('model_number', '')
            device.serial_number = request.POST.get('serial_number', '')
            device.manufacturer = request.POST.get('manufacturer', '')
            device.operating_system = request.POST.get('operating_system', '')
            device.specifications = request.POST.get('specifications', '')
            device.location = request.POST.get('location', 'Main Office')
            device.status = request.POST.get('status', 'working')
            device.priority = request.POST.get('priority', 'medium')
            device.maintenance_cost = request.POST.get('maintenance_cost', 0)
            device.description = request.POST.get('description', '')
            device.assigned_to = request.POST.get('assigned_to', '')
            
            # Handle date fields
            purchase_date = request.POST.get('purchase_date')
            device.purchase_date = purchase_date if purchase_date else None
            
            warranty_expiry = request.POST.get('warranty_expiry')
            device.warranty_expiry = warranty_expiry if warranty_expiry else None
            
            last_maintenance = request.POST.get('last_maintenance')
            device.last_maintenance = last_maintenance if last_maintenance else None
            
            next_maintenance = request.POST.get('next_maintenance')
            device.next_maintenance = next_maintenance if next_maintenance else None
            
            device.save()
            messages.success(request, f'Electronics device "{device.name}" has been updated successfully!')
            return redirect('electronics_list')
        except Exception as e:
            messages.error(request, f'Error updating device: {str(e)}')
    
    context = {
        'device': device,
        'device_types': ElectronicsDevice.DEVICE_TYPES,
        'status_choices': ElectronicsDevice.STATUS_CHOICES,
        'priority_choices': ElectronicsDevice.PRIORITY_CHOICES,
    }
    return render(request, 'electronics/edit.html', context)

@login_required
def electronics_delete(request, device_id):
    device = get_object_or_404(ElectronicsDevice, id=device_id)
    
    if request.method == 'POST':
        device_name = device.name
        device.delete()
        messages.success(request, f'Electronics device "{device_name}" has been deleted successfully!')
        return redirect('electronics_list')
    
    return render(request, 'electronics/delete.html', {'device': device})

@login_required
@require_POST
@csrf_exempt
def verify_admin_password(request):
    """
    API endpoint to verify admin password for accessing sensitive information
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        password = data.get('password', '')
        
        if not password:
            return JsonResponse({
                'success': False,
                'message': 'Password is required'
            }, status=400)
        
        # Authenticate the current user with the provided password
        user = authenticate(username=request.user.username, password=password)
        
        if user is not None and user.is_staff:
            # Store the admin verification in session for this session only
            request.session['admin_verified'] = True
            request.session['admin_verified_at'] = timezone.now().isoformat()
            
            return JsonResponse({
                'success': True,
                'message': 'Admin access granted'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid password or insufficient privileges'
            }, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid request format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)

@login_required
def profile_view(request):
    """View for user profile page"""
    if request.method == 'POST':
        # Handle profile update
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'title': 'Profile',
        'user': request.user,
    }
    return render(request, 'profile/profile.html', context)

@login_required
def settings_view(request):
    """View for user settings page"""
    if request.method == 'POST':
        # Handle different form submissions
        if 'change_password' in request.POST:
            # Handle password change
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
            elif len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
            else:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, 'Password changed successfully!')
                return redirect('login')  # Redirect to login after password change
        
        elif 'account_settings' in request.POST:
            # Handle account settings update
            user = request.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.save()
            messages.success(request, 'Account settings updated successfully!')
    
    context = {
        'title': 'Settings',
        'user': request.user,
    }
    return render(request, 'settings/settings.html', context)
