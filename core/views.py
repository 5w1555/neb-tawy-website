from datetime import date, datetime
from django.http import JsonResponse
from django.db.models import Count
from django.shortcuts import render, redirect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Post, Booking

from django_ratelimit.decorators import ratelimit
from django.http import Http404

import brevo_python

import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY

PRICES = {
    'focused_reading':    2500,   # €25
    'indepth_guidance':   5000,   # €50
    'signature_guidance': 13500,  # €135
    'zoom_session':       15000,  # €150
}

SERVICE_NAMES = {
    'focused_reading':    'Focused Reading',
    'indepth_guidance':   'In-Depth Guidance',
    'signature_guidance': 'Signature Guidance',
    'zoom_session':       'Zoom Session',
}

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def booking(request):
    if request.method == 'POST':
        service = request.POST.get('service')
        date_selected = request.POST.get('date')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        message = request.POST.get('message', '')

        if service not in PRICES:
            return render(request, 'booking.html', {'error': 'Please select a valid service.'})

        if not date_selected:
            return render(request, 'booking.html', {'error': 'Please select a date.'})

        try:
            parsed_date = datetime.strptime(date_selected, '%Y-%m-%d').date()
        except ValueError:
            return render(request, 'booking.html', {'error': 'Invalid date format.'})

        if parsed_date < date.today():
            return render(request, 'booking.html', {'error': 'Please choose a future date.'})

        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'booking.html', {'error': 'Please enter a valid email address.'})

        if Booking.objects.filter(date=parsed_date, paid=True).count() >= 2:
            return render(request, 'booking.html', {'error': 'That date is no longer available. Please choose another.'})

        try:
            new_booking = Booking.objects.create(
                service=service,
                date=parsed_date,
                first_name=first_name,
                last_name=last_name,
                email=email,
                message=message,
                paid=False
            )
            return redirect('payment', booking_id=new_booking.id)
        except Exception as e:
            print("BOOKING ERROR:", e)
            return render(request, 'booking.html', {'error': 'Something went wrong. Please try again.'})

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

@ratelimit(key='ip', rate='10/m', block=True)
def payment(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        raise Http404("Booking not found")

    if booking.paid:
        return redirect('payment_success')

    try:
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
    except stripe.error.StripeError as e:
        print("STRIPE ERROR:", e)
        return render(request, 'booking.html', {'error': 'Payment setup failed. Please try again.'})

def send_booking_notification(booking):
    configuration = brevo_python.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    api_instance = brevo_python.TransactionalEmailsApi(
        brevo_python.ApiClient(configuration)
    )

    # Email to her — new booking notification
    owner_email = brevo_python.SendSmtpEmail(
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

    # Email to client — confirmation
    client_email = brevo_python.SendSmtpEmail(
        to=[{"email": booking.email, "name": f"{booking.first_name} {booking.last_name}"}],
        sender={"email": "marwanewafik2@gmail.com", "name": "Neb Tawy"},
        reply_to={"email": settings.BOOKING_NOTIFICATION_EMAIL},
        subject="Your booking is confirmed",
        text_content=f"""
Dear {booking.first_name},

Your booking has been confirmed. Here are your details:

Service: {SERVICE_NAMES.get(booking.service, booking.service)}
Date: {booking.date.strftime('%B %d, %Y')}

If you have any questions, simply reply to this email.

Neb Tawy
        """.strip()
    )

    api_instance.send_transac_email(owner_email)
    api_instance.send_transac_email(client_email)

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

        try:
            booking_id = session['metadata']['booking_id']
            booking = Booking.objects.get(id=booking_id)
            if not booking.paid:
                booking.paid = True
                booking.save(update_fields=["paid"])
                try:
                    send_booking_notification(booking)
                except Exception as email_error:
                    print(f"EMAIL ERROR: {email_error}")
        except KeyError:
            print("WEBHOOK ERROR: missing booking_id in metadata")
        except Booking.DoesNotExist:
            print(f"BOOKING NOT FOUND: {booking_id}")
        except Exception as e:
            print(f"WEBHOOK ERROR: {e}")

    return JsonResponse({'status': 'ok'})

def payment_success(request):
    return render(request, 'payment_success.html')

def payment_cancel(request):
    return render(request, 'payment_cancel.html')