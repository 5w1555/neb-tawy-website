# booking/availability.py
from datetime import time

ZOOM_SLOTS = [
    (time(10, 0), time(10, 45)),
    (time(11, 0), time(11, 45)),
    (time(14, 0), time(14, 45)),
    (time(16, 0), time(16, 45)),
]

PHONE_SLOTS = [
    (time(18, 30), time(19, 0)),
    (time(19, 0), time(19, 30)),
]

SATURDAY = 5
SUNDAY = 6

def get_available_slots(service_type, date):
    if service_type == "zoom":
        if date.weekday() != SATURDAY:
            return []
        slots = ZOOM_SLOTS
    elif service_type == "phone":
        if date.weekday() == SUNDAY:
            return []
        slots = PHONE_SLOTS
    else:
        return []

    taken = set(
        Booking.objects.filter(date=date, service_type=service_type)
        .values_list("start_time", flat=True)
    )
    return [(start, end) for start, end in slots if start not in taken]