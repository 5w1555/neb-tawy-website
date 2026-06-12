from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('booking/', views.booking, name='booking'),
    path('booking/unavailable/', views.get_unavailable_dates, name='unavailable_dates'),
    path('booking/payment/<int:booking_id>/', views.payment, name='payment'),
    path('booking/success/', views.payment_success, name='payment_success'),
    path('booking/cancel/', views.payment_cancel, name='payment_cancel'),
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.post_detail, name='post_detail'),
    path('mentions-legales/', views.legal, name='legal'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
]