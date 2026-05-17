from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('receptionist', 'Приёмщик'),
        ('mechanic', 'Механик'),
    ]

    role = models.CharField(
        'Роль', max_length=20, choices=ROLE_CHOICES, default='receptionist'
    )
    phone = models.CharField('Телефон', max_length=20, unique=True, blank=True, null=True)
    specialty = models.CharField('Специализация', max_length=100, blank=True)
    hourly_rate = models.DecimalField(
        'Часовая ставка', max_digits=10, decimal_places=2, default=0
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_mechanic(self):
        return self.role == 'mechanic'

    @property
    def role_badge_class(self):
        return {
            'admin': 'bg-red-100 text-red-800',
            'receptionist': 'bg-blue-100 text-blue-800',
            'mechanic': 'bg-orange-100 text-orange-800',
        }.get(self.role, 'bg-gray-100 text-gray-800')
