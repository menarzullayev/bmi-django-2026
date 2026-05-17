from decimal import Decimal

from django.db import models
from django.urls import reverse
from django.utils import timezone


class Invoice(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Наличные'),
        ('card', 'Карта'),
        ('transfer', 'Перевод'),
    ]

    workorder = models.OneToOneField(
        'workorders.WorkOrder', on_delete=models.CASCADE,
        related_name='invoice', verbose_name='Заказ-наряд',
    )
    invoice_number = models.CharField('Номер счёта', max_length=30, unique=True, blank=True)
    subtotal = models.DecimalField('Сумма без НДС', max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField('НДС', max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField('Итого', max_digits=12, decimal_places=2, default=0)
    issued_at = models.DateTimeField('Выставлен', default=timezone.now)
    paid_at = models.DateTimeField('Оплачен', null=True, blank=True)
    payment_method = models.CharField(
        'Способ оплаты', max_length=20, choices=PAYMENT_CHOICES, null=True, blank=True,
    )

    class Meta:
        verbose_name = 'Счёт'
        verbose_name_plural = 'Счета'
        ordering = ('-issued_at',)

    def __str__(self):
        return self.invoice_number or f'Счёт #{self.pk}'

    def get_absolute_url(self):
        return reverse('billing:detail', args=[self.pk])

    def save(self, *args, **kwargs):
        creating = self.pk is None
        if not self.invoice_number:
            self.invoice_number = f'INV-{timezone.now().strftime("%Y%m%d")}-TEMP'
        # Recalculate totals from subtotal + tax if not preset
        if self.subtotal and not self.total:
            self.total = (self.subtotal + (self.tax_amount or Decimal('0')))
        super().save(*args, **kwargs)
        if creating and self.invoice_number.endswith('-TEMP'):
            self.invoice_number = f'INV-{self.issued_at.strftime("%Y%m%d")}-{self.pk:04d}'
            super().save(update_fields=['invoice_number'])

    @property
    def is_paid(self):
        return self.paid_at is not None

    @property
    def status_label(self):
        return 'Оплачен' if self.is_paid else 'Не оплачен'

    @property
    def status_badge_class(self):
        return 'bg-green-100 text-green-700' if self.is_paid else 'bg-yellow-100 text-yellow-700'
