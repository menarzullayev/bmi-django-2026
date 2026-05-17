from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import RedirectView

from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),

    path('login/', accounts_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),

    path('dashboard/', include(('core.urls', 'core'), namespace='core')),
    path('orders/', include(('workorders.urls', 'workorders'), namespace='workorders')),
    path('kanban/', include(('workorders.kanban_urls', 'kanban'), namespace='kanban')),
    path('parts/', include(('parts.urls', 'parts'), namespace='parts')),
    path('mechanics/', include(('mechanics.urls', 'mechanics'), namespace='mechanics')),
    path('customers/', include(('customers.urls', 'customers'), namespace='customers')),
    path('vehicles/', include(('vehicles.urls', 'vehicles'), namespace='vehicles')),
    path('invoices/', include(('billing.urls', 'billing'), namespace='billing')),
    path('reports/', include(('core.report_urls', 'reports'), namespace='reports')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'Автосервис — Администрирование'
admin.site.site_title = 'Автосервис ERP'
admin.site.index_title = 'Управление автосервисом'
