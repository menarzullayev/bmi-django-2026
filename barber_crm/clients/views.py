from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from .models import Client
from loyalty.models import LoyaltyAccount


def _get_or_create_client(user):
    client, _ = Client.objects.get_or_create(user=user)
    return client


@login_required
def my_appointments(request):
    client = _get_or_create_client(request.user)
    now = timezone.now()
    upcoming = client.appointments.select_related('barber__user', 'service').filter(start_at__gte=now).order_by('start_at')
    past = client.appointments.select_related('barber__user', 'service').filter(start_at__lt=now).order_by('-start_at')
    return render(request, 'client/appointments.html', {
        'client': client,
        'upcoming': upcoming,
        'past': past,
    })


@login_required
def my_loyalty(request):
    client = _get_or_create_client(request.user)
    account, _ = LoyaltyAccount.objects.get_or_create(client=client)
    transactions = account.transactions.all()[:10]
    total = account.transactions.count()
    return render(request, 'client/loyalty.html', {
        'client': client,
        'account': account,
        'transactions': transactions,
        'has_more': total > 10,
        'next_offset': 10,
    })


@login_required
def loyalty_more(request):
    client = _get_or_create_client(request.user)
    account, _ = LoyaltyAccount.objects.get_or_create(client=client)
    try:
        offset = int(request.GET.get('offset', '0'))
    except ValueError:
        offset = 0
    limit = 10
    transactions = account.transactions.all()[offset:offset + limit]
    total = account.transactions.count()
    return render(request, 'partials/loyalty_transactions.html', {
        'transactions': transactions,
        'has_more': offset + limit < total,
        'next_offset': offset + limit,
    })
