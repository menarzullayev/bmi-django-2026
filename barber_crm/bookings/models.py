from datetime import timedelta

from django.db import models


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('confirmed', 'Подтверждена'),
        ('in_progress', 'Выполняется'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
        ('no_show', 'Не явился'),
    ]

    STATUS_BADGE = {
        'pending': 'bg-amber-100 text-amber-700',
        'confirmed': 'bg-indigo-100 text-indigo-700',
        'in_progress': 'bg-violet-100 text-violet-700',
        'completed': 'bg-emerald-100 text-emerald-700',
        'cancelled': 'bg-rose-100 text-rose-700',
        'no_show': 'bg-slate-200 text-slate-700',
    }

    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='appointments', verbose_name='Клиент')
    barber = models.ForeignKey('staff.Barber', on_delete=models.PROTECT, related_name='appointments', verbose_name='Мастер')
    service = models.ForeignKey('services.Service', on_delete=models.PROTECT, related_name='appointments', verbose_name='Услуга')
    start_at = models.DateTimeField('Начало')
    duration_minutes = models.PositiveIntegerField('Длительность (мин)', default=30)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField('Заметки', blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ['-start_at']

    def __str__(self):
        return f'{self.client} — {self.service} ({self.start_at:%d.%m %H:%M})'

    @property
    def end_at(self):
        return self.start_at + timedelta(minutes=self.duration_minutes)

    @property
    def badge_classes(self):
        return self.STATUS_BADGE.get(self.status, 'bg-slate-100 text-slate-700')
