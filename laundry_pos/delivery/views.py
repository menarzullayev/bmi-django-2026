from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import User
from intake.models import IntakeTicket
from .models import DeliveryRoute, DeliveryAssignment


@login_required
def delivery_list(request):
    today = timezone.localdate()
    today_routes = DeliveryRoute.objects.filter(date=today).select_related('driver').prefetch_related('assignments__ticket__customer')
    upcoming = DeliveryRoute.objects.filter(date__gt=today).select_related('driver')[:20]
    past = DeliveryRoute.objects.filter(date__lt=today).select_related('driver')[:20]
    return render(request, 'delivery/list.html', {
        'today_routes': today_routes,
        'upcoming': upcoming,
        'past': past,
        'today': today,
    })


@login_required
def route_detail(request, pk):
    route = get_object_or_404(
        DeliveryRoute.objects.select_related('driver').prefetch_related('assignments__ticket__customer'),
        pk=pk,
    )
    assignments = route.assignments.all().order_by('order')
    return render(request, 'delivery/route_detail.html', {
        'route': route,
        'assignments': assignments,
    })


@login_required
def route_new(request):
    drivers = User.objects.filter(role='driver')
    ready_tickets = IntakeTicket.objects.filter(
        status='ready', pickup_method='delivery'
    ).select_related('customer').order_by('received_at')
    if request.method == 'POST':
        date_raw = request.POST.get('date', '').strip()
        driver_id = request.POST.get('driver')
        ticket_ids = request.POST.getlist('ticket_ids')
        try:
            date = timezone.datetime.fromisoformat(date_raw).date() if date_raw else timezone.localdate()
        except ValueError:
            date = timezone.localdate()
        if not driver_id:
            messages.error(request, 'Выберите водителя.')
            return redirect('delivery:route_new')
        driver = get_object_or_404(User, pk=driver_id)
        route = DeliveryRoute.objects.create(date=date, driver=driver, status='planned')
        for i, tid in enumerate(ticket_ids, start=1):
            try:
                ticket = IntakeTicket.objects.get(pk=tid)
            except IntakeTicket.DoesNotExist:
                continue
            DeliveryAssignment.objects.create(
                route=route, ticket=ticket,
                address=ticket.delivery_address or ticket.customer.address or 'Адрес не указан',
                order=i,
            )
        messages.success(request, f'Маршрут #{route.pk} создан.')
        return redirect('delivery:route_detail', pk=route.pk)
    return render(request, 'delivery/route_new.html', {
        'drivers': drivers,
        'ready_tickets': ready_tickets,
        'today': timezone.localdate(),
    })


@login_required
@require_POST
def assignment_deliver(request, pk):
    assignment = get_object_or_404(DeliveryAssignment.objects.select_related('ticket', 'route'), pk=pk)
    assignment.status = 'delivered'
    assignment.delivered_at = timezone.now()
    assignment.save(update_fields=['status', 'delivered_at'])
    ticket = assignment.ticket
    ticket.status = 'delivered'
    ticket.delivered_at = timezone.now()
    ticket.save(update_fields=['status', 'delivered_at'])
    route = assignment.route
    if all(a.status == 'delivered' for a in route.assignments.all()):
        route.status = 'completed'
        route.save(update_fields=['status'])
    if request.headers.get('HX-Request'):
        return render(request, 'partials/delivery_row.html', {'a': assignment})
    return redirect('delivery:route_detail', pk=route.pk)
