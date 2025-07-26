from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Sales
    path('sales/', views.sale_list, name='sale_list'),
    path('sales/add/', views.sale_add, name='sale_add'),
    path('sales/<int:pk>/', views.sale_detail, name='sale_detail'),
    
    # Expenses
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.expense_add, name='expense_add'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    
    # Projects
    path('projects/', views.project_list, name='project_list'),
    path('projects/add/', views.project_add, name='project_add'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    
    # Electrical Maintenance
    path('electrical/', views.electrical_list, name='electrical_list'),
    path('electrical/add/', views.electrical_add, name='electrical_add'),
    path('electrical/<int:pk>/edit/', views.electrical_edit, name='electrical_edit'),
    path('electrical/<int:pk>/delete/', views.electrical_delete, name='electrical_delete'),
    
    # Electronics Maintenance
    path('electronics/', views.electronics_list, name='electronics_list'),
    path('electronics/add/', views.electronics_add, name='electronics_add'),
    path('electronics/<int:pk>/edit/', views.electronics_edit, name='electronics_edit'),
    path('electronics/<int:pk>/delete/', views.electronics_delete, name='electronics_delete'),
    
    # Stock Management
    path('stock/', views.stock_in_list, name='stock_in_list'),
    path('stock/movement/', views.stock_movement, name='stock_movement'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:pk>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/count/', views.notification_count_api, name='notification_count_api'),
    path('notifications/dropdown/', views.notification_dropdown_api, name='notification_dropdown_api'),
    
    # Profile and Settings
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    
    # Debt Management
    path('debts/', views.debt_list, name='debt_list'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.customer_add, name='customer_add'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/profile/', views.customer_profile, name='customer_profile'),
    path('debts/<int:pk>/payment/', views.debt_payment, name='debt_payment'),
    path('sales/credit/', views.credit_sale_add, name='credit_sale_add'),
    
    # API endpoints for AJAX
    path('api/dashboard-data/', views.dashboard_data_api, name='dashboard_data_api'),
    path('api/sales-chart/', views.sales_chart_api, name='sales_chart_api'),
    path('api/services-chart/', views.services_chart_api, name='services_chart_api'),
    path('api/products/search/', views.product_search_api, name='product_search_api'),
    path('api/verify-admin-password/', views.verify_admin_password, name='verify_admin_password'),
    path('api/customers/search/', views.customer_search_api, name='customer_search_api'),
]