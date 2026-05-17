from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Q, Sum
from django.shortcuts import render
from django.utils import timezone

from billing.models import Invoice
from parts.models import SparePart
from workorders.models import WorkOrder


User = get_user_model()


@login_required
def dashboard(request):
    today = timezone.localdate()
    week_ago = today - timedelta(days=6)

    active = WorkOrder.objects.filter(status__in=WorkOrder.ACTIVE_STATUSES)
    completed_today = WorkOrder.objects.filter(
        status__in=('completed', 'delivered'), completed_at__date=today,
    )

    revenue_today = Invoice.objects.filter(issued_at__date=today).aggregate(
        total=Sum('total')
    )['total'] or Decimal('0')
    revenue_week = Invoice.objects.filter(issued_at__date__gte=week_ago).aggregate(
        total=Sum('total')
    )['total'] or Decimal('0')

    mechanics = User.objects.filter(role='mechanic').annotate(
        active_load=Count(
            'assigned_orders',
            filter=Q(assigned_orders__status__in=WorkOrder.ACTIVE_STATUSES),
        ),
    ).order_by('-active_load')[:6]

    low_stock = SparePart.objects.filter(
        quantity_in_stock__lte=F('reorder_level')
    ).order_by('quantity_in_stock')[:8]

    status_breakdown = list(
        WorkOrder.objects.values('status').annotate(c=Count('id')).order_by('status')
    )
    status_labels_map = dict(WorkOrder.STATUS_CHOICES)
    status_chart = {
        'labels': [status_labels_map.get(row['status'], row['status']) for row in status_breakdown],
        'data': [row['c'] for row in status_breakdown],
    }

    trend_labels = []
    trend_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        s = Invoice.objects.filter(issued_at__date=d).aggregate(t=Sum('total'))['t'] or Decimal('0')
        trend_labels.append(d.strftime('%d.%m'))
        trend_data.append(float(s))

    recent_orders = WorkOrder.objects.select_related(
        'vehicle', 'vehicle__customer', 'assigned_mechanic',
    ).order_by('-received_at')[:8]

    context = {
        'kpi_active': active.count(),
        'kpi_completed_today': completed_today.count(),
        'kpi_revenue_today': revenue_today,
        'kpi_revenue_week': revenue_week,
        'kpi_low_stock': SparePart.objects.filter(quantity_in_stock__lte=F('reorder_level')).count(),
        'mechanics': mechanics,
        'low_stock_parts': low_stock,
        'status_chart': status_chart,
        'trend_labels': trend_labels,
        'trend_data': trend_data,
        'recent_orders': recent_orders,
        'active_nav': 'dashboard',
        'page_title': 'Панель управления',
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def reports_daily(request):
    today = timezone.localdate()
    week_ago = today - timedelta(days=6)

    days = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        orders = WorkOrder.objects.filter(received_at__date=d).count()
        completed = WorkOrder.objects.filter(completed_at__date=d).count()
        revenue = Invoice.objects.filter(issued_at__date=d).aggregate(t=Sum('total'))['t'] or 0
        days.append({
            'date': d,
            'orders': orders,
            'completed': completed,
            'revenue': revenue,
        })

    totals = {
        'orders': sum(d['orders'] for d in days),
        'completed': sum(d['completed'] for d in days),
        'revenue': sum(d['revenue'] for d in days),
    }

    by_mechanic = User.objects.filter(role='mechanic').annotate(
        total_done=Count(
            'assigned_orders',
            filter=Q(assigned_orders__completed_at__date__gte=week_ago),
        ),
    ).order_by('-total_done')

    context = {
        'days': days,
        'totals': totals,
        'by_mechanic': by_mechanic,
        'active_nav': 'reports',
        'page_title': 'Отчёты',
    }
    return render(request, 'reports/daily.html', context)
