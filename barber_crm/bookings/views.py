from datetime import datetime, timedelta, date as date_cls

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from services.models import Service
from staff.models import Barber
from clients.models import Client
from .models import Appointment


WORK_START_HOUR = 10
WORK_END_HOUR = 20
SLOT_MINUTES = 30


def _parse_date(value):
    if not value:
        return timezone.localdate()
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return timezone.localdate()


def booking_calendar(request):
    services = Service.objects.filter(is_active=True).select_related('category')
    barbers = Barber.objects.filter(is_active=True).select_related('user')
    today = timezone.localdate()
    return render(request, 'public/booking_calendar.html', {
        'services': services,
        'barbers': barbers,
        'today': today.strftime('%Y-%m-%d'),
        'min_date': today.strftime('%Y-%m-%d'),
        'max_date': (today + timedelta(days=30)).strftime('%Y-%m-%d'),
    })


def booking_slots(request):
    service_id = request.GET.get('service')
    barber_id = request.GET.get('barber')
    date_str = request.GET.get('date')
    if not (service_id and barber_id and date_str):
        return render(request, 'partials/time_slots.html', {'slots': [], 'message': 'Выберите услугу, мастера и дату'})
    service = get_object_or_404(Service, pk=service_id, is_active=True)
    barber = get_object_or_404(Barber, pk=barber_id, is_active=True)
    day = _parse_date(date_str)

    busy = list(Appointment.objects.filter(
        barber=barber,
        start_at__date=day,
        status__in=['pending', 'confirmed', 'in_progress'],
    ).values_list('start_at', 'duration_minutes'))

    tz = timezone.get_current_timezone()
    slots = []
    now = timezone.now()
    cursor = datetime.combine(day, datetime.min.time()).replace(hour=WORK_START_HOUR, tzinfo=tz)
    end = cursor.replace(hour=WORK_END_HOUR)
    while cursor + timedelta(minutes=service.duration_minutes) <= end:
        slot_end = cursor + timedelta(minutes=service.duration_minutes)
        overlap = any(
            cursor < (b_start + timedelta(minutes=b_dur)) and slot_end > b_start
            for b_start, b_dur in busy
        )
        in_past = cursor < now
        slots.append({
            'datetime': cursor,
            'label': cursor.strftime('%H:%M'),
            'iso': cursor.strftime('%Y-%m-%dT%H:%M'),
            'available': not overlap and not in_past,
        })
        cursor += timedelta(minutes=SLOT_MINUTES)
    return render(request, 'partials/time_slots.html', {
        'slots': slots,
        'service': service,
        'barber': barber,
        'date': day,
    })


@login_required
def booking_confirm(request, service_id, barber_id, datetime_str):
    service = get_object_or_404(Service, pk=service_id, is_active=True)
    barber = get_object_or_404(Barber, pk=barber_id, is_active=True)
    try:
        naive = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
    except ValueError:
        return HttpResponseBadRequest('Неверная дата')
    start_at = timezone.make_aware(naive, timezone.get_current_timezone())

    if request.method == 'POST':
        client, _ = Client.objects.get_or_create(user=request.user)
        appt = Appointment.objects.create(
            client=client,
            barber=barber,
            service=service,
            start_at=start_at,
            duration_minutes=service.duration_minutes,
            status='confirmed',
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Запись успешно создана!')
        return redirect('bookings:success', pk=appt.pk)

    return render(request, 'public/booking_confirm.html', {
        'service': service,
        'barber': barber,
        'start_at': start_at,
        'datetime_str': datetime_str,
    })


@login_required
def booking_success(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    return render(request, 'public/booking_success.html', {'appointment': appt})
