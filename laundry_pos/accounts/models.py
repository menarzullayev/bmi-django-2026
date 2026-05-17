from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('cashier', 'Кассир'),
        ('operator', 'Оператор'),
        ('driver', 'Водитель'),
    ]
    role = models.CharField('Роль', max_length=20, choices=ROLE_CHOICES, default='cashier')
    phone = models.CharField('Телефон', max_length=32, blank=True)
    full_name = models.CharField('ФИО', max_length=160, blank=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.full_name or self.username

    def display_name(self):
        return self.full_name or self.get_full_name() or self.username
