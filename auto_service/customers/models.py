from django.db import models
from django.urls import reverse


class Customer(models.Model):
    name = models.CharField('ФИО', max_length=200)
    phone = models.CharField('Телефон', max_length=20, unique=True)
    email = models.EmailField('Email', blank=True)
    company = models.CharField('Компания', max_length=200, blank=True)
    address = models.CharField('Адрес', max_length=300, blank=True)
    notes = models.TextField('Примечания', blank=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ('-created_at',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('customers:detail', args=[self.pk])
