from django.db import models
from django.urls import reverse


class Vehicle(models.Model):
    customer = models.ForeignKey(
        'customers.Customer', on_delete=models.CASCADE,
        related_name='vehicles', verbose_name='Клиент',
    )
    make = models.CharField('Марка', max_length=60)
    model = models.CharField('Модель', max_length=60)
    year = models.PositiveIntegerField('Год выпуска')
    plate = models.CharField('Гос. номер', max_length=20, unique=True)
    vin = models.CharField('VIN', max_length=30, blank=True)
    mileage_km = models.PositiveIntegerField('Пробег (км)', default=0)
    color = models.CharField('Цвет', max_length=40, blank=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.make} {self.model} — {self.plate}'

    def get_absolute_url(self):
        return reverse('vehicles:list')

    @property
    def display_title(self):
        return f'{self.make} {self.model} {self.year}'
