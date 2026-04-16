"""
Management command to seed the database with demo data.
Run: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import ClientNode, FederatedRound, AttackLog, ModelPerformance
from core.federated import run_federated_simulation
from django.utils import timezone
import random
import json
from datetime import timedelta


class Command(BaseCommand):
    help = 'Seeds the database with demo data for FedSecure'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Seeding FedSecure database...')

        # Create superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@fedsecure.local', 'admin123')
            self.stdout.write('✅ Created admin user (admin/admin123)')
        else:
            self.stdout.write('ℹ️  Admin user already exists')

        # Create demo user
        if not User.objects.filter(username='analyst').exists():
            User.objects.create_user('analyst', 'analyst@fedsecure.local', 'analyst123')
            self.stdout.write('✅ Created analyst user (analyst/analyst123)')

        # Create clients
        client_data = [
            {'name': 'Hospital Node Alpha', 'ip': '192.168.1.10', 'samples': 5240, 'accuracy': 93.2},
            {'name': 'Bank Node Beta', 'ip': '192.168.1.11', 'samples': 4810, 'accuracy': 95.1},
            {'name': 'University Node Gamma', 'ip': '192.168.1.12', 'samples': 6100, 'accuracy': 91.8},
            {'name': 'Gov Node Delta', 'ip': '10.0.0.5', 'samples': 3900, 'accuracy': 94.5},
        ]

        clients = []
        for d in client_data:
            c, created = ClientNode.objects.get_or_create(
                name=d['name'],
                defaults={
                    'ip_address': d['ip'],
                    'local_samples': d['samples'],
                    'local_accuracy': d['accuracy'],
                    'status': random.choice(['active', 'active', 'active', 'idle']),
                    'last_seen': timezone.now() - timedelta(minutes=random.randint(0, 30)),
                }
            )
            clients.append(c)
            if created:
                self.stdout.write(f'✅ Created client: {c.name}')

        # Create federated rounds
        if FederatedRound.objects.count() == 0:
            self.stdout.write('🔄 Running federated simulation (10 rounds)...')
            run_federated_simulation(10)
            self.stdout.write('✅ Federated simulation complete')
        else:
            self.stdout.write(f'ℹ️  {FederatedRound.objects.count()} rounds already exist')

        self.stdout.write('\n' + '='*50)
        self.stdout.write('✅ Database seeded successfully!')
        self.stdout.write('='*50)
        self.stdout.write('🔑 Login credentials:')
        self.stdout.write('   Admin:    admin / admin123')
        self.stdout.write('   Analyst:  analyst / analyst123')
        self.stdout.write('🌐 Start server: python manage.py runserver')
        self.stdout.write('🔗 Open: http://127.0.0.1:8000/')
