from django.conf import settings
from django.db import models


class DeliveryRoute(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Запланирован'),
        ('in_progress', 'В пути'),
        ('completed', 'Завершён'),
    ]
    date = models.DateField('Дата', db_index=True)
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='routes', verbose_name='Водитель')
    status = models.CharField('Статус', max_length=12, choices=STATUS_CHOICES, default='planned')

    class Meta:
        verbose_name = 'Маршрут'
        verbose_name_plural = 'Маршруты доставки'
        ordering = ['-date']

    def __str__(self):
        return f'Маршрут {self.date} — {self.driver}'


class DeliveryAssignment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('delivered', 'Доставлено'),
        ('failed', 'Не доставлено'),
    ]
    route = models.ForeignKey(DeliveryRoute, on_delete=models.CASCADE, related_name='assignments', verbose_name='Маршрут')
    ticket = models.ForeignKey('intake.IntakeTicket', on_delete=models.PROTECT, related_name='deliveries', verbose_name='Квитанция')
    address = models.CharField('Адрес', max_length=255)
    time_window_start = models.TimeField('Окно с', null=True, blank=True)
    time_window_end = models.TimeField('Окно по', null=True, blank=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)
    status = models.CharField('Статус', max_length=12, choices=STATUS_CHOICES, default='pending')
    delivered_at = models.DateTimeField('Доставлено', null=True, blank=True)

    class Meta:
        verbose_name = 'Задание доставки'
        verbose_name_plural = 'Задания доставки'
        ordering = ['order']

    def __str__(self):
        return f'{self.ticket.ticket_number} → {self.address}'
