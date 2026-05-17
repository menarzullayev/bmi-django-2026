from django.db import models


class ClothType(models.Model):
    CATEGORY_CHOICES = [
        ('top', 'Верх'),
        ('bottom', 'Низ'),
        ('outerwear', 'Верхняя одежда'),
        ('bedding', 'Постельное'),
        ('other', 'Прочее'),
    ]
    name = models.CharField('Наименование', max_length=80, unique=True)
    category = models.CharField('Категория', max_length=20, choices=CATEGORY_CHOICES, default='other')
    default_icon = models.CharField('Иконка', max_length=4, default='👕')

    class Meta:
        verbose_name = 'Вид одежды'
        verbose_name_plural = 'Виды одежды'
        ordering = ['category', 'name']

    def __str__(self):
        return f'{self.default_icon} {self.name}'


class ServiceType(models.Model):
    name = models.CharField('Наименование', max_length=80, unique=True)
    code = models.SlugField('Код', max_length=40, unique=True)
    description = models.CharField('Описание', max_length=200, blank=True)

    class Meta:
        verbose_name = 'Вид услуги'
        verbose_name_plural = 'Виды услуг'
        ordering = ['name']

    def __str__(self):
        return self.name


class PriceRule(models.Model):
    cloth_type = models.ForeignKey(ClothType, on_delete=models.CASCADE, verbose_name='Вид одежды', related_name='prices')
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, verbose_name='Вид услуги', related_name='prices')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Прайс'
        verbose_name_plural = 'Прайс-лист'
        unique_together = [('cloth_type', 'service_type')]
        ordering = ['cloth_type__name', 'service_type__name']

    def __str__(self):
        return f'{self.cloth_type.name} × {self.service_type.name} = {self.price}'
