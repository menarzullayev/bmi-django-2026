from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from parts.models import PartUsage, SparePart
from workflow.models import ServiceTask

from .forms import WorkOrderForm
from .models import WorkOrder


User = get_user_model()


@login_required
def order_list(request):
    qs = WorkOrder.objects.select_related(
        'vehicle', 'vehicle__customer', 'assigned_mechanic',
    )

    status = request.GET.get('status') or ''
    priority = request.GET.get('priority') or ''
    mechanic = request.GET.get('mechanic') or ''
    q = (request.GET.get('q') or '').strip()

    if status:
        qs = qs.filter(status=status)
    if priority:
        qs = qs.filter(priority=priority)
    if mechanic:
        qs = qs.filter(assigned_mechanic_id=mechanic)
    if q:
        qs = qs.filter(
            order_number__icontains=q,
        ) | qs.filter(vehicle__plate__icontains=q) | qs.filter(vehicle__customer__name__icontains=q)
        qs = qs.distinct()

    qs = qs.order_by('-received_at')

    context = {
        'orders': qs[:200],
        'total': qs.count(),
        'statuses': WorkOrder.STATUS_CHOICES,
        'priorities': WorkOrder.PRIORITY_CHOICES,
        'mechanics_all': User.objects.filter(role='mechanic').order_by('first_name'),
        'filter_status': status,
        'filter_priority': priority,
        'filter_mechanic': mechanic,
        'filter_q': q,
        'active_nav': 'orders',
        'page_title': 'Заказ-наряды',
    }
    return render(request, 'orders/list.html', context)


@login_required
def order_detail(request, pk):
    order = get_object_or_404(
        WorkOrder.objects.select_related('vehicle__customer', 'assigned_mechanic', 'created_by'),
        pk=pk,
    )
    tasks = order.tasks.select_related('mechanic').all()
    part_usages = order.part_usages.select_related('part').all()

    context = {
        'order': order,
        'tasks': tasks,
        'part_usages': part_usages,
        'mechanics_all': User.objects.filter(role='mechanic').order_by('first_name'),
        'parts_all': SparePart.objects.order_by('name'),
        'active_nav': 'orders',
        'page_title': order.order_number,
    }
    return render(request, 'orders/detail.html', context)


@login_required
def order_new(request):
    if request.method == 'POST':
        form = WorkOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user
            order.received_at = timezone.now()
            order.save()
            messages.success(request, f'Заказ-наряд {order.order_number} создан.')
            return redirect('workorders:detail', pk=order.pk)
    else:
        form = WorkOrderForm()

    context = {
        'form': form,
        'active_nav': 'orders',
        'page_title': 'Новый заказ-наряд',
    }
    return render(request, 'orders/new.html', context)


@login_required
@require_POST
def order_transition(request, pk):
    order = get_object_or_404(WorkOrder, pk=pk)
    target = request.POST.get('target') or order.next_status
    if not target:
        if request.headers.get('HX-Request'):
            return _render_kanban_card(request, order)
        return redirect('workorders:detail', pk=order.pk)

    if target not in dict(WorkOrder.STATUS_CHOICES):
        return HttpResponseBadRequest('Unknown status')

    order.status = target
    if target in ('completed', 'delivered') and not order.completed_at:
        order.completed_at = timezone.now()
    order.save()

    if request.headers.get('HX-Request'):
        # If the request came from the kanban board, swap out the card
        if request.POST.get('from') == 'kanban':
            return _render_kanban_card(request, order)
        return render(request, 'orders/_status_section.html', {'order': order})

    messages.success(request, f'Статус заказа изменён: {order.get_status_display()}.')
    return redirect('workorders:detail', pk=order.pk)


def _render_kanban_card(request, order):
    return render(request, 'partials/kanban_card.html', {'order': order})


@login_required
@require_POST
def order_add_task(request, pk):
    order = get_object_or_404(WorkOrder, pk=pk)
    description = (request.POST.get('description') or '').strip()
    if not description:
        return HttpResponseBadRequest('Описание обязательно')

    mechanic_id = request.POST.get('mechanic') or None
    estimated_hours = Decimal(request.POST.get('estimated_hours') or '0')
    hourly_rate = Decimal(request.POST.get('hourly_rate') or '0')

    task = ServiceTask.objects.create(
        workorder=order,
        description=description,
        mechanic_id=mechanic_id or None,
        estimated_hours=estimated_hours,
        hourly_rate=hourly_rate,
        order=order.tasks.count() + 1,
    )

    if request.headers.get('HX-Request'):
        return render(request, 'partials/task_row.html', {'task': task, 'order': order})
    return redirect('workorders:detail', pk=order.pk)


@login_required
@require_POST
@transaction.atomic
def order_add_part(request, pk):
    order = get_object_or_404(WorkOrder, pk=pk)
    part_id = request.POST.get('part')
    quantity = int(request.POST.get('quantity') or '1')

    part = get_object_or_404(SparePart, pk=part_id)
    if quantity < 1:
        quantity = 1
    if part.quantity_in_stock < quantity:
        if request.headers.get('HX-Request'):
            return render(request, 'partials/order_part_error.html', {
                'message': f'Недостаточно на складе: доступно {part.quantity_in_stock}',
            })
        messages.error(request, 'Недостаточно запчастей на складе.')
        return redirect('workorders:detail', pk=order.pk)

    usage = PartUsage.objects.create(
        workorder=order, part=part, quantity=quantity, unit_price=part.unit_price,
    )
    part.quantity_in_stock -= quantity
    part.save(update_fields=['quantity_in_stock'])

    if request.headers.get('HX-Request'):
        return render(request, 'partials/order_part_row.html', {'usage': usage, 'order': order})
    return redirect('workorders:detail', pk=order.pk)


@login_required
def kanban(request):
    statuses = [s for s in WorkOrder.STATUS_CHOICES if s[0] != 'cancelled']
    columns = []
    for code, label in statuses:
        orders = WorkOrder.objects.filter(status=code).select_related(
            'vehicle__customer', 'assigned_mechanic',
        ).order_by('-received_at')
        columns.append({
            'code': code,
            'label': label,
            'orders': orders,
            'count': orders.count(),
        })

    context = {
        'columns': columns,
        'active_nav': 'kanban',
        'page_title': 'Канбан-доска',
    }
    return render(request, 'orders/kanban.html', context)
