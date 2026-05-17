from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import ClothType, ServiceType, PriceRule


@login_required
def pricing_matrix(request):
    cloth_types = list(ClothType.objects.all())
    service_types = list(ServiceType.objects.all())
    rules = {(r.cloth_type_id, r.service_type_id): r for r in PriceRule.objects.all()}
    rows = []
    for ct in cloth_types:
        cells = []
        for st in service_types:
            rule = rules.get((ct.id, st.id))
            cells.append({'cloth': ct, 'service': st, 'price': rule.price if rule else None})
        rows.append({'cloth': ct, 'cells': cells})
    return render(request, 'catalog/pricing.html', {
        'cloth_types': cloth_types,
        'service_types': service_types,
        'rows': rows,
    })


@login_required
def price_cell(request, cloth_id, service_id):
    rule = PriceRule.objects.filter(cloth_type_id=cloth_id, service_type_id=service_id).first()
    return render(request, 'partials/price_matrix_cell.html', {
        'cloth_id': cloth_id, 'service_id': service_id,
        'price': rule.price if rule else None,
    })


@login_required
def price_cell_edit(request, cloth_id, service_id):
    rule = PriceRule.objects.filter(cloth_type_id=cloth_id, service_type_id=service_id).first()
    return render(request, 'partials/price_matrix_cell_edit.html', {
        'cloth_id': cloth_id, 'service_id': service_id,
        'price': rule.price if rule else '',
    })


@login_required
@require_POST
def price_cell_save(request, cloth_id, service_id):
    raw = request.POST.get('price', '').strip().replace(',', '.')
    try:
        price = Decimal(raw) if raw else None
    except InvalidOperation:
        price = None
    cloth = get_object_or_404(ClothType, pk=cloth_id)
    service = get_object_or_404(ServiceType, pk=service_id)
    if price is None or price <= 0:
        PriceRule.objects.filter(cloth_type=cloth, service_type=service).delete()
        new_price = None
    else:
        rule, _ = PriceRule.objects.update_or_create(
            cloth_type=cloth, service_type=service,
            defaults={'price': price},
        )
        new_price = rule.price
    return render(request, 'partials/price_matrix_cell.html', {
        'cloth_id': cloth_id, 'service_id': service_id, 'price': new_price,
    })


@login_required
def cloth_types(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category = request.POST.get('category', 'other')
        icon = request.POST.get('default_icon', '').strip() or '👕'
        if name:
            ClothType.objects.get_or_create(name=name, defaults={'category': category, 'default_icon': icon})
            messages.success(request, f'Добавлен вид одежды «{name}».')
        return redirect('catalog:cloth_types')
    return render(request, 'catalog/cloth_types.html', {
        'cloth_types': ClothType.objects.all(),
        'category_choices': ClothType.CATEGORY_CHOICES,
    })


@login_required
def service_types(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip() or name.lower().replace(' ', '_')
        description = request.POST.get('description', '').strip()
        if name:
            ServiceType.objects.get_or_create(name=name, defaults={'code': code, 'description': description})
            messages.success(request, f'Добавлена услуга «{name}».')
        return redirect('catalog:service_types')
    return render(request, 'catalog/service_types.html', {
        'service_types': ServiceType.objects.all(),
    })
