from django.conf import settings
from django.db import models
from django.utils import timezone


class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Наличные'),
        ('card', 'Карта'),
        ('transfer', 'Перевод'),
    ]
    ticket = models.ForeignKey('intake.IntakeTicket', on_delete=models.CASCADE, related_name='payments', verbose_name='Квитанция')
    amount = models.DecimalField('Сумма', max_digits=12, decimal_places=2)
    method = models.CharField('Метод', max_length=12, choices=METHOD_CHOICES, default='cash')
    paid_at = models.DateTimeField('Оплачено', default=timezone.now)
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='Кассир')
    note = models.CharField('Заметка', max_length=200, blank=True)

    class Meta:
        verbose_name = 'Оплата'
        verbose_name_plural = 'Оплаты'
        ordering = ['-paid_at']

    def __str__(self):
        return f'{self.amount} ({self.get_method_display()})'
