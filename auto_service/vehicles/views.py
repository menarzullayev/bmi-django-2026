from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render

from .models import Vehicle


@login_required
def vehicle_list(request):
    q = (request.GET.get('q') or '').strip()
    qs = Vehicle.objects.select_related('customer').annotate(
        orders_count=Count('work_orders', distinct=True),
    )
    if q:
        qs = qs.filter(
            Q(plate__icontains=q) | Q(make__icontains=q)
            | Q(model__icontains=q) | Q(customer__name__icontains=q)
            | Q(vin__icontains=q)
        )
    qs = qs.order_by('-created_at')

    context = {
        'vehicles': qs[:200],
        'total': qs.count(),
        'filter_q': q,
        'active_nav': 'vehicles',
        'page_title': 'Автомобили',
    }
    return render(request, 'vehicles/list.html', context)
