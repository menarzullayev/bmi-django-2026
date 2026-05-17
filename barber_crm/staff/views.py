from datetime import timedelta

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from bookings.models import Appointment
from clients.models import Client
from services.models import Service, ServiceCategory
from .models import Barber


def _is_staff(user):
    return user.is_authenticated and getattr(user, 'is_staff_role', False)


@login_required
@user_passes_test(_is_staff)
def schedule(request):
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    days = [week_start + timedelta(days=i) for i in range(7)]
    appts = Appointment.objects.filter(
        start_at__date__gte=days[0],
        start_at__date__lte=days[-1],
    ).select_related('client__user', 'barber__user', 'service').order_by('start_at')
    grid = {d: [] for d in days}
    for a in appts:
        d = timezone.localtime(a.start_at).date()
        if d in grid:
            grid[d].append(a)
    return render(request, 'dashboard/schedule.html', {
        'days': days,
        'grid': grid,
        'barbers': Barber.objects.filter(is_active=True).select_related('user'),
    })


@login_required
@user_passes_test(_is_staff)
def clients_list(request):
    q = (request.GET.get('q') or '').strip()
    clients = Client.objects.select_related('user', 'preferred_barber__user').all()
    if q:
        clients = clients.filter(
            Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(user__phone__icontains=q)
            | Q(user__username__icontains=q)
        )
    clients = clients.distinct()[:200]
    return render(request, 'dashboard/clients.html', {'clients': clients, 'q': q})


@login_required
@user_passes_test(_is_staff)
def services_management(request):
    return render(request, 'dashboard/services.html', {
        'services': Service.objects.select_related('category').all(),
        'categories': ServiceCategory.objects.all(),
    })
