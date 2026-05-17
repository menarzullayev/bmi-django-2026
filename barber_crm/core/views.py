from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from services.models import Service, ServiceCategory
from staff.models import Barber


def landing(request):
    return render(request, 'public/landing.html', {
        'featured_services': Service.objects.filter(is_active=True).select_related('category')[:6],
        'categories': ServiceCategory.objects.all()[:6],
        'barbers': Barber.objects.filter(is_active=True).select_related('user')[:4],
    })


@login_required
def dashboard(request):
    if not getattr(request.user, 'is_staff_role', False):
        return redirect('core:landing')
    from bookings.models import Appointment
    from liveline.models import QueueEntry
    today = timezone.now().date()
    appts_today_qs = Appointment.objects.filter(start_at__date=today)
    appts_today = appts_today_qs.count()
    revenue_today = sum(
        (a.service.price for a in appts_today_qs.filter(status='completed').select_related('service')),
        0,
    )
    queue_count = QueueEntry.objects.filter(status='waiting').count()
    top_barber = (
        Barber.objects.filter(is_active=True)
        .order_by('-rating')
        .select_related('user')
        .first()
    )
    return render(request, 'dashboard/index.html', {
        'appts_today': appts_today,
        'revenue_today': revenue_today,
        'queue_count': queue_count,
        'top_barber': top_barber,
        'recent_appts': Appointment.objects.select_related('client__user', 'barber__user', 'service').order_by('-start_at')[:10],
    })
