from datetime import date
from django.http import JsonResponse
from django.db.models import Count
from django.shortcuts import render, redirect
from .models import Post, Booking

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from django.core.mail import EmailMessage
from django.utils.html import strip_tags

import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY

def index(request):
    return render(request, 'index.html')

def booking(request):
    if request.method == 'POST':
        service = request.POST.get('service')
        date_selected = request.POST.get('date')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        message = request.POST.get('message', '')

        try:
            new_booking = Booking.objects.create(
                service=service,
                date=date_selected,
                first_name=first_name,
                last_name=last_name,
                email=email,
                message=message,
                paid=False
            )
            return redirect('payment', booking_id=new_booking.id)
        except Exception as e:
            print("BOOKING ERROR:", e)

    return render(request, 'booking.html')

def blog(request):
    posts = Post.objects.filter(published=True).order_by('-created_at')
    return render(request, 'blog.html', {'posts': posts})

def get_unavailable_dates(request):
    unavailable = (
        Booking.objects
        .filter(paid=True, date__gte=date.today())
        .values('date')
        .annotate(count=Count('id'))
        .filter(count__gte=2)
        .values_list('date', flat=True)
    )
    return JsonResponse({
        'unavailable': [d.strftime('%Y-%m-%d') for d in unavailable]
    })

def legal(request):
    return render(request, 'mentions-legales.html')

def post_detail(request, slug):
    post = Post.objects.get(slug=slug, published=True)
    return render(request, 'post_detail.html', {'post': post})

PRICES = {
    'tarot': 5000,      # €50.00 in cents — change to real price
    'personal': 8000,   # €80.00 in cents — change to real price
}

SERVICE_NAMES = {
    'tarot': 'Card Reading',
    'personal': 'Personal Séance',
}

def payment(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': SERVICE_NAMES[booking.service],
                },
                'unit_amount': PRICES[booking.service],
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri('/booking/success/'),
        cancel_url=request.build_absolute_uri('/booking/cancel/'),
        metadata={'booking_id': booking.id}
    )
    return redirect(session.url, permanent=False)

def send_booking_notification(booking):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": settings.BOOKING_NOTIFICATION_EMAIL}],
        sender={"email": "marwanewafik2@gmail.com", "name": "Neb Tawy"},
        reply_to={"email": booking.email},
        subject=f"New booking: {SERVICE_NAMES.get(booking.service, booking.service)}",
        text_content=f"""
New paid booking received.

Service: {SERVICE_NAMES.get(booking.service, booking.service)}
Date: {booking.date}

Customer:
{booking.first_name} {booking.last_name}
Email: {booking.email}

Message:
{booking.message or "No message provided."}
        """.strip()
    )

    api_instance.send_transac_email(email)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return JsonResponse({'error': 'Invalid payload'}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        booking_id = session['metadata']['booking_id']

        try:
            booking = Booking.objects.get(id=booking_id)

            if not booking.paid:
                booking.paid = True
                booking.save(update_fields=["paid"])

                send_booking_notification(booking)

        except Booking.DoesNotExist:
            print(f"BOOKING NOT FOUND: {booking_id}")

    return JsonResponse({'status': 'ok'})

def payment_success(request):
    return render(request, 'payment_success.html')

def payment_cancel(request):
    return render(request, 'payment_cancel.html')

