import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from clients.models import Client
from staff.models import Barber
from services.models import Service, ServiceCategory
from bookings.models import Appointment
from loyalty.models import LoyaltyAccount, PointsTransaction
from liveline.models import QueueEntry

User = get_user_model()

BARBER_NAMES = [
    ('master1', 'Алишер', 'Каримов', '+998901111101', 'Классические стрижки'),
    ('master2', 'Рустам', 'Усманов', '+998901111102', 'Бритьё и борода'),
    ('master3', 'Сардор', 'Турсунов', '+998901111103', 'Современные фейды'),
    ('master4', 'Жасур', 'Холматов', '+998901111104', 'Детские стрижки'),
]

CLIENT_NAMES = [
    ('Дилнавоз', 'Журакулова'),
    ('Малика', 'Каримова'),
    ('Анвар', 'Тошматов'),
    ('Нилуфар', 'Раджабова'),
    ('Бекзод', 'Назаров'),
    ('Камола', 'Юсупова'),
    ('Шохрух', 'Абдуллаев'),
    ('Мадина', 'Исмаилова'),
    ('Тимур', 'Хасанов'),
    ('Зарина', 'Алимова'),
    ('Илхом', 'Махмудов'),
    ('Гульнора', 'Сулайманова'),
    ('Достон', 'Ахмедов'),
    ('Шахноза', 'Турдиева'),
    ('Фаррух', 'Бабаев'),
]

CATEGORIES = [
    ('Стрижки', '✂️'),
    ('Борода', '🪒'),
    ('Окрашивание', '🎨'),
    ('Уход', '💆'),
    ('Детские', '👶'),
    ('Премиум', '⭐'),
]

SERVICES = [
    ('Стрижки', 'Мужская стрижка', 30, 25000),
    ('Стрижки', 'Машинкой', 20, 15000),
    ('Стрижки', 'Фейд', 45, 35000),
    ('Стрижки', 'Андеркат', 40, 30000),
    ('Борода', 'Моделирование бороды', 30, 20000),
    ('Борода', 'Бритьё опасной бритвой', 45, 30000),
    ('Борода', 'Стрижка усов', 15, 10000),
    ('Окрашивание', 'Окрашивание волос', 90, 80000),
    ('Окрашивание', 'Камуфляж седины', 60, 50000),
    ('Окрашивание', 'Окрашивание бороды', 45, 35000),
    ('Уход', 'Уход за кожей лица', 40, 40000),
    ('Уход', 'Чёрная маска', 30, 25000),
    ('Уход', 'Массаж головы', 20, 20000),
    ('Детские', 'Детская стрижка', 25, 20000),
    ('Детские', 'Первая стрижка', 30, 25000),
    ('Премиум', 'Полный VIP-пакет', 120, 150000),
    ('Премиум', 'Стрижка + бритьё', 60, 50000),
    ('Премиум', 'Свадебный пакет', 90, 120000),
    ('Стрижки', 'Стрижка ножницами', 40, 30000),
    ('Уход', 'Парафинотерапия', 30, 30000),
]


class Command(BaseCommand):
    help = 'Создаёт демо-данные для Барбершоп CRM'

    def handle(self, *args, **options):
        random.seed(42)
        self.stdout.write('Создание данных...')

        # admin
        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={'phone': '+998900000000', 'role': 'admin', 'first_name': 'Главный', 'last_name': 'Администратор', 'is_staff': True, 'is_superuser': True},
        )
        admin.set_password('admin123')
        admin.is_staff = True
        admin.is_superuser = True
        admin.role = 'admin'
        admin.save()

        # barbers
        barbers = []
        for username, first, last, phone, spec in BARBER_NAMES:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'phone': phone, 'role': 'barber', 'first_name': first, 'last_name': last, 'is_staff': True},
            )
            user.set_password('master123')
            user.role = 'barber'
            user.is_staff = True
            user.first_name = first
            user.last_name = last
            user.phone = phone
            user.save()
            barber, _ = Barber.objects.get_or_create(
                user=user,
                defaults={'specialization': spec, 'experience_years': random.randint(2, 12), 'rating': Decimal(str(round(random.uniform(4.3, 5.0), 2))), 'bio': f'Профессиональный мастер. {spec}.'},
            )
            barbers.append(barber)

        # categories
        cats = {}
        for name, emoji in CATEGORIES:
            cat, _ = ServiceCategory.objects.get_or_create(name=name, defaults={'icon_emoji': emoji})
            cat.icon_emoji = emoji
            cat.save()
            cats[name] = cat

        # services
        services = []
        for cat_name, name, dur, price in SERVICES:
            svc, _ = Service.objects.get_or_create(
                category=cats[cat_name], name=name,
                defaults={'duration_minutes': dur, 'price': Decimal(str(price)), 'description': f'{name} — качественное исполнение и индивидуальный подход.', 'is_active': True},
            )
            services.append(svc)

        # clients
        clients = []
        for i, (first, last) in enumerate(CLIENT_NAMES, start=1):
            username = f'client{i}'
            phone = f'+99893{1000000 + i:07d}'
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={'phone': phone, 'role': 'client', 'first_name': first, 'last_name': last},
            )
            user.set_password('client123')
            user.role = 'client'
            user.first_name = first
            user.last_name = last
            user.phone = phone
            user.save()
            client, _ = Client.objects.get_or_create(
                user=user,
                defaults={'preferred_barber': random.choice(barbers) if random.random() > 0.4 else None},
            )
            clients.append(client)
            LoyaltyAccount.objects.get_or_create(
                client=client,
                defaults={'balance': random.randint(30, 800), 'tier': random.choice(['bronze', 'silver', 'gold'])},
            )

        # appointments
        Appointment.objects.all().delete()
        now = timezone.now()
        appt_specs = []
        for _ in range(10):
            appt_specs.append((now - timedelta(days=random.randint(1, 30), hours=random.randint(0, 8)), 'completed'))
        for _ in range(5):
            appt_specs.append((now.replace(hour=random.randint(10, 18), minute=random.choice([0, 30])), random.choice(['confirmed', 'in_progress'])))
        for _ in range(15):
            appt_specs.append((now + timedelta(days=random.randint(1, 14), hours=random.randint(-4, 6)), random.choice(['pending', 'confirmed'])))
        for _ in range(3):
            appt_specs.append((now - timedelta(days=random.randint(1, 10)), 'cancelled'))

        for start_at, status in appt_specs:
            svc = random.choice(services)
            Appointment.objects.create(
                client=random.choice(clients),
                barber=random.choice(barbers),
                service=svc,
                start_at=start_at,
                duration_minutes=svc.duration_minutes,
                status=status,
            )
        n_appts = Appointment.objects.count()

        # points transactions
        PointsTransaction.objects.all().delete()
        for _ in range(50):
            client = random.choice(clients)
            account = client.loyalty
            amt = random.choice([20, 30, 50, -50, 100, -100, 75])
            PointsTransaction.objects.create(
                account=account,
                amount=amt,
                reason='Начисление за визит' if amt > 0 else 'Списание баллов',
            )

        # queue
        QueueEntry.objects.all().delete()
        for c in random.sample(clients, 5):
            QueueEntry.objects.create(
                client=c,
                preferred_barber=random.choice(barbers) if random.random() > 0.5 else None,
                status='waiting',
            )

        self.stdout.write(self.style.SUCCESS(
            f'Создано: {len(clients)} клиентов, {n_appts} записей, {len(services)} услуг, {len(barbers)} мастеров'
        ))
