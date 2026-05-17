from django.db import models
from clients.models import Client
from staff.models import Barber


class QueueEntry(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Ожидает'),
        ('being_served', 'Обслуживается'),
        ('done', 'Готово'),
        ('cancelled', 'Отменено'),
    ]
    STATUS_BADGE = {
        'waiting': 'bg-amber-100 text-amber-700',
        'being_served': 'bg-indigo-100 text-indigo-700',
        'done': 'bg-emerald-100 text-emerald-700',
        'cancelled': 'bg-rose-100 text-rose-700',
    }
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='queue_entries', verbose_name='Клиент')
    preferred_barber = models.ForeignKey(Barber, on_delete=models.SET_NULL, null=True, blank=True, related_name='preferred_queue_entries', verbose_name='Желаемый мастер')
    joined_at = models.DateTimeField('Время прихода', auto_now_add=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='waiting')
    served_by = models.ForeignKey(Barber, on_delete=models.SET_NULL, null=True, blank=True, related_name='served_queue_entries', verbose_name='Обслужил')

    class Meta:
        verbose_name = 'Запись в очереди'
        verbose_name_plural = 'Очередь'
        ordering = ['joined_at']

    def __str__(self):
        return f'{self.client} — {self.get_status_display()}'

    @property
    def badge_classes(self):
        return self.STATUS_BADGE.get(self.status, 'bg-slate-100 text-slate-700')
