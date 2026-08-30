from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook')  # language switcher
]

urlpatterns += i18n_patterns(
    path('', include('core.urls')),
    prefix_default_language=True,
)