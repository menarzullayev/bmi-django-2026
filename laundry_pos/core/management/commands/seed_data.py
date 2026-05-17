import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from customers.models import Customer
from catalog.models import ClothType, ServiceType, PriceRule
from intake.models import IntakeTicket, Garment
from payments.models import Payment
from delivery.models import DeliveryRoute, DeliveryAssignment


CLOTH_TYPES = [
    ('Рубашка', 'top', '👔'),
    ('Футболка', 'top', '👕'),
    ('Брюки', 'bottom', '👖'),
    ('Костюм', 'top', '🤵'),
    ('Пальто', 'outerwear', '🧥'),
    ('Одеяло', 'bedding', '🛏️'),
    ('Простыня', 'bedding', '🛌'),
    ('Детская одежда', 'top', '🧒'),
    ('Юбка', 'bottom', '👗'),
    ('Платье', 'top', '👗'),
    ('Куртка', 'outerwear', '🧥'),
    ('Свитер', 'top', '🧶'),
]

SERVICE_TYPES = [
    ('Стирка', 'wash', 'Стандартная стирка в воде'),
    ('Сухая чистка', 'dry', 'Химическая сухая чистка'),
    ('Глажка', 'iron', 'Глажка и отпаривание'),
    ('Чистка паром', 'steam', 'Деликатная чистка паром'),
    ('Чистка перьев', 'feather', 'Для пуховиков и подушек'),
    ('Удаление пятен', 'stain', 'Локальная обработка пятен'),
]

CUSTOMER_NAMES = [
    'Иванов Иван Иванович', 'Петрова Мария Сергеевна', 'Сидоров Алексей Петрович',
    'Кузнецова Елена Дмитриевна', 'Смирнов Дмитрий Олегович', 'Михайлова Ольга Викторовна',
    'Каримов Бекзод Алишерович', 'Юсупова Зарина Рустамовна', 'Назаров Тимур Камилович',
    'Хасанова Гульнара Шавкатовна', 'Рахимов Шохрух Бахтиёрович', 'Алиева Ноила Фарходовна',
    'Турсунов Жасур Икрамович', 'Эргашева Дилфуза Анваровна', 'Файзиев Сардор Уткирович',
    'Мирзоева Шахноза Эркиновна', 'Усманов Анвар Хасанович', 'Каримова Манзура Толибовна',
    'Соколов Виктор Андреевич', 'Орлова Анна Михайловна', 'Лебедев Сергей Николаевич',
    'Морозова Татьяна Владимировна', 'Волков Андрей Игоревич', 'Новикова Светлана Юрьевна',
    'Павлов Михаил Александрович', 'Семёнова Наталья Викторовна', 'Голубев Евгений Сергеевич',
    'Виноградова Ирина Олеговна', 'Богданов Максим Денисович', 'Воробьёва Юлия Алексеевна',
]

ADDRESSES = [
    'ул. Амира Темура, 12', 'ул. Шота Руставели, 45', 'пр. Мустакиллик, 7',
    'ул. Беруни, 23', 'ул. Навои, 88', 'ул. Чиланзар, 14, кв. 56',
    'ул. Юнусабад, 9-7', 'ул. Сергели, 34', 'ул. Бабура, 102',
    'пр. Бунёдкор, 19', 'ул. Лабзак, 5', 'мкр. Высоковольтный, 6',
]

NOTES_POOL = ['', '', 'Аккуратно', 'Срочно', 'Без отбеливателя', 'Деликатный режим', 'Пятно от вина']
COLORS = ['чёрный', 'белый', 'синий', 'красный', 'серый', 'бежевый', 'зелёный', '']


class Command(BaseCommand):
    help = 'Заполнить базу демо-данными для химчистки.'

    @transaction.atomic
    def handle(self, *args, **opts):
        self.stdout.write(self.style.NOTICE('Заполняем демо-данные...'))

        # Users
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={'is_staff': True, 'is_superuser': True, 'role': 'admin', 'full_name': 'Администратор Системы'},
        )
        if created:
            admin.set_password('admin123'); admin.save()

        accounts = [
            ('cashier1', 'cashier', 'Кассир Алишер'),
            ('cashier2', 'cashier', 'Кассир Гулноза'),
            ('operator', 'operator', 'Оператор Дилшод'),
            ('driver1', 'driver', 'Водитель Рустам'),
            ('driver2', 'driver', 'Водитель Бахтиёр'),
        ]
        users_by_role = {'cashier': [], 'driver': [], 'operator': [], 'admin': [admin]}
        for username, role, full in accounts:
            u, c = User.objects.get_or_create(
                username=username,
                defaults={'role': role, 'full_name': full, 'is_staff': role == 'admin'},
            )
            if c:
                u.set_password('admin123'); u.save()
            users_by_role.setdefault(role, []).append(u)

        cashiers = users_by_role['cashier'] + [admin]
        drivers = users_by_role['driver']

        # Catalog
        cloth_objs = []
        for name, cat, icon in CLOTH_TYPES:
            ct, _ = ClothType.objects.get_or_create(name=name, defaults={'category': cat, 'default_icon': icon})
            cloth_objs.append(ct)
        service_objs = []
        for name, code, desc in SERVICE_TYPES:
            st, _ = ServiceType.objects.get_or_create(name=name, defaults={'code': code, 'description': desc})
            service_objs.append(st)

        # Price rules
        for ct in cloth_objs:
            base = random.randint(15, 50) * 1000
            for st in service_objs:
                mult = {'wash': 1.0, 'dry': 1.6, 'iron': 0.5, 'steam': 1.4, 'feather': 1.8, 'stain': 0.7}.get(st.code, 1.0)
                price = Decimal(int(base * mult / 1000)) * 1000
                PriceRule.objects.update_or_create(
                    cloth_type=ct, service_type=st, defaults={'price': price},
                )

        # Customers
        customers = []
        for i, name in enumerate(CUSTOMER_NAMES):
            phone = f'+99890{1000000 + i * 7919 % 9000000:07d}'
            c, _ = Customer.objects.get_or_create(
                phone=phone,
                defaults={'full_name': name, 'address': random.choice(ADDRESSES)},
            )
            customers.append(c)

        # Tickets — 50 distributed across statuses
        IntakeTicket.objects.all().delete()
        status_plan = (['received'] * 5 + ['sorting'] * 5 + ['washing'] * 8 + ['drying'] * 5 +
                       ['ironing'] * 5 + ['ready'] * 10 + ['delivered'] * 10 + ['cancelled'] * 2)
        random.shuffle(status_plan)

        now = timezone.now()
        tickets = []
        for i, status in enumerate(status_plan):
            days_ago = random.randint(0, 9)
            received = now - timedelta(days=days_ago, hours=random.randint(0, 12), minutes=random.randint(0, 59))
            customer = random.choice(customers)
            pickup = 'delivery' if random.random() < 0.35 else 'in_store'
            ticket = IntakeTicket(
                customer=customer,
                cashier=random.choice(cashiers),
                status=status,
                received_at=received,
                ready_by=received + timedelta(days=random.randint(1, 3)),
                pickup_method=pickup,
                delivery_address=customer.address if pickup == 'delivery' else '',
                discount=Decimal(random.choice([0, 0, 0, 5000, 10000])),
                notes=random.choice(NOTES_POOL),
            )
            ticket.save()
            # Garments
            n_garments = random.randint(2, 6)
            subtotal = Decimal('0')
            for _ in range(n_garments):
                ct = random.choice(cloth_objs)
                st = random.choice(service_objs)
                pr = PriceRule.objects.filter(cloth_type=ct, service_type=st).first()
                price = pr.price if pr else Decimal('20000')
                Garment.objects.create(
                    ticket=ticket, cloth_type=ct, service_type=st,
                    color=random.choice(COLORS), brand='',
                    notes=random.choice(NOTES_POOL),
                    price=price, status=status,
                )
                subtotal += price
            ticket.subtotal = subtotal
            ticket.total = max(subtotal - ticket.discount, Decimal('0'))
            if status == 'ready':
                ticket.ready_at = received + timedelta(days=2)
            if status == 'delivered':
                ticket.ready_at = received + timedelta(days=2)
                ticket.delivered_at = received + timedelta(days=3)
            ticket.save(update_fields=['subtotal', 'total', 'ready_at', 'delivered_at'])
            tickets.append(ticket)

        # Payments for ready + delivered + some others
        for t in tickets:
            if t.status in ('ready', 'delivered') or random.random() < 0.2:
                method = random.choice(['cash', 'card', 'transfer'])
                amount = t.total if t.status == 'delivered' else (t.total if random.random() < 0.7 else t.total / 2)
                if amount > 0:
                    Payment.objects.create(
                        ticket=t, amount=amount, method=method,
                        cashier=t.cashier,
                        paid_at=t.received_at + timedelta(days=random.randint(0, 3)),
                    )
                    t.amount_paid = sum((p.amount for p in t.payments.all()), Decimal('0'))
                    t.save(update_fields=['amount_paid'])
                    t.customer.total_spent = (t.customer.total_spent or Decimal('0')) + amount
                    t.customer.save(update_fields=['total_spent'])

        # Delivery routes
        DeliveryRoute.objects.all().delete()
        today = timezone.localdate()
        for offset in [-3, -1, 0, 0, 2]:
            date = today + timedelta(days=offset)
            driver = random.choice(drivers)
            route_status = 'completed' if offset < 0 else ('in_progress' if offset == 0 else 'planned')
            route = DeliveryRoute.objects.create(date=date, driver=driver, status=route_status)
            candidates = [t for t in tickets if t.pickup_method == 'delivery'][:30]
            chosen = random.sample(candidates, k=min(random.randint(2, 5), len(candidates)))
            for i, t in enumerate(chosen, 1):
                a_status = 'delivered' if offset < 0 else 'pending'
                DeliveryAssignment.objects.create(
                    route=route, ticket=t,
                    address=t.delivery_address or t.customer.address or 'Адрес не указан',
                    order=i, status=a_status,
                    delivered_at=(now - timedelta(days=abs(offset))) if a_status == 'delivered' else None,
                )

        self.stdout.write(self.style.SUCCESS('Готово!'))
        self.stdout.write(f'  Пользователей: {User.objects.count()}')
        self.stdout.write(f'  Клиентов: {Customer.objects.count()}')
        self.stdout.write(f'  Видов одежды: {ClothType.objects.count()}')
        self.stdout.write(f'  Услуг: {ServiceType.objects.count()}')
        self.stdout.write(f'  Прайсов: {PriceRule.objects.count()}')
        self.stdout.write(f'  Квитанций: {IntakeTicket.objects.count()}')
        self.stdout.write(f'  Вещей: {Garment.objects.count()}')
        self.stdout.write(f'  Оплат: {Payment.objects.count()}')
        self.stdout.write(f'  Маршрутов: {DeliveryRoute.objects.count()}')
        sample = IntakeTicket.objects.first()
        if sample:
            self.stdout.write(self.style.NOTICE(f'  Пример квитанции: {sample.ticket_number}'))
            self.stdout.write(self.style.NOTICE(f'  Демо QR: /qr/{sample.ticket_number}/'))
