from django.conf import settings
from django.db import models


class ServiceTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('in_progress', 'Выполняется'),
        ('done', 'Готово'),
        ('blocked', 'Заблокировано'),
    ]

    STATUS_BADGES = {
        'pending': 'bg-gray-200 text-gray-700',
        'in_progress': 'bg-orange-100 text-orange-700',
        'done': 'bg-green-100 text-green-700',
        'blocked': 'bg-red-100 text-red-700',
    }

    workorder = models.ForeignKey(
        'workorders.WorkOrder', on_delete=models.CASCADE,
        related_name='tasks', verbose_name='Заказ-наряд',
    )
    description = models.CharField('Описание работы', max_length=300)
    mechanic = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        related_name='tasks', null=True, blank=True,
        verbose_name='Механик',
        limit_choices_to={'role': 'mechanic'},
    )
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    estimated_hours = models.DecimalField('Норма часов', max_digits=5, decimal_places=2, default=0)
    actual_hours = models.DecimalField('Факт часов', max_digits=5, decimal_places=2, default=0)
    hourly_rate = models.DecimalField('Часовая ставка', max_digits=10, decimal_places=2, default=0)
    order = models.PositiveIntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Создана', auto_now_add=True)

    class Meta:
        verbose_name = 'Сервисная работа'
        verbose_name_plural = 'Сервисные работы'
        ordering = ('order', 'created_at')

    def __str__(self):
        return self.description

    @property
    def status_badge_class(self):
        return self.STATUS_BADGES.get(self.status, 'bg-gray-100 text-gray-700')

    @property
    def line_total(self):
        hours = self.actual_hours or self.estimated_hours
        return hours * (self.hourly_rate or 0)
