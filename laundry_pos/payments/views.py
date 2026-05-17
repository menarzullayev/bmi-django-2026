from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from .models import Payment


@login_required
def payment_list(request):
    qs = Payment.objects.select_related('ticket__customer', 'cashier').all()
    method = request.GET.get('method', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    if method:
        qs = qs.filter(method=method)
    if date_from:
        qs = qs.filter(paid_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(paid_at__date__lte=date_to)
    payments = list(qs[:300])
    totals = qs.aggregate(s=Sum('amount'))
    today = timezone.localdate()
    today_total = Payment.objects.filter(paid_at__date=today).aggregate(s=Sum('amount'))['s'] or Decimal('0')
    return render(request, 'payments/list.html', {
        'payments': payments,
        'total': totals['s'] or Decimal('0'),
        'today_total': today_total,
        'method_choices': Payment.METHOD_CHOICES,
        'filters': {'method': method, 'date_from': date_from, 'date_to': date_to},
    })
