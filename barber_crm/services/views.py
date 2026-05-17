from django.shortcuts import render, get_object_or_404
from .models import Service, ServiceCategory


def service_list(request):
    category_slug = request.GET.get('cat')
    services = Service.objects.filter(is_active=True).select_related('category')
    if category_slug:
        services = services.filter(category__slug=category_slug)
    return render(request, 'public/services.html', {
        'services': services,
        'categories': ServiceCategory.objects.all(),
        'active_category': category_slug,
    })


def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk, is_active=True)
    return render(request, 'public/service_detail.html', {'service': service})
