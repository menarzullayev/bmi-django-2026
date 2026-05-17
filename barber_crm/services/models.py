from django.db import models
from django.utils.text import slugify


class ServiceCategory(models.Model):
    name = models.CharField('Название', max_length=80)
    slug = models.SlugField('Слаг', max_length=80, unique=True, blank=True)
    icon_emoji = models.CharField('Иконка', max_length=8, default='✂️')

    class Meta:
        verbose_name = 'Категория услуг'
        verbose_name_plural = 'Категории услуг'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True) or 'cat'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.icon_emoji} {self.name}'


class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services', verbose_name='Категория')
    name = models.CharField('Название', max_length=120)
    description = models.TextField('Описание', blank=True)
    duration_minutes = models.PositiveIntegerField('Длительность (мин)', default=30)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2, default=0)
    image_url = models.URLField('Изображение (URL)', blank=True)
    is_active = models.BooleanField('Активна', default=True)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['category__name', 'name']

    def __str__(self):
        return self.name
