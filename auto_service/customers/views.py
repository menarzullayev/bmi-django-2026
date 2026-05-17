from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from .models import Customer


@login_required
def customer_list(request):
    q = (request.GET.get('q') or '').strip()
    qs = Customer.objects.annotate(
        vehicles_count=Count('vehicles', distinct=True),
        orders_count=Count('vehicles__work_orders', distinct=True),
    )
    if q:
        qs = qs.filter(
            Q(name__icontains=q) | Q(phone__icontains=q)
            | Q(company__icontains=q) | Q(email__icontains=q)
        )
    qs = qs.order_by('name')

    context = {
        'customers': qs[:200],
        'total': qs.count(),
        'filter_q': q,
        'active_nav': 'customers',
        'page_title': 'Клиенты',
    }
    return render(request, 'customers/list.html', context)


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    vehicles = customer.vehicles.all()
    orders = []
    for v in vehicles:
        for o in v.work_orders.all().order_by('-received_at'):
            orders.append(o)
    orders.sort(key=lambda o: o.received_at, reverse=True)
    context = {
        'customer': customer,
        'vehicles': vehicles,
        'orders': orders[:30],
        'active_nav': 'customers',
        'page_title': customer.name,
    }
    return render(request, 'customers/detail.html', context)
