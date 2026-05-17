from django.db import models
from clients.models import Client


class LoyaltyAccount(models.Model):
    TIER_CHOICES = [
        ('bronze', 'Бронзовый'),
        ('silver', 'Серебряный'),
        ('gold', 'Золотой'),
        ('platinum', 'Платиновый'),
    ]
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='loyalty', verbose_name='Клиент')
    balance = models.PositiveIntegerField('Баланс баллов', default=0)
    tier = models.CharField('Уровень', max_length=20, choices=TIER_CHOICES, default='bronze')
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Счёт лояльности'
        verbose_name_plural = 'Счета лояльности'

    def __str__(self):
        return f'{self.client} — {self.balance} баллов'

    @property
    def tier_progress(self):
        thresholds = {'bronze': 200, 'silver': 500, 'gold': 1000, 'platinum': 2000}
        target = thresholds.get(self.tier, 200)
        pct = min(100, int((self.balance / target) * 100)) if target else 100
        return pct


class PointsTransaction(models.Model):
    account = models.ForeignKey(LoyaltyAccount, on_delete=models.CASCADE, related_name='transactions', verbose_name='Счёт')
    amount = models.IntegerField('Сумма (баллы)')
    reason = models.CharField('Причина', max_length=200)
    appointment = models.ForeignKey('bookings.Appointment', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Запись')
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Транзакция баллов'
        verbose_name_plural = 'Транзакции баллов'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.account} {self.amount:+d}'
