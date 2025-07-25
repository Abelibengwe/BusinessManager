from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import (
    Product, Sale, SaleItem, Expense, Project, 
    StockMovement, Notification, Category, 
    ExpenseCategory, Customer, Supplier
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
    # Get current date and 30 days ago
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Basic statistics
    total_products = Product.objects.filter(is_active=True).count()
    total_sales = Sale.objects.filter(sale_date__date__gte=thirty_days_ago).count()
    total_revenue = Sale.objects.filter(sale_date__date__gte=thirty_days_ago).aggregate(
        total=Sum('total_amount'))['total'] or 0
    total_expenses = Expense.objects.filter(expense_date__gte=thirty_days_ago).aggregate(
        total=Sum('amount'))['total'] or 0
    
    # Low stock products
    low_stock_products = Product.objects.filter(
        stock_quantity__lte=F('min_stock_level'),
        is_active=True
    )[:5]
    
    # Recent sales
    recent_sales = Sale.objects.select_related('customer').order_by('-created_at')[:5]
    
    # Recent projects
    recent_projects = Project.objects.order_by('-created_at')[:5]
    
    # Notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:10]
    
    context = {
        'total_products': total_products,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'profit': total_revenue - total_expenses,
        'low_stock_products': low_stock_products,
        'recent_sales': recent_sales,
        'recent_projects': recent_projects,
        'notifications': notifications,
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
    sales = Sale.objects.select_related('customer', 'created_by').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(sales, 20)
    page_number = request.GET.get('page')
    sales = paginator.get_page(page_number)
    
    return render(request, 'sales/list.html', {'sales': sales})

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
    
    # Pagination
    paginator = Paginator(expenses, 20)
    page_number = request.GET.get('page')
    expenses = paginator.get_page(page_number)
    
    return render(request, 'expenses/list.html', {'expenses': expenses})

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
    return render(request, 'expenses/add.html', {'categories': categories})

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
    
    # Pagination
    paginator = Paginator(projects, 20)
    page_number = request.GET.get('page')
    projects = paginator.get_page(page_number)
    
    return render(request, 'projects/list.html', {'projects': projects})

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
def stock_in_list(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    stock_movements = StockMovement.objects.select_related('product', 'created_by').order_by('-created_at')[:20]
    
    return render(request, 'stock/list.html', {
        'products': products,
        'stock_movements': stock_movements
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
    # Date range (last 30 days by default)
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Sales analytics
    sales_data = Sale.objects.filter(sale_date__date__gte=thirty_days_ago)
    total_sales = sales_data.count()
    total_revenue = sales_data.aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Expense analytics
    expense_data = Expense.objects.filter(expense_date__gte=thirty_days_ago)
    total_expenses = expense_data.aggregate(total=Sum('amount'))['total'] or 0
    
    # Product analytics
    top_products = Product.objects.filter(is_active=True).annotate(
        total_sold=Sum('saleitem__quantity')
    ).order_by('-total_sold')[:10]
    
    # Project analytics
    active_projects = Project.objects.filter(status='in_progress').count()
    completed_projects = Project.objects.filter(status='completed').count()
    
    context = {
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'profit': total_revenue - total_expenses,
        'top_products': top_products,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
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
    today = timezone.now().date()
    days = int(request.GET.get('days', 30))
    start_date = today - timedelta(days=days)
    
    sales_data = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        daily_sales = Sale.objects.filter(sale_date__date=date).aggregate(
            total=Sum('total_amount'))['total'] or 0
        sales_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'sales': float(daily_sales)
        })
    
    return JsonResponse({'data': sales_data})

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
