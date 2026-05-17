from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import PartCategory, SparePart


class SparePartForm(forms.ModelForm):
    class Meta:
        model = SparePart
        fields = [
            'name', 'sku', 'brand', 'category',
            'quantity_in_stock', 'reorder_level',
            'unit_cost', 'unit_price',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base = (
            'mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 '
            'text-sm shadow-sm focus:border-orange-500 focus:ring-orange-500'
        )
        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing} {base}'.strip()


@login_required
def part_list(request):
    qs = SparePart.objects.select_related('category')

    q = (request.GET.get('q') or '').strip()
    category = request.GET.get('category') or ''
    low = request.GET.get('low') or ''

    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q) | Q(brand__icontains=q))
    if category:
        qs = qs.filter(category_id=category)
    if low:
        qs = qs.filter(quantity_in_stock__lte=F('reorder_level'))

    qs = qs.order_by('name')

    context = {
        'parts': qs[:300],
        'total': qs.count(),
        'categories': PartCategory.objects.order_by('name'),
        'filter_q': q,
        'filter_category': category,
        'filter_low': low,
        'low_count': SparePart.objects.filter(quantity_in_stock__lte=F('reorder_level')).count(),
        'active_nav': 'parts',
        'page_title': 'Склад запчастей',
    }
    return render(request, 'parts/list.html', context)


@login_required
def part_detail(request, pk):
    part = get_object_or_404(SparePart.objects.select_related('category'), pk=pk)
    usages = part.usages.select_related('workorder', 'workorder__vehicle').order_by('-used_at')[:30]
    context = {
        'part': part,
        'usages': usages,
        'active_nav': 'parts',
        'page_title': part.name,
    }
    return render(request, 'parts/detail.html', context)


@login_required
def part_new(request):
    if request.method == 'POST':
        form = SparePartForm(request.POST)
        if form.is_valid():
            part = form.save()
            messages.success(request, f'Запчасть «{part.name}» добавлена.')
            return redirect('parts:detail', pk=part.pk)
    else:
        form = SparePartForm()

    context = {
        'form': form,
        'active_nav': 'parts',
        'page_title': 'Новая запчасть',
    }
    return render(request, 'parts/new.html', context)


@login_required
@require_POST
def part_adjust(request, pk):
    part = get_object_or_404(SparePart, pk=pk)
    try:
        delta = int(request.POST.get('delta') or '0')
    except ValueError:
        return HttpResponseBadRequest('Неверное значение')

    new_qty = part.quantity_in_stock + delta
    if new_qty < 0:
        new_qty = 0
    part.quantity_in_stock = new_qty
    part.save(update_fields=['quantity_in_stock'])

    if request.headers.get('HX-Request'):
        return render(request, 'partials/parts_row.html', {'part': part})

    return redirect('parts:list')
