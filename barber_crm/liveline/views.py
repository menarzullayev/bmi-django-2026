from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import QueueEntry


def _is_staff(user):
    return user.is_authenticated and getattr(user, 'is_staff_role', False)


@login_required
@user_passes_test(_is_staff)
def queue(request):
    waiting = QueueEntry.objects.filter(status='waiting').select_related('client__user', 'preferred_barber__user')
    serving = QueueEntry.objects.filter(status='being_served').select_related('client__user', 'preferred_barber__user', 'served_by__user')
    done = QueueEntry.objects.filter(status='done').select_related('client__user').order_by('-joined_at')[:10]
    return render(request, 'dashboard/queue.html', {
        'waiting': waiting,
        'serving': serving,
        'done': done,
    })


@login_required
@user_passes_test(_is_staff)
@require_POST
def queue_status_toggle(request, pk):
    entry = get_object_or_404(QueueEntry, pk=pk)
    new_status = request.POST.get('status')
    if new_status in dict(QueueEntry.STATUS_CHOICES):
        entry.status = new_status
        if new_status == 'being_served' and not entry.served_by and getattr(request.user, 'barber_profile', None):
            entry.served_by = request.user.barber_profile
        entry.save(update_fields=['status', 'served_by'])
    if request.headers.get('HX-Request'):
        return render(request, 'partials/queue_entry.html', {'entry': entry})
    return redirect('liveline:queue')
