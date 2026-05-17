from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('client', 'Клиент'),
        ('barber', 'Мастер'),
        ('admin', 'Администратор'),
    ]
    phone = models.CharField('Телефон', max_length=20, unique=True)
    role = models.CharField('Роль', max_length=20, choices=ROLE_CHOICES, default='client')
    avatar = models.ImageField('Аватар', upload_to='avatars/', null=True, blank=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def initials(self):
        first = (self.first_name or self.username[:1] or 'U').strip()[:1]
        last = (self.last_name or '').strip()[:1]
        return (first + last).upper() or 'U'

    @property
    def is_staff_role(self):
        return self.role in ('barber', 'admin') or self.is_superuser
