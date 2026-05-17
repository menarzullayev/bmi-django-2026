from django.conf import settings
from django.db import models


class Client(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_profile', verbose_name='Пользователь')
    birthday = models.DateField('День рождения', null=True, blank=True)
    preferred_barber = models.ForeignKey('staff.Barber', on_delete=models.SET_NULL, null=True, blank=True, related_name='regulars', verbose_name='Любимый мастер')
    notes = models.TextField('Заметки', blank=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['-created_at']

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def phone(self):
        return self.user.phone
