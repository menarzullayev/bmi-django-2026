from decimal import Decimal
from django.db import models


class Customer(models.Model):
    phone = models.CharField('Телефон', max_length=32, unique=True, db_index=True)
    full_name = models.CharField('ФИО', max_length=160)
    address = models.CharField('Адрес', max_length=255, blank=True)
    notes = models.TextField('Заметки', blank=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    total_spent = models.DecimalField('Сумма покупок', max_digits=12, decimal_places=2, default=Decimal('0'))

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name} ({self.phone})'
