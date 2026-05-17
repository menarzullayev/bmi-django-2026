import io
from decimal import Decimal
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from django.utils import timezone

import qrcode

from customers.models import Customer
from catalog.models import ClothType, ServiceType


STATUS_CHOICES = [
    ('received', 'Принято'),
    ('sorting', 'Сортировка'),
    ('washing', 'Стирка'),
    ('drying', 'Сушка'),
    ('ironing', 'Глажка'),
    ('ready', 'Готово к выдаче'),
    ('delivered', 'Выдано'),
    ('cancelled', 'Отменено'),
]

STATUS_COLORS = {
    'received': 'bg-gray-400 text-white',
    'sorting': 'bg-yellow-400 text-gray-900',
    'washing': 'bg-cyan-400 text-white',
    'drying': 'bg-orange-300 text-gray-900',
    'ironing': 'bg-pink-400 text-white',
    'ready': 'bg-green-500 text-white',
    'delivered': 'bg-emerald-700 text-white',
    'cancelled': 'bg-red-400 text-white',
}

PICKUP_CHOICES = [
    ('in_store', 'Самовывоз'),
    ('delivery', 'Доставка'),
]


class IntakeTicket(models.Model):
    ticket_number = models.CharField('Номер квитанции', max_length=24, unique=True, db_index=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='tickets', verbose_name='Клиент')
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='tickets_taken', verbose_name='Кассир')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='received', db_index=True)
    received_at = models.DateTimeField('Принято', default=timezone.now)
    ready_by = models.DateTimeField('Готово к (план)', null=True, blank=True)
    ready_at = models.DateTimeField('Готово (факт)', null=True, blank=True)
    delivered_at = models.DateTimeField('Выдано', null=True, blank=True)
    pickup_method = models.CharField('Способ получения', max_length=12, choices=PICKUP_CHOICES, default='in_store')
    delivery_address = models.CharField('Адрес доставки', max_length=255, blank=True)
    notes = models.TextField('Заметки', blank=True)
    subtotal = models.DecimalField('Сумма', max_digits=12, decimal_places=2, default=Decimal('0'))
    discount = models.DecimalField('Скидка', max_digits=12, decimal_places=2, default=Decimal('0'))
    total = models.DecimalField('Итого', max_digits=12, decimal_places=2, default=Decimal('0'))
    amount_paid = models.DecimalField('Оплачено', max_digits=12, decimal_places=2, default=Decimal('0'))
    qr_image = models.ImageField('QR код', upload_to='qr/', blank=True, null=True)

    class Meta:
        verbose_name = 'Квитанция'
        verbose_name_plural = 'Квитанции'
        ordering = ['-received_at']

    def __str__(self):
        return self.ticket_number

    @staticmethod
    def generate_ticket_number():
        today = timezone.localdate()
        prefix = f"T-{today.strftime('%Y%m%d')}"
        last = IntakeTicket.objects.filter(ticket_number__startswith=prefix).order_by('-ticket_number').first()
        seq = 1
        if last:
            try:
                seq = int(last.ticket_number.split('-')[-1]) + 1
            except (ValueError, IndexError):
                seq = 1
        return f"{prefix}-{seq:04d}"

    def recalc_totals(self, save=True):
        subtotal = sum((g.price for g in self.garments.all()), Decimal('0'))
        self.subtotal = subtotal
        self.total = max(subtotal - self.discount, Decimal('0'))
        if save:
            super().save(update_fields=['subtotal', 'total'])

    def get_qr_url(self):
        return reverse('qr:public_status', kwargs={'ticket_number': self.ticket_number})

    def build_qr_image(self, base_url='http://127.0.0.1:8767'):
        url = f"{base_url}{self.get_qr_url()}"
        qr = qrcode.QRCode(version=None, box_size=8, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white').convert('RGB')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return ContentFile(buf.getvalue(), name=f'{self.ticket_number}.png')

    def save(self, *args, **kwargs):
        new = self.pk is None
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()
        super().save(*args, **kwargs)
        if not self.qr_image:
            self.qr_image.save(f'{self.ticket_number}.png', self.build_qr_image(), save=False)
            super().save(update_fields=['qr_image'])

    @property
    def balance_due(self):
        return self.total - self.amount_paid

    @property
    def is_paid(self):
        return self.amount_paid >= self.total and self.total > 0

    def status_color(self):
        return STATUS_COLORS.get(self.status, 'bg-gray-300 text-gray-900')


class Garment(models.Model):
    ticket = models.ForeignKey(IntakeTicket, on_delete=models.CASCADE, related_name='garments', verbose_name='Квитанция')
    cloth_type = models.ForeignKey(ClothType, on_delete=models.PROTECT, verbose_name='Вид одежды')
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT, verbose_name='Услуга')
    color = models.CharField('Цвет', max_length=40, blank=True)
    brand = models.CharField('Бренд', max_length=80, blank=True)
    notes = models.CharField('Примечание', max_length=200, blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2, default=Decimal('0'))
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='received')

    class Meta:
        verbose_name = 'Вещь'
        verbose_name_plural = 'Вещи'

    def __str__(self):
        return f'{self.cloth_type.name} — {self.service_type.name}'
