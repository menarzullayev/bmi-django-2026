from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from intake.models import IntakeTicket
from payments.models import Payment


@login_required
def dashboard(request):
    today = timezone.localdate()
    today_qs = IntakeTicket.objects.filter(received_at__date=today)
    payments_today = Payment.objects.filter(paid_at__date=today)

    stats = {
        'count_today': today_qs.count(),
        'revenue_today': payments_today.aggregate(s=Sum('amount'))['s'] or Decimal('0'),
        'ready_count': IntakeTicket.objects.filter(status='ready').count(),
        'in_progress': IntakeTicket.objects.filter(
            status__in=['received', 'sorting', 'washing', 'drying', 'ironing']
        ).count(),
    }

    by_status = (
        IntakeTicket.objects.values('status')
        .annotate(c=Count('id'))
        .order_by()
    )
    status_map = {row['status']: row['c'] for row in by_status}
    status_order = ['received', 'sorting', 'washing', 'drying', 'ironing', 'ready', 'delivered']
    status_labels = dict(IntakeTicket._meta.get_field('status').choices)
    status_rows = [
        {'code': s, 'label': status_labels.get(s, s), 'count': status_map.get(s, 0)}
        for s in status_order
    ]

    recent = IntakeTicket.objects.select_related('customer', 'cashier').order_by('-received_at')[:10]
    ready_tickets = IntakeTicket.objects.filter(status='ready').select_related('customer')[:8]

    return render(request, 'pos/dashboard.html', {
        'stats': stats,
        'status_rows': status_rows,
        'recent': recent,
        'ready_tickets': ready_tickets,
        'today': today,
    })


def public_status(request, ticket_number):
    ticket = get_object_or_404(
        IntakeTicket.objects.select_related('customer').prefetch_related('garments__cloth_type', 'garments__service_type'),
        ticket_number=ticket_number,
    )
    return render(request, 'qr/public_status.html', {'ticket': ticket})
