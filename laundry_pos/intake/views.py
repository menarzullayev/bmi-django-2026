from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils import timezone

from customers.models import Customer
from catalog.models import ClothType, ServiceType, PriceRule
from .models import IntakeTicket, Garment


@login_required
def intake_new(request):
    if request.method == 'POST':
        return _handle_intake_post(request)

    return render(request, 'intake/new.html', {
        'cloth_types': ClothType.objects.all(),
        'service_types': ServiceType.objects.all(),
        'empty_row_index': 0,
    })


def _parse_decimal(value, default=Decimal('0')):
    try:
        return Decimal(str(value).replace(',', '.')) if value not in (None, '') else default
    except (InvalidOperation, ValueError):
        return default


@transaction.atomic
def _handle_intake_post(request):
    phone = request.POST.get('customer_phone', '').strip()
    full_name = request.POST.get('customer_name', '').strip()
    address = request.POST.get('customer_address', '').strip()

    if not phone or not full_name:
        messages.error(request, 'Укажите телефон и имя клиента.')
        return redirect('intake:new')

    customer, _ = Customer.objects.get_or_create(
        phone=phone,
        defaults={'full_name': full_name, 'address': address},
    )
    if not customer.full_name:
        customer.full_name = full_name
    if address and not customer.address:
        customer.address = address
    customer.save()

    pickup_method = request.POST.get('pickup_method', 'in_store')
    delivery_address = request.POST.get('delivery_address', '').strip()
    notes = request.POST.get('notes', '').strip()
    discount = _parse_decimal(request.POST.get('discount', '0'))
    ready_by_raw = request.POST.get('ready_by', '').strip()
    ready_by = None
    if ready_by_raw:
        try:
            ready_by = timezone.make_aware(timezone.datetime.fromisoformat(ready_by_raw))
        except (ValueError, TypeError):
            ready_by = None

    cloth_ids = request.POST.getlist('cloth_type[]')
    service_ids = request.POST.getlist('service_type[]')
    colors = request.POST.getlist('color[]')
    brands = request.POST.getlist('brand[]')
    g_notes = request.POST.getlist('g_notes[]')
    prices = request.POST.getlist('price[]')

    if not cloth_ids:
        messages.error(request, 'Добавьте хотя бы одну вещь.')
        return redirect('intake:new')

    ticket = IntakeTicket(
        customer=customer,
        cashier=request.user,
        pickup_method=pickup_method,
        delivery_address=delivery_address if pickup_method == 'delivery' else '',
        notes=notes,
        discount=discount,
        ready_by=ready_by,
    )
    ticket.save()

    for i, cid in enumerate(cloth_ids):
        if not cid:
            continue
        sid = service_ids[i] if i < len(service_ids) else None
        if not sid:
            continue
        price = _parse_decimal(prices[i] if i < len(prices) else '0')
        Garment.objects.create(
            ticket=ticket,
            cloth_type_id=int(cid),
            service_type_id=int(sid),
            color=colors[i] if i < len(colors) else '',
            brand=brands[i] if i < len(brands) else '',
            notes=g_notes[i] if i < len(g_notes) else '',
            price=price,
            status='received',
        )

    ticket.recalc_totals(save=True)
    messages.success(request, f'Квитанция {ticket.ticket_number} создана.')
    return redirect('tickets:detail', pk=ticket.pk)


@login_required
def customer_search(request):
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        results = Customer.objects.filter(
            phone__icontains=q
        ).union(
            Customer.objects.filter(full_name__icontains=q)
        )[:8]
    return render(request, 'partials/customer_search_results.html', {'results': results, 'q': q})


@login_required
def garment_add_row(request):
    idx = int(request.GET.get('idx', 0))
    return render(request, 'partials/garment_row.html', {
        'cloth_types': ClothType.objects.all(),
        'service_types': ServiceType.objects.all(),
        'idx': idx,
    })


@login_required
def price_lookup(request):
    cloth = request.GET.get('cloth')
    service = request.GET.get('service')
    idx = request.GET.get('idx', '0')
    price = Decimal('0')
    if cloth and service:
        rule = PriceRule.objects.filter(cloth_type_id=cloth, service_type_id=service).first()
        if rule:
            price = rule.price
    return render(request, 'partials/price_cell.html', {'price': price, 'idx': idx})
