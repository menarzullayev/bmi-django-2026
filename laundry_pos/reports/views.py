from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.shortcuts import render
from django.utils import timezone

from intake.models import IntakeTicket, STATUS_CHOICES
from payments.models import Payment


@login_required
def daily_report(request):
    date_raw = request.GET.get('date', '').strip()
    try:
        date = timezone.datetime.fromisoformat(date_raw).date() if date_raw else timezone.localdate()
    except ValueError:
        date = timezone.localdate()

    tickets_qs = IntakeTicket.objects.filter(received_at__date=date)
    payments_qs = Payment.objects.filter(paid_at__date=date).select_related('cashier', 'ticket__customer')

    tickets_count = tickets_qs.count()
    payments_total = payments_qs.aggregate(s=Sum('amount'))['s'] or Decimal('0')
    tickets_subtotal = tickets_qs.aggregate(s=Sum('total'))['s'] or Decimal('0')

    by_status_map = {row['status']: row['c'] for row in tickets_qs.values('status').annotate(c=Count('id'))}
    status_labels = dict(STATUS_CHOICES)
    by_status = [{'code': k, 'label': status_labels.get(k, k), 'count': v} for k, v in by_status_map.items()]

    by_method = payments_qs.values('method').annotate(s=Sum('amount'), c=Count('id'))
    method_labels = dict(Payment.METHOD_CHOICES)
    by_method = [{'method': m['method'], 'label': method_labels.get(m['method'], m['method']),
                  'sum': m['s'] or Decimal('0'), 'count': m['c']} for m in by_method]

    by_cashier = payments_qs.values('cashier__username', 'cashier__full_name').annotate(
        s=Sum('amount'), c=Count('id')
    )
    by_cashier = [{'name': row['cashier__full_name'] or row['cashier__username'],
                   'sum': row['s'] or Decimal('0'), 'count': row['c']} for row in by_cashier]

    return render(request, 'reports/daily.html', {
        'date': date,
        'tickets_count': tickets_count,
        'tickets_subtotal': tickets_subtotal,
        'payments_total': payments_total,
        'by_status': by_status,
        'by_method': by_method,
        'by_cashier': by_cashier,
        'payments': payments_qs[:100],
    })
