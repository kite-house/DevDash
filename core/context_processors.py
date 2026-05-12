from django.utils import timezone
from .models import Event

def cases_visibility(request):
    now = timezone.now()
    event = Event.objects.first()
    can_view = False
    if event and now >= event.cases_visible_date:
        can_view = True

    return {
        'can_view_cases': can_view,
        'current_event': event,
    }