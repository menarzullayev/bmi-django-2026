from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from workorders.models import WorkOrder


User = get_user_model()


@login_required
def mechanic_list(request):
    week_ago = timezone.localdate() - timedelta(days=6)
    qs = User.objects.filter(role='mechanic').annotate(
        active_orders=Count(
            'assigned_orders',
            filter=Q(assigned_orders__status__in=WorkOrder.ACTIVE_STATUSES),
            distinct=True,
        ),
        completed_orders=Count(
            'assigned_orders',
            filter=Q(assigned_orders__completed_at__date__gte=week_ago),
            distinct=True,
        ),
        hours_week=Sum(
            'tasks__actual_hours',
            filter=Q(tasks__created_at__date__gte=week_ago),
        ),
    ).order_by('-active_orders', 'first_name')

    context = {
        'mechanics': qs,
        'active_nav': 'mechanics',
        'page_title': 'Механики',
    }
    return render(request, 'mechanics/list.html', context)


@login_required
def mechanic_detail(request, pk):
    mechanic = get_object_or_404(User, pk=pk, role='mechanic')
    week_ago = timezone.localdate() - timedelta(days=6)

    active_orders = WorkOrder.objects.filter(
        assigned_mechanic=mechanic,
        status__in=WorkOrder.ACTIVE_STATUSES,
    ).select_related('vehicle__customer').order_by('-received_at')

    completed_orders = WorkOrder.objects.filter(
        assigned_mechanic=mechanic,
        status__in=('completed', 'delivered'),
    ).select_related('vehicle__customer').order_by('-completed_at')[:20]

    hours_week = mechanic.tasks.filter(
        created_at__date__gte=week_ago
    ).aggregate(t=Sum('actual_hours'))['t'] or Decimal('0')

    context = {
        'mechanic': mechanic,
        'active_orders': active_orders,
        'completed_orders': completed_orders,
        'hours_week': hours_week,
        'active_nav': 'mechanics',
        'page_title': mechanic.get_full_name() or mechanic.username,
    }
    return render(request, 'mechanics/detail.html', context)
