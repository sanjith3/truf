import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'turf_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from turfs.models import Turf, SportType
from django.core.files.base import ContentFile

User = get_user_model()

def populate():
    print("Populating data...")

    # Create Superuser
    if not User.objects.filter(phone_number='admin').exists():
        User.objects.create_superuser('admin', 'adminpass')
        print("Superuser created: admin / adminpass")

    # Create Sport Types
    football, _ = SportType.objects.get_or_create(name='Football', icon='fa-futbol')
    cricket, _ = SportType.objects.get_or_create(name='Cricket', icon='fa-cricket-bat')
    print("Sports created.")

    # Create Owner
    owner_phone = '9876543210'
    if not User.objects.filter(phone_number=owner_phone).exists():
        owner = User.objects.create_user(owner_phone, 'password123', is_turf_owner=True)
        print(f"Owner created: {owner_phone} / password123")
    else:
        owner = User.objects.get(phone_number=owner_phone)

    # Create Turfs
    if not Turf.objects.filter(name='Chennai Super Arena').exists():
        t1 = Turf.objects.create(
            owner=owner,
            name='Chennai Super Arena',
            description='Premier football turf with FIFA quality grass.',
            address='123 OMR Road',
            city='Chennai',
            price_per_hour=1500.00,
            is_active=True,
            amenities='Parking,Changing Room,Water'
        )
        t1.sports.add(football)
        print("Chennai Turf created.")

    if not Turf.objects.filter(name='Kochi Blasters Ground').exists():
        t2 = Turf.objects.create(
            owner=owner,
            name='Kochi Blasters Ground',
            description='The heart of football in Kerala.',
            address='Marine Drive',
            city='Kochi',
            price_per_hour=1200.00,
            is_active=True,
            amenities='Floodlights,Cafeteria'
        )
        t2.sports.add(football, cricket)
        print("Kochi Turf created.")

    print("Populate Complete.")

if __name__ == '__main__':
    populate()
