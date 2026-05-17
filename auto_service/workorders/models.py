from decimal import Decimal

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class WorkOrder(models.Model):
    STATUS_CHOICES = [
        ('received', 'Принят'),
        ('diagnosed', 'Диагностирован'),
        ('awaiting_parts', 'Ожидание запчастей'),
        ('in_repair', 'В ремонте'),
        ('quality_check', 'Контроль качества'),
        ('completed', 'Готов'),
        ('delivered', 'Выдан'),
        ('cancelled', 'Отменён'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('normal', 'Обычный'),
        ('high', 'Высокий'),
        ('urgent', 'Срочный'),
    ]

    # status → tailwind badge classes (industrial palette)
    STATUS_BADGES = {
        'received': 'bg-gray-200 text-gray-800',
        'diagnosed': 'bg-blue-100 text-blue-800',
        'awaiting_parts': 'bg-yellow-100 text-yellow-800',
        'in_repair': 'bg-orange-100 text-orange-800',
        'quality_check': 'bg-purple-100 text-purple-800',
        'completed': 'bg-green-100 text-green-800',
        'delivered': 'bg-emerald-100 text-emerald-800',
        'cancelled': 'bg-red-100 text-red-800',
    }

    PRIORITY_BADGES = {
        'low': 'bg-gray-100 text-gray-700',
        'normal': 'bg-blue-100 text-blue-700',
        'high': 'bg-orange-100 text-orange-700',
        'urgent': 'bg-red-100 text-red-700',
    }

    # Linear transition graph used by the "next stage" button.
    NEXT_STATUS = {
        'received': 'diagnosed',
        'diagnosed': 'awaiting_parts',
        'awaiting_parts': 'in_repair',
        'in_repair': 'quality_check',
        'quality_check': 'completed',
        'completed': 'delivered',
    }

    ACTIVE_STATUSES = (
        'received', 'diagnosed', 'awaiting_parts', 'in_repair', 'quality_check', 'completed',
    )

    vehicle = models.ForeignKey(
        'vehicles.Vehicle', on_delete=models.PROTECT,
        related_name='work_orders', verbose_name='Автомобиль',
    )
    assigned_mechanic = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        related_name='assigned_orders', null=True, blank=True,
        verbose_name='Назначенный механик',
        limit_choices_to={'role': 'mechanic'},
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='created_orders', verbose_name='Создал',
    )
    status = models.CharField(
        'Статус', max_length=20, choices=STATUS_CHOICES, default='received',
    )
    priority = models.CharField(
        'Приоритет', max_length=10, choices=PRIORITY_CHOICES, default='normal',
    )
    problem_description = models.TextField('Описание проблемы')
    diagnosis_notes = models.TextField('Заметки по диагностике', blank=True)
    estimated_cost = models.DecimalField(
        'Предв. стоимость', max_digits=12, decimal_places=2, default=0,
    )
    actual_cost = models.DecimalField(
        'Итоговая стоимость', max_digits=12, decimal_places=2, default=0,
    )
    received_at = models.DateTimeField('Принят', default=timezone.now)
    expected_ready_at = models.DateTimeField('Ожидаемая готовность', null=True, blank=True)
    completed_at = models.DateTimeField('Завершён', null=True, blank=True)
    order_number = models.CharField('Номер заказ-наряда', max_length=30, unique=True, blank=True)
    mileage_at_intake = models.PositiveIntegerField('Пробег при приёмке', default=0)

    class Meta:
        verbose_name = 'Заказ-наряд'
        verbose_name_plural = 'Заказ-наряды'
        ordering = ('-received_at',)

    def __str__(self):
        return self.order_number or f'Заказ #{self.pk}'

    def get_absolute_url(self):
        return reverse('workorders:detail', args=[self.pk])

    def save(self, *args, **kwargs):
        creating = self.pk is None
        if not self.order_number:
            # placeholder; corrected below when we know the pk
            self.order_number = f'WO-{timezone.now().strftime("%Y%m%d")}-TEMP'
        super().save(*args, **kwargs)
        if creating and self.order_number.endswith('-TEMP'):
            self.order_number = f'WO-{self.received_at.strftime("%Y%m%d")}-{self.pk:04d}'
            super().save(update_fields=['order_number'])

    @property
    def status_badge_class(self):
        return self.STATUS_BADGES.get(self.status, 'bg-gray-100 text-gray-700')

    @property
    def priority_badge_class(self):
        return self.PRIORITY_BADGES.get(self.priority, 'bg-gray-100 text-gray-700')

    @property
    def next_status(self):
        return self.NEXT_STATUS.get(self.status)

    @property
    def can_advance(self):
        return self.next_status is not None

    @property
    def labor_total(self):
        total = Decimal('0')
        for task in self.tasks.all():
            total += (task.actual_hours or task.estimated_hours or Decimal('0')) * (task.hourly_rate or Decimal('0'))
        return total

    @property
    def parts_total(self):
        total = Decimal('0')
        for usage in self.part_usages.all():
            total += usage.quantity * usage.unit_price
        return total

    @property
    def grand_total(self):
        return self.labor_total + self.parts_total

    @property
    def customer(self):
        return self.vehicle.customer
