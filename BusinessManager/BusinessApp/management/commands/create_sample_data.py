from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import random
from datetime import date, timedelta
from BusinessApp.models import Project, ElectricalDevice, ElectronicsDevice

class Command(BaseCommand):
    help = 'Generate sample data for Projects, Electrical and Electronics devices'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of records to create for each model (default: 10)',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Get or create a default user
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@empiredynamics.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: admin/admin123'))

        # Clear existing sample data (optional)
        self.stdout.write('Clearing existing sample data...')
        Project.objects.filter(name__startswith='Sample').delete()
        ElectricalDevice.objects.filter(name__startswith='Sample').delete()
        ElectronicsDevice.objects.filter(name__startswith='Sample').delete()

        # Create Projects
        self.stdout.write('Creating sample projects...')
        projects_data = [
            {
                'name': 'Sample Office Building Renovation',
                'description': 'Complete renovation of the main office building including electrical, plumbing, and interior design',
                'client': 'Empire Dynamics Ltd',
                'budget': Decimal('150000.00'),
                'spent_amount': Decimal('75000.00'),
                'status': 'in_progress',
                'progress': 50
            },
            {
                'name': 'Sample Smart Home Installation',
                'description': 'Installation of smart home automation system including lighting, security, and climate control',
                'client': 'Johnson Family',
                'budget': Decimal('45000.00'),
                'spent_amount': Decimal('42000.00'),
                'status': 'completed',
                'progress': 100
            },
            {
                'name': 'Sample Industrial Electrical Upgrade',
                'description': 'Upgrade of industrial electrical systems for manufacturing facility',
                'client': 'TechManufacturing Corp',
                'budget': Decimal('200000.00'),
                'spent_amount': Decimal('120000.00'),
                'status': 'in_progress',
                'progress': 60
            },
            {
                'name': 'Sample Solar Panel Installation',
                'description': 'Installation of solar panel system for residential complex',
                'client': 'Green Valley Apartments',
                'budget': Decimal('85000.00'),
                'spent_amount': Decimal('25000.00'),
                'status': 'planning',
                'progress': 15
            },
            {
                'name': 'Sample Data Center Setup',
                'description': 'Complete setup of data center with cooling, power backup, and network infrastructure',
                'client': 'CloudTech Solutions',
                'budget': Decimal('300000.00'),
                'spent_amount': Decimal('180000.00'),
                'status': 'in_progress',
                'progress': 70
            },
            {
                'name': 'Sample School Electrical System',
                'description': 'Installation of modern electrical system for new school building',
                'client': 'Dar es Salaam International School',
                'budget': Decimal('120000.00'),
                'spent_amount': Decimal('95000.00'),
                'status': 'in_progress',
                'progress': 80
            },
            {
                'name': 'Sample Hospital Generator Installation',
                'description': 'Installation of backup generator system for hospital emergency power',
                'client': 'Muhimbili National Hospital',
                'budget': Decimal('180000.00'),
                'spent_amount': Decimal('180000.00'),
                'status': 'completed',
                'progress': 100
            },
            {
                'name': 'Sample Shopping Mall Lighting',
                'description': 'LED lighting installation and upgrade for shopping mall',
                'client': 'City Mall Tanzania',
                'budget': Decimal('75000.00'),
                'spent_amount': Decimal('15000.00'),
                'status': 'planning',
                'progress': 10
            },
            {
                'name': 'Sample Factory Automation',
                'description': 'Industrial automation and control system installation',
                'client': 'Tanzanian Textile Industries',
                'budget': Decimal('250000.00'),
                'spent_amount': Decimal('0.00'),
                'status': 'planning',
                'progress': 5
            },
            {
                'name': 'Sample Hotel Electrical Retrofit',
                'description': 'Complete electrical system retrofit for luxury hotel',
                'client': 'Serena Hotel Dar es Salaam',
                'budget': Decimal('160000.00'),
                'spent_amount': Decimal('80000.00'),
                'status': 'on_hold',
                'progress': 35
            }
        ]

        for i, project_data in enumerate(projects_data[:count]):
            start_date = timezone.now().date() - timedelta(days=random.randint(30, 365))
            end_date = start_date + timedelta(days=random.randint(30, 180)) if project_data['status'] in ['completed', 'in_progress'] else None
            
            Project.objects.create(
                name=project_data['name'],
                description=project_data['description'],
                client=project_data['client'],
                budget=project_data['budget'],
                spent_amount=project_data['spent_amount'],
                start_date=start_date,
                end_date=end_date,
                status=project_data['status'],
                progress=project_data['progress'],
                created_by=user
            )

        # Create Electrical Devices
        self.stdout.write('Creating sample electrical devices...')
        electrical_devices_data = [
            {
                'name': 'Sample Main Distribution Panel',
                'model_number': 'MDP-400A-3P',
                'manufacturer': 'Schneider Electric',
                'voltage_rating': '400V AC',
                'power_rating': '400A',
                'location': 'Main Electrical Room',
                'status': 'working',
                'priority': 'critical'
            },
            {
                'name': 'Sample Emergency Generator',
                'model_number': 'DG-150KVA',
                'manufacturer': 'Caterpillar',
                'voltage_rating': '400V AC',
                'power_rating': '150KVA',
                'location': 'Generator Room',
                'status': 'working',
                'priority': 'critical'
            },
            {
                'name': 'Sample UPS System',
                'model_number': 'UPS-20KVA-Online',
                'manufacturer': 'APC',
                'voltage_rating': '230V AC',
                'power_rating': '20KVA',
                'location': 'Server Room',
                'status': 'working',
                'priority': 'high'
            },
            {
                'name': 'Sample Air Conditioning Unit',
                'model_number': 'AC-5TR-Split',
                'manufacturer': 'Daikin',
                'voltage_rating': '415V AC',
                'power_rating': '5TR',
                'location': 'Conference Room',
                'status': 'maintenance',
                'priority': 'medium'
            },
            {
                'name': 'Sample Industrial Motor',
                'model_number': 'IM-15HP-3PH',
                'manufacturer': 'Siemens',
                'voltage_rating': '415V AC',
                'power_rating': '15HP',
                'location': 'Production Floor',
                'status': 'working',
                'priority': 'high'
            },
            {
                'name': 'Sample Lighting Control Panel',
                'model_number': 'LCP-32CH-DMX',
                'manufacturer': 'Philips',
                'voltage_rating': '230V AC',
                'power_rating': '5KW',
                'location': 'Lighting Control Room',
                'status': 'working',
                'priority': 'medium'
            },
            {
                'name': 'Sample Fire Pump Motor',
                'model_number': 'FPM-25HP-Vertical',
                'manufacturer': 'Grundfos',
                'voltage_rating': '415V AC',
                'power_rating': '25HP',
                'location': 'Fire Pump Room',
                'status': 'working',
                'priority': 'critical'
            },
            {
                'name': 'Sample Elevator Motor Drive',
                'model_number': 'EMD-10HP-VFD',
                'manufacturer': 'OTIS',
                'voltage_rating': '415V AC',
                'power_rating': '10HP',
                'location': 'Elevator Machine Room',
                'status': 'repair',
                'priority': 'high'
            },
            {
                'name': 'Sample Water Heater Element',
                'model_number': 'WHE-6KW-Immersion',
                'manufacturer': 'Ariston',
                'voltage_rating': '230V AC',
                'power_rating': '6KW',
                'location': 'Utility Room',
                'status': 'working',
                'priority': 'low'
            },
            {
                'name': 'Sample Security System Panel',
                'model_number': 'SSP-16Zone-GSM',
                'manufacturer': 'Honeywell',
                'voltage_rating': '12V DC',
                'power_rating': '2A',
                'location': 'Security Control Room',
                'status': 'damaged',
                'priority': 'high'
            }
        ]

        for i, device_data in enumerate(electrical_devices_data[:count]):
            purchase_date = timezone.now().date() - timedelta(days=random.randint(90, 1095))
            warranty_expiry = purchase_date + timedelta(days=random.randint(365, 1095))
            last_maintenance = purchase_date + timedelta(days=random.randint(30, 300))
            next_maintenance = last_maintenance + timedelta(days=random.randint(30, 180))
            
            ElectricalDevice.objects.create(
                name=device_data['name'],
                model_number=device_data['model_number'],
                serial_number=f"SN{random.randint(100000, 999999)}",
                manufacturer=device_data['manufacturer'],
                voltage_rating=device_data['voltage_rating'],
                power_rating=device_data['power_rating'],
                location=device_data['location'],
                status=device_data['status'],
                priority=device_data['priority'],
                purchase_date=purchase_date,
                warranty_expiry=warranty_expiry,
                last_maintenance=last_maintenance,
                next_maintenance=next_maintenance,
                maintenance_cost=Decimal(random.randint(5000, 50000)),
                description=f"Sample electrical device for demonstration purposes - {device_data['name']}",
                created_by=user
            )

        # Create Electronics Devices
        self.stdout.write('Creating sample electronics devices...')
        electronics_devices_data = [
            {
                'name': 'Sample Dell OptiPlex Desktop',
                'device_type': 'computer',
                'model_number': 'OptiPlex-7090',
                'manufacturer': 'Dell',
                'operating_system': 'Windows 11 Pro',
                'specifications': 'Intel i7-11700, 16GB RAM, 512GB SSD',
                'location': 'Accounting Department',
                'status': 'working',
                'priority': 'medium',
                'assigned_to': 'John Doe - Accountant'
            },
            {
                'name': 'Sample HP LaserJet Printer',
                'device_type': 'printer',
                'model_number': 'LaserJet-P3015',
                'manufacturer': 'HP',
                'operating_system': 'Embedded Linux',
                'specifications': 'Monochrome Laser, 42ppm, Network Ready',
                'location': 'General Office',
                'status': 'working',
                'priority': 'medium',
                'assigned_to': 'Shared Resource'
            },
            {
                'name': 'Sample Cisco Router',
                'device_type': 'router',
                'model_number': 'ISR-4321',
                'manufacturer': 'Cisco',
                'operating_system': 'Cisco IOS XE',
                'specifications': '4-port Gigabit, VPN capable, 2x SFP slots',
                'location': 'Network Room',
                'status': 'working',
                'priority': 'critical',
                'assigned_to': 'IT Department'
            },
            {
                'name': 'Sample Samsung Monitor',
                'device_type': 'monitor',
                'model_number': 'C27F390FHU',
                'manufacturer': 'Samsung',
                'operating_system': 'N/A',
                'specifications': '27" Curved, 1920x1080, HDMI/VGA',
                'location': 'Reception Desk',
                'status': 'working',
                'priority': 'low',
                'assigned_to': 'Receptionist'
            },
            {
                'name': 'Sample iPad Pro Tablet',
                'device_type': 'tablet',
                'model_number': 'iPad-Pro-12.9-5th',
                'manufacturer': 'Apple',
                'operating_system': 'iPadOS 15',
                'specifications': 'M1 Chip, 128GB, Wi-Fi + Cellular',
                'location': 'Executive Office',
                'status': 'working',
                'priority': 'medium',
                'assigned_to': 'CEO Office'
            },
            {
                'name': 'Sample Canon Document Scanner',
                'device_type': 'scanner',
                'model_number': 'DR-C225W',
                'manufacturer': 'Canon',
                'operating_system': 'Embedded',
                'specifications': 'Duplex ADF, 25ppm, Wi-Fi enabled',
                'location': 'Document Processing',
                'status': 'maintenance',
                'priority': 'medium',
                'assigned_to': 'Admin Department'
            },
            {
                'name': 'Sample Lenovo ThinkPad Laptop',
                'device_type': 'computer',
                'model_number': 'ThinkPad-E15-Gen3',
                'manufacturer': 'Lenovo',
                'operating_system': 'Windows 11 Pro',
                'specifications': 'AMD Ryzen 7, 16GB RAM, 512GB SSD',
                'location': 'Sales Department',
                'status': 'working',
                'priority': 'medium',
                'assigned_to': 'Sales Manager'
            },
            {
                'name': 'Sample Epson Projector',
                'device_type': 'projector',
                'model_number': 'EB-X41',
                'manufacturer': 'Epson',
                'operating_system': 'Embedded',
                'specifications': '3600 lumens, XGA, HDMI/VGA/USB',
                'location': 'Conference Room',
                'status': 'repair',
                'priority': 'high',
                'assigned_to': 'Conference Room'
            },
            {
                'name': 'Sample TP-Link Switch',
                'device_type': 'switch',
                'model_number': 'TL-SG1024',
                'manufacturer': 'TP-Link',
                'operating_system': 'Embedded',
                'specifications': '24-port Gigabit, Unmanaged',
                'location': 'Network Cabinet',
                'status': 'working',
                'priority': 'high',
                'assigned_to': 'IT Department'
            },
            {
                'name': 'Sample IP Phone System',
                'device_type': 'phone',
                'model_number': 'SIP-T46U',
                'manufacturer': 'Yealink',
                'operating_system': 'Linux',
                'specifications': '16-line IP Phone, Color Display, PoE',
                'location': 'Manager Office',
                'status': 'damaged',
                'priority': 'medium',
                'assigned_to': 'Operations Manager'
            }
        ]

        for i, device_data in enumerate(electronics_devices_data[:count]):
            purchase_date = timezone.now().date() - timedelta(days=random.randint(90, 1095))
            warranty_expiry = purchase_date + timedelta(days=random.randint(365, 1095))
            last_maintenance = purchase_date + timedelta(days=random.randint(30, 300))
            next_maintenance = last_maintenance + timedelta(days=random.randint(30, 365))
            
            ElectronicsDevice.objects.create(
                name=device_data['name'],
                device_type=device_data['device_type'],
                model_number=device_data['model_number'],
                serial_number=f"SN{random.randint(100000, 999999)}",
                manufacturer=device_data['manufacturer'],
                operating_system=device_data['operating_system'],
                specifications=device_data['specifications'],
                location=device_data['location'],
                status=device_data['status'],
                priority=device_data['priority'],
                purchase_date=purchase_date,
                warranty_expiry=warranty_expiry,
                last_maintenance=last_maintenance,
                next_maintenance=next_maintenance,
                maintenance_cost=Decimal(random.randint(1000, 25000)),
                description=f"Sample electronics device for demonstration purposes - {device_data['name']}",
                assigned_to=device_data['assigned_to'],
                created_by=user
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data:\n'
                f'- {count} Projects\n'
                f'- {count} Electrical Devices\n'
                f'- {count} Electronics Devices\n'
                f'Total: {count * 3} records created!'
            )
        )
