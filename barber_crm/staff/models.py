from django.conf import settings
from django.db import models


class Barber(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='barber_profile', verbose_name='Пользователь')
    specialization = models.CharField('Специализация', max_length=120, blank=True)
    experience_years = models.PositiveIntegerField('Опыт (лет)', default=1)
    rating = models.DecimalField('Рейтинг', max_digits=4, decimal_places=2, default=5.0)
    bio = models.TextField('О мастере', blank=True)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Мастер'
        verbose_name_plural = 'Мастера'
        ordering = ['-rating']

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
