#!/usr/bin/env python
"""
Script to check and display services statistics for debugging
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BusinessManager.settings')
django.setup()

from BusinessApp.models import ElectricalDevice, ElectronicsDevice, Project
from django.db.models import Count, Q

def check_services_data():
    """Check the actual services data in the database"""
    
    print("=== SERVICES DATA ANALYSIS ===")
    
    # Check electrical devices
    print("\n--- ELECTRICAL DEVICES ---")
    electrical_total = ElectricalDevice.objects.count()
    electrical_statuses = ElectricalDevice.objects.values('status').annotate(count=Count('id')).order_by('-count')
    
    print(f"Total Electrical Devices: {electrical_total}")
    print("Status breakdown:")
    for status in electrical_statuses:
        print(f"  {status['status']}: {status['count']}")
    
    # Check electronics devices  
    print("\n--- ELECTRONICS DEVICES ---")
    electronics_total = ElectronicsDevice.objects.count()
    electronics_statuses = ElectronicsDevice.objects.values('status').annotate(count=Count('id')).order_by('-count')
    
    print(f"Total Electronics Devices: {electronics_total}")
    print("Status breakdown:")
    for status in electronics_statuses:
        print(f"  {status['status']}: {status['count']}")
    
    # Check projects
    print("\n--- PROJECTS ---")
    projects_total = Project.objects.count()
    project_statuses = Project.objects.values('status').annotate(count=Count('id')).order_by('-count')
    
    print(f"Total Projects: {projects_total}")
    print("Status breakdown:")
    for status in project_statuses:
        print(f"  {status['status']}: {status['count']}")
    
    # Check due maintenance
    print("\n--- DUE MAINTENANCE ---")
    from django.utils import timezone
    today = timezone.now().date()
    
    try:
        electrical_due = ElectricalDevice.objects.filter(
            next_maintenance__lte=today,
            status__in=['working', 'active']
        ).count()
        print(f"Electrical devices due for maintenance: {electrical_due}")
    except Exception as e:
        print(f"Error checking electrical due maintenance: {e}")
        electrical_due = 0
    
    try:
        electronics_due = ElectronicsDevice.objects.filter(
            next_maintenance__lte=today,
            status__in=['working', 'active']
        ).count()
        print(f"Electronics devices due for maintenance: {electronics_due}")
    except Exception as e:
        print(f"Error checking electronics due maintenance: {e}")
        electronics_due = 0
    
    total_due_maintenance = electrical_due + electronics_due
    print(f"Total devices due for maintenance: {total_due_maintenance}")
    
    # Calculate corrected statistics
    print("\n=== CORRECTED STATISTICS ===")
    
    # Electrical stats with multiple possible status values
    electrical_working = ElectricalDevice.objects.filter(
        status__in=['working', 'active', 'operational']
    ).count()
    
    electrical_maintenance = ElectricalDevice.objects.filter(
        status__in=['maintenance', 'servicing', 'under_maintenance']
    ).count()
    
    electrical_repair = ElectricalDevice.objects.filter(
        status__in=['repair', 'broken', 'damaged', 'faulty']
    ).count()
    
    # Electronics stats
    electronics_working = ElectronicsDevice.objects.filter(
        status__in=['working', 'active', 'operational']
    ).count()
    
    electronics_maintenance = ElectronicsDevice.objects.filter(
        status__in=['maintenance', 'servicing', 'under_maintenance']  
    ).count()
    
    electronics_repair = ElectronicsDevice.objects.filter(
        status__in=['repair', 'broken', 'damaged', 'faulty']
    ).count()
    
    # Projects stats
    active_projects = Project.objects.filter(
        status__in=['active', 'in_progress', 'ongoing']
    ).count()
    
    # Totals
    total_devices = electrical_total + electronics_total
    total_working = electrical_working + electronics_working
    total_maintenance = electrical_maintenance + electronics_maintenance
    total_repair = electrical_repair + electronics_repair
    
    # Calculate uptime
    uptime = (total_working / total_devices * 100) if total_devices > 0 else 0
    
    # Calculate realistic budget estimates
    electrical_maintenance_cost = electrical_maintenance * 50000 + electrical_repair * 100000
    electronics_maintenance_cost = electronics_maintenance * 30000 + electronics_repair * 75000
    active_projects_budget = active_projects * 500000
    
    print(f"Total Devices: {total_devices}")
    print(f"Working Devices: {total_working}")
    print(f"Maintenance Devices: {total_maintenance}")
    print(f"Repair/Critical Devices: {total_repair}")
    print(f"Active Projects: {active_projects}")
    print(f"Due Maintenance: {total_due_maintenance}")
    print(f"Uptime Percentage: {uptime:.1f}%")
    print(f"Electrical Maintenance Cost: TSh {electrical_maintenance_cost:,}")
    print(f"Electronics Maintenance Cost: TSh {electronics_maintenance_cost:,}")
    print(f"Projects Budget: TSh {active_projects_budget:,}")
    
    return {
        'total_services_devices': total_devices,
        'total_working_devices': total_working,
        'total_maintenance_devices': total_maintenance,
        'total_critical_devices': total_repair,
        'total_due_maintenance': total_due_maintenance,
        'active_projects_count': active_projects,
        'services_uptime': uptime,
        'electrical_device_count': electrical_total,
        'electronics_device_count': electronics_total,
        'electrical_maintenance_cost': electrical_maintenance_cost,
        'electronics_maintenance_cost': electronics_maintenance_cost,
        'active_projects_budget': active_projects_budget,
    }

if __name__ == '__main__':
    stats = check_services_data()
    print(f"\n=== DASHBOARD CONTEXT ===")
    for key, value in stats.items():
        print(f"{key}: {value}")
