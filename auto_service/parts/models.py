from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class PartCategory(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)
    slug = models.SlugField('Слаг', max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name = 'Категория запчастей'
        verbose_name_plural = 'Категории запчастей'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name, allow_unicode=True) or 'cat'
            self.slug = base[:120]
        super().save(*args, **kwargs)


class SparePart(models.Model):
    name = models.CharField('Наименование', max_length=200)
    sku = models.CharField('Артикул', max_length=50, unique=True)
    brand = models.CharField('Производитель', max_length=80, blank=True)
    category = models.ForeignKey(
        PartCategory, on_delete=models.PROTECT,
        related_name='parts', verbose_name='Категория',
    )
    quantity_in_stock = models.PositiveIntegerField('Остаток на складе', default=0)
    reorder_level = models.PositiveIntegerField('Точка дозаказа', default=5)
    unit_cost = models.DecimalField('Закупочная цена', max_digits=10, decimal_places=2, default=0)
    unit_price = models.DecimalField('Цена продажи', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)

    class Meta:
        verbose_name = 'Запчасть'
        verbose_name_plural = 'Запчасти'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.sku})'

    def get_absolute_url(self):
        return reverse('parts:detail', args=[self.pk])

    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_level

    @property
    def stock_value(self):
        return self.quantity_in_stock * self.unit_cost


class PartUsage(models.Model):
    workorder = models.ForeignKey(
        'workorders.WorkOrder', on_delete=models.CASCADE,
        related_name='part_usages', verbose_name='Заказ-наряд',
    )
    part = models.ForeignKey(
        SparePart, on_delete=models.PROTECT,
        related_name='usages', verbose_name='Запчасть',
    )
    quantity = models.PositiveIntegerField('Количество', default=1)
    unit_price = models.DecimalField('Цена за ед.', max_digits=10, decimal_places=2)
    used_at = models.DateTimeField('Использована', auto_now_add=True)

    class Meta:
        verbose_name = 'Использование запчасти'
        verbose_name_plural = 'Использование запчастей'
        ordering = ('-used_at',)

    def __str__(self):
        return f'{self.part.name} × {self.quantity}'

    @property
    def line_total(self):
        return self.quantity * self.unit_price
