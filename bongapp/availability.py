import datetime
from bongapp.models import HallBookings,Hall

def availability(hall,checkin,checkout):
    avail_list=[]
    bookings = HallBookings.objects.filter(Hall=hall).select_for_update()
    for booking in bookings:
        if booking.checkin > checkout or booking.checkout < checkin:
            avail_list.append(True)
        else:
            avail_list.append(False)
    return all(avail_list)