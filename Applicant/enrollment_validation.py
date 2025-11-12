"""
Enrollment validation utilities
Checks if enrollment is currently active based on enrollment events
"""
from django.utils import timezone
from .models import Event, BatchCycle


def is_enrollment_active():
    """
    Check if there is an active enrollment event running right now
    Returns: (is_active: bool, message: str, event: Event or None)
    """
    now = timezone.now()
    today = now.date()
    current_time = now.time()
    
    # Find active enrollment events
    active_events = Event.objects.filter(
        category='enrollment',
        status='active',
        start_date__lte=today,
        end_date__gte=today
    )
    
    for event in active_events:
        # Check if we're within the time range
        event_started = False
        event_ended = False
        
        # Check start
        if event.start_date < today:
            event_started = True
        elif event.start_date == today:
            if event.start_time is None or current_time >= event.start_time:
                event_started = True
        
        # Check end
        if event.end_date > today:
            event_ended = False
        elif event.end_date == today:
            if event.end_time is None or current_time <= event.end_time:
                event_ended = False
            else:
                event_ended = True
        
        # If event has started and not ended, enrollment is active
        if event_started and not event_ended:
            batch_cycle = BatchCycle.get_active_cycle()
            message = f"Enrollment is currently open until {event.end_date.strftime('%B %d, %Y')}"
            if event.end_time:
                message += f" at {event.end_time.strftime('%I:%M %p')}"
            message += f" for Batch {batch_cycle.current_batch}."
            return True, message, event
    
    # No active enrollment found
    # Check for upcoming enrollment
    upcoming_events = Event.objects.filter(
        category='enrollment',
        status='active',
        start_date__gt=today
    ).order_by('start_date').first()
    
    if upcoming_events:
        message = f"Enrollment is not currently open. Next enrollment starts on {upcoming_events.start_date.strftime('%B %d, %Y')}"
        if upcoming_events.start_time:
            message += f" at {upcoming_events.start_time.strftime('%I:%M %p')}"
        message += ". Please check back then."
    else:
        message = "Enrollment is not currently open. Please wait for the administration to announce the next enrollment period."
    
    return False, message, None


def get_enrollment_info():
    """
    Get detailed information about enrollment status
    Returns: dict with enrollment information
    """
    is_active, message, event = is_enrollment_active()
    batch_cycle = BatchCycle.get_active_cycle()
    
    info = {
        'is_active': is_active,
        'message': message,
        'current_batch': batch_cycle.current_batch,
        'batch_display': f"Batch {batch_cycle.current_batch}",
    }
    
    if event:
        info['event'] = {
            'title': event.title,
            'start_date': event.start_date.strftime('%Y-%m-%d'),
            'end_date': event.end_date.strftime('%Y-%m-%d'),
            'start_time': event.start_time.strftime('%H:%M') if event.start_time else None,
            'end_time': event.end_time.strftime('%H:%M') if event.end_time else None,
        }
    else:
        info['event'] = None
    
    return info
