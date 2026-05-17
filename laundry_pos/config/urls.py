from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

from accounts.views import LaundryLoginView


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('pos:dashboard')
    return redirect('login')


admin.site.site_header = 'Химчистка — Администрирование'
admin.site.site_title = 'Химчистка POS'
admin.site.index_title = 'Управление химчисткой'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_redirect, name='root'),
    path('login/', LaundryLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('pos/', include('core.urls', namespace='pos')),
    path('intake/', include('intake.urls', namespace='intake')),
    path('tickets/', include('intake.urls_tickets', namespace='tickets')),
    path('pricing/', include('catalog.urls_pricing', namespace='pricing')),
    path('catalog/', include('catalog.urls', namespace='catalog')),
    path('delivery/', include('delivery.urls', namespace='delivery')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('reports/', include('reports.urls', namespace='reports')),
    path('qr/', include('core.urls_qr', namespace='qr')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
