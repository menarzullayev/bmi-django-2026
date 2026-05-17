"""Idempotent seed data for the Auto Service ERP project."""
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from billing.models import Invoice
from customers.models import Customer
from parts.models import PartCategory, PartUsage, SparePart
from vehicles.models import Vehicle
from workflow.models import ServiceTask
from workorders.models import WorkOrder


User = get_user_model()

RUS_FIRST = [
    'Анвар', 'Алишер', 'Бахром', 'Дилшод', 'Жасур', 'Икром', 'Камол',
    'Лазиз', 'Мансур', 'Наби', 'Отабек', 'Рустам', 'Санжар', 'Темур',
    'Фарход', 'Хасан', 'Шерзод', 'Юсуф', 'Зафар', 'Бекзод',
    'Михаил', 'Сергей', 'Андрей', 'Иван', 'Дмитрий',
]
RUS_LAST = [
    'Тошматов', 'Каримов', 'Юсупов', 'Рахимов', 'Назаров', 'Усманов',
    'Хакимов', 'Ахмедов', 'Алиев', 'Расулов', 'Мирзоев', 'Касымов',
    'Исмаилов', 'Турсунов', 'Бакиров', 'Холматов', 'Пулатов',
    'Иванов', 'Петров', 'Сидоров', 'Кузнецов', 'Смирнов',
]
COMPANIES = ['', '', '', 'ООО «Логистика-Сервис»', 'ИП Каримов', 'ООО «Дельта-Транс»', 'АО «Узавтотранс»']

CAR_MODELS = [
    ('Chevrolet', 'Cobalt'), ('Chevrolet', 'Nexia'), ('Chevrolet', 'Spark'),
    ('Chevrolet', 'Lacetti'), ('Chevrolet', 'Captiva'), ('Chevrolet', 'Malibu'),
    ('Toyota', 'Camry'), ('Toyota', 'Corolla'), ('Toyota', 'RAV4'),
    ('BMW', 'X5'), ('BMW', '320i'),
    ('Hyundai', 'Sonata'), ('Hyundai', 'Tucson'),
    ('Kia', 'Sportage'), ('Kia', 'Rio'),
    ('Volkswagen', 'Polo'), ('Lada', 'Vesta'),
]
COLORS = ['Белый', 'Чёрный', 'Серебристый', 'Синий', 'Красный', 'Серый']

PART_CATEGORIES = [
    'Двигатель', 'Тормоза', 'Подвеска', 'Электрика', 'Кузов',
    'Расходники', 'Фильтры', 'Свечи', 'Аккумуляторы', 'Жидкости',
]

PART_NAMES = {
    'Двигатель': [
        ('Поршень двигателя', 'PISTON'),
        ('Коленвал', 'CRANK'),
        ('Прокладка ГБЦ', 'GASKET-H'),
        ('Ремень ГРМ', 'TIMING-BELT'),
        ('Маслосъёмные колпачки', 'OIL-SEAL'),
        ('Турбокомпрессор', 'TURBO'),
    ],
    'Тормоза': [
        ('Колодки тормозные передние', 'BRAKE-F'),
        ('Колодки тормозные задние', 'BRAKE-R'),
        ('Диск тормозной передний', 'DISC-F'),
        ('Диск тормозной задний', 'DISC-R'),
        ('Суппорт тормозной', 'CALIPER'),
        ('Шланг тормозной', 'BRAKE-HOSE'),
    ],
    'Подвеска': [
        ('Амортизатор передний', 'SHOCK-F'),
        ('Амортизатор задний', 'SHOCK-R'),
        ('Стойка стабилизатора', 'STAB'),
        ('Шаровая опора', 'BALL-JOINT'),
        ('Сайлентблок рычага', 'SLBLOCK'),
        ('Пружина подвески', 'SPRING'),
    ],
    'Электрика': [
        ('Стартер', 'STARTER'),
        ('Генератор', 'ALTERNATOR'),
        ('Датчик ABS', 'ABS-SENSOR'),
        ('Лямбда-зонд', 'O2-SENSOR'),
        ('Катушка зажигания', 'IGN-COIL'),
        ('Блок управления двигателем', 'ECU'),
    ],
    'Кузов': [
        ('Бампер передний', 'BUMPER-F'),
        ('Крыло переднее', 'FENDER-F'),
        ('Решётка радиатора', 'GRILLE'),
        ('Зеркало боковое', 'MIRROR'),
        ('Фара левая', 'HEADLIGHT-L'),
        ('Фара правая', 'HEADLIGHT-R'),
    ],
    'Расходники': [
        ('Щётка стеклоочистителя', 'WIPER'),
        ('Лампа H4', 'BULB-H4'),
        ('Лампа H7', 'BULB-H7'),
        ('Тосол', 'COOLANT'),
        ('Хомут', 'CLAMP'),
        ('Прокладка масляная', 'GASKET-OIL'),
    ],
    'Фильтры': [
        ('Фильтр масляный', 'FILTER-OIL'),
        ('Фильтр воздушный', 'FILTER-AIR'),
        ('Фильтр салона', 'FILTER-CAB'),
        ('Фильтр топливный', 'FILTER-FUEL'),
    ],
    'Свечи': [
        ('Свеча зажигания NGK', 'SPARK-NGK'),
        ('Свеча зажигания Bosch', 'SPARK-BOSCH'),
        ('Свеча зажигания Denso', 'SPARK-DENSO'),
        ('Свеча накаливания', 'GLOW-PLUG'),
    ],
    'Аккумуляторы': [
        ('Аккумулятор 60 А·ч', 'BAT-60'),
        ('Аккумулятор 75 А·ч', 'BAT-75'),
        ('Аккумулятор 90 А·ч', 'BAT-90'),
    ],
    'Жидкости': [
        ('Масло моторное 5W-30 (4л)', 'OIL-5W30'),
        ('Масло моторное 5W-40 (4л)', 'OIL-5W40'),
        ('Масло трансмиссионное', 'OIL-TRANS'),
        ('Жидкость тормозная DOT-4', 'BRAKE-FLUID'),
        ('Антифриз G12', 'ANTIFREEZE'),
    ],
}

PROBLEMS = [
    'Не заводится двигатель',
    'Стучит подвеска при движении',
    'Тормоза не держат, педаль проваливается',
    'Скрежет при торможении',
    'Не работает кондиционер',
    'Загорелась лампа Check Engine',
    'Гудит подшипник передней ступицы',
    'Подтекает масло из-под двигателя',
    'Не работает стартер',
    'Перегревается двигатель',
    'Плановое ТО: замена масла и фильтров',
    'Стук в рулевой колонке',
    'Не работает поворотник',
    'Вибрация на скорости свыше 100 км/ч',
    'Замена тормозных колодок и дисков',
    'Дёргается АКПП при переключении',
    'Замена ремня ГРМ',
    'Замена сцепления',
    'Нет искры на свечах',
    'Сел аккумулятор',
]

TASK_TEMPLATES = [
    'Диагностика двигателя на стенде',
    'Замена масла и масляного фильтра',
    'Замена воздушного фильтра',
    'Замена тормозных колодок',
    'Снятие и установка колеса',
    'Проверка геометрии подвески',
    'Развал-схождение',
    'Сварочные работы',
    'Электрические замеры мультиметром',
    'Замена ремня ГРМ',
    'Промывка инжектора',
    'Замена свечей зажигания',
    'Полировка фар',
    'Заправка кондиционера',
]


def make_plate(seq):
    """Make Tashkent-style plate '01 A 123 BC'."""
    letters = ['A', 'B', 'C', 'D', 'E', 'H', 'K', 'M', 'O', 'P', 'T', 'X']
    region = random.choice(['01', '10', '20', '30', '40', '50'])
    a = random.choice(letters)
    bc = random.choice(letters) + random.choice(letters)
    return f'{region} {a} {seq:03d} {bc}'


class Command(BaseCommand):
    help = 'Засеивает базу демо-данными для автосервиса (идемпотентно).'

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)
        self.stdout.write(self.style.MIGRATE_HEADING('Засев демо-данных АвтоСервис ERP...'))

        # ---- Users ----
        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Администратор', 'last_name': 'Системы',
                'is_staff': True, 'is_superuser': True, 'role': 'admin',
                'phone': '+998901111111', 'email': 'admin@autoservice.uz',
            },
        )
        admin.set_password('admin123'); admin.is_staff = True; admin.is_superuser = True
        admin.role = 'admin'; admin.save()

        reception, _ = User.objects.get_or_create(
            username='reception',
            defaults={
                'first_name': 'Зухра', 'last_name': 'Юлдашева',
                'role': 'receptionist', 'phone': '+998902222222',
                'is_staff': True,
            },
        )
        reception.set_password('admin123')
        reception.role = 'receptionist'; reception.is_staff = True; reception.save()

        mechanic_data = [
            ('mechanic1', 'Бекзод', 'Холматов', 'Двигатель и трансмиссия', Decimal('80000')),
            ('mechanic2', 'Жасур', 'Рахимов', 'Подвеска и тормоза', Decimal('75000')),
            ('mechanic3', 'Шерзод', 'Каримов', 'Электрика и диагностика', Decimal('85000')),
            ('mechanic4', 'Темур', 'Назаров', 'Кузовные работы', Decimal('70000')),
        ]
        mechanics = []
        for uname, fn, ln, spec, rate in mechanic_data:
            m, _ = User.objects.get_or_create(
                username=uname,
                defaults={
                    'first_name': fn, 'last_name': ln,
                    'role': 'mechanic', 'specialty': spec,
                    'hourly_rate': rate, 'is_staff': False,
                    'phone': f'+9989033{random.randint(10000, 99999)}',
                },
            )
            m.set_password('admin123')
            m.role = 'mechanic'; m.specialty = spec; m.hourly_rate = rate
            m.save()
            mechanics.append(m)
        self.stdout.write(f'  · Пользователей: admin, reception, {len(mechanics)} механиков')

        # ---- Customers ----
        customers = []
        for i in range(25):
            phone = f'+99890{4000000 + i}'
            fname = random.choice(RUS_FIRST)
            lname = random.choice(RUS_LAST)
            name = f'{lname} {fname}'
            cust, _ = Customer.objects.get_or_create(
                phone=phone,
                defaults={
                    'name': name,
                    'email': f'client{i}@mail.uz',
                    'company': random.choice(COMPANIES),
                    'address': f'г. Ташкент, ул. Демо, д. {i + 1}',
                },
            )
            customers.append(cust)
        self.stdout.write(f'  · Клиентов: {len(customers)}')

        # ---- Vehicles ----
        vehicles = []
        for i in range(35):
            customer = random.choice(customers)
            make, model = random.choice(CAR_MODELS)
            plate = make_plate(i + 1)
            year = random.randint(2008, 2024)
            v, _ = Vehicle.objects.get_or_create(
                plate=plate,
                defaults={
                    'customer': customer, 'make': make, 'model': model,
                    'year': year, 'color': random.choice(COLORS),
                    'mileage_km': random.randint(10000, 250000),
                    'vin': f'VIN{1000000 + i:09d}',
                },
            )
            vehicles.append(v)
        self.stdout.write(f'  · Автомобилей: {len(vehicles)}')

        # ---- Parts ----
        categories = {}
        for name in PART_CATEGORIES:
            cat, _ = PartCategory.objects.get_or_create(name=name)
            categories[name] = cat

        parts = []
        sku_seq = 0
        for cat_name, items in PART_NAMES.items():
            cat = categories[cat_name]
            for base_name, base_sku in items:
                for brand_idx, brand in enumerate(['Bosch', 'NGK', 'Mann', 'Sachs']):
                    if random.random() > 0.7 and brand_idx > 0:
                        continue
                    sku_seq += 1
                    sku = f'{base_sku}-{brand[:3].upper()}-{sku_seq:04d}'
                    qty = random.choice([0, 2, 3, 5, 10, 15, 25, 40])
                    reorder = random.choice([3, 5, 8])
                    cost = Decimal(random.randint(20000, 800000))
                    price = cost * Decimal('1.4')
                    SparePart.objects.get_or_create(
                        sku=sku,
                        defaults={
                            'name': f'{base_name} {brand}',
                            'brand': brand, 'category': cat,
                            'quantity_in_stock': qty,
                            'reorder_level': reorder,
                            'unit_cost': cost,
                            'unit_price': price,
                        },
                    )
        parts = list(SparePart.objects.all())
        low_count = sum(1 for p in parts if p.is_low_stock)
        self.stdout.write(f'  · Запчастей: {len(parts)} (низких остатков: {low_count})')

        # ---- Work orders ----
        statuses = [s[0] for s in WorkOrder.STATUS_CHOICES]
        priorities = [p[0] for p in WorkOrder.PRIORITY_CHOICES]
        now = timezone.now()

        existing_count = WorkOrder.objects.count()
        target = 40
        to_create = max(0, target - existing_count)

        created_orders = []
        for i in range(to_create):
            v = random.choice(vehicles)
            mech = random.choice(mechanics) if random.random() > 0.15 else None
            status = random.choice(statuses)
            priority = random.choices(
                priorities, weights=[1, 5, 3, 1], k=1
            )[0]
            received = now - timedelta(days=random.randint(0, 20), hours=random.randint(0, 12))
            est_cost = Decimal(random.randint(200000, 3000000))
            wo = WorkOrder.objects.create(
                vehicle=v, assigned_mechanic=mech,
                created_by=reception,
                status=status, priority=priority,
                problem_description=random.choice(PROBLEMS),
                diagnosis_notes='' if random.random() < 0.4 else 'Требуется детальная диагностика.',
                estimated_cost=est_cost,
                received_at=received,
                expected_ready_at=received + timedelta(days=random.randint(1, 5)),
                completed_at=received + timedelta(days=random.randint(1, 4)) if status in ('completed', 'delivered') else None,
                mileage_at_intake=v.mileage_km,
            )
            created_orders.append(wo)

        orders = list(WorkOrder.objects.select_related('vehicle').all())
        self.stdout.write(f'  · Заказ-нарядов: {len(orders)} (создано новых: {len(created_orders)})')

        # ---- Tasks for each order ----
        for o in orders:
            if o.tasks.exists():
                continue
            n_tasks = random.randint(2, 4)
            for idx in range(n_tasks):
                ServiceTask.objects.create(
                    workorder=o,
                    description=random.choice(TASK_TEMPLATES),
                    mechanic=o.assigned_mechanic if random.random() > 0.3 else random.choice(mechanics),
                    status=random.choice(['pending', 'in_progress', 'done', 'done']),
                    estimated_hours=Decimal(str(random.choice([0.5, 1.0, 1.5, 2.0, 3.0, 4.0]))),
                    actual_hours=Decimal(str(random.choice([0.5, 1.0, 1.5, 2.0, 3.0]))),
                    hourly_rate=o.assigned_mechanic.hourly_rate if o.assigned_mechanic else Decimal('70000'),
                    order=idx + 1,
                )

        # ---- Part usages for in-repair+ orders ----
        for o in orders:
            if o.status in ('received', 'diagnosed', 'cancelled'):
                continue
            if o.part_usages.exists():
                continue
            n_parts = random.randint(1, 3)
            chosen = random.sample(parts, min(n_parts, len(parts)))
            for part in chosen:
                qty = random.randint(1, 2)
                PartUsage.objects.create(
                    workorder=o, part=part,
                    quantity=qty, unit_price=part.unit_price,
                )

        # ---- Invoices for completed/delivered ----
        inv_created = 0
        for o in orders:
            if o.status not in ('completed', 'delivered'):
                continue
            if hasattr(o, 'invoice'):
                continue
            subtotal = o.grand_total
            if subtotal == 0:
                subtotal = Decimal('250000')
            tax = (subtotal * Decimal('0.12')).quantize(Decimal('0.01'))
            total = subtotal + tax
            paid_at = o.completed_at if o.status == 'delivered' else None
            payment = random.choice(['cash', 'card', 'transfer']) if paid_at else None
            Invoice.objects.create(
                workorder=o,
                subtotal=subtotal,
                tax_amount=tax,
                total=total,
                issued_at=o.completed_at or now,
                paid_at=paid_at,
                payment_method=payment,
            )
            inv_created += 1
        self.stdout.write(f'  · Счетов создано: {inv_created} (всего: {Invoice.objects.count()})')

        # ---- Summary ----
        self.stdout.write(self.style.SUCCESS('\nГотово!'))
        self.stdout.write('  Доступ:')
        self.stdout.write('    Администратор: admin / admin123')
        self.stdout.write('    Приёмщик:      reception / admin123')
        self.stdout.write('    Механики:      mechanic1..mechanic4 / admin123')
