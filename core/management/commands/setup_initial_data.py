from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import UserRole, MaterialType, RVM

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up initial data for the RVM ecosystem'
    
    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')
        
        # create user roles
        roles_data = [
            {'name': 'regular_user', 'description': 'Regular recycling user'},
            {'name': 'admin', 'description': 'System administrator'},
            {'name': 'technician', 'description': 'RVM maintenance technician'},
        ]
        
        for role_data in roles_data:
            role, created = UserRole.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            if created:
                self.stdout.write(f'Created role: {role.name}')
            else:
                self.stdout.write(f'Role already exists: {role.name}')
        
        # create material types with point values
        materials_data = [
            {'name': 'Plastic', 'points_per_kg': 1.00},
            {'name': 'Metal', 'points_per_kg': 3.00},
            {'name': 'Glass', 'points_per_kg': 2.00},
            {'name': 'Paper', 'points_per_kg': 0.50},
            {'name': 'Cardboard', 'points_per_kg': 0.75},
        ]
        
        for material_data in materials_data:
            material, created = MaterialType.objects.get_or_create(
                name=material_data['name'],
                defaults={'points_per_kg': material_data['points_per_kg']}
            )
            if created:
                self.stdout.write(f'Created material: {material.name} ({material.points_per_kg} pts/kg)')
            else:
                self.stdout.write(f'Material already exists: {material.name}')
        
        # create some sample RVMs in Cairo locations
        rvms_data = [
            {'name': 'Maadi Station', 'location': 'Maadi Corniche, Cairo'},
            {'name': 'Zamalek Location', 'location': 'Zamalek, Gezira Island, Cairo'},
            {'name': 'Heliopolis Campus', 'location': 'Heliopolis, Cairo'},
            {'name': 'Nasr City Park', 'location': 'Nasr City, Cairo'},
            {'name': 'Downtown Cairo', 'location': 'Tahrir Square, Downtown Cairo'},
            {'name': 'Garden City', 'location': 'Garden City, Cairo'},
            {'name': 'Mohandessin', 'location': 'Mohandessin, Giza'},
            {'name': '6th of October', 'location': '6th of October City, Giza'},
        ]
        
        for rvm_data in rvms_data:
            rvm, created = RVM.objects.get_or_create(
                name=rvm_data['name'],
                defaults={'location': rvm_data['location']}
            )
            if created:
                self.stdout.write(f'Created RVM: {rvm.name} at {rvm.location}')
            else:
                self.stdout.write(f'RVM already exists: {rvm.name}')
        
        # create a superuser if none exists
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write('Creating superuser...')
            User.objects.create_superuser(
                email='admin@rvm.com',
                first_name='Ahmed',
                last_name='Mahmoud',
                password='admin123'
            )
            self.stdout.write('Superuser created: admin@rvm.com / admin123')
        
        self.stdout.write(self.style.SUCCESS('Initial data setup completed!')) 