from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Event, BatchCycle, Notification, Applicant, AdminPermission, Training, ApprovedApplicant
from django.utils import timezone
from datetime import datetime, time, timedelta, date

def check_admin_permission(user, permission_name: str) -> bool:
    """Local helper to avoid circular imports with views.py."""
    if not getattr(user, 'is_authenticated', False):
        return False
    if not user.is_superuser:
        return False
    try:
        perms = AdminPermission.objects.get(user=user)
        return getattr(perms, permission_name, True)
    except AdminPermission.DoesNotExist:
        return True


# Event Management Views
@csrf_exempt
def create_event(request):
    """Create a new event"""
    if request.method == 'POST':
        try:
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({'success': False, 'error': 'User not authenticated'})
            
            data = json.loads(request.body)
            
            # Validate required fields
            if not data.get('title'):
                return JsonResponse({'success': False, 'error': 'Title is required'})
            if not data.get('start_date'):
                return JsonResponse({'success': False, 'error': 'Start date is required'})
            
            # Parse date and time fields properly
            start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
            end_date = None
            if data.get('end_date'):
                end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
            
            start_time = None
            if data.get('start_time'):
                start_time = datetime.strptime(data.get('start_time'), '%H:%M').time()
            
            end_time = None
            if data.get('end_time'):
                end_time = datetime.strptime(data.get('end_time'), '%H:%M').time()

            event = Event.objects.create(
                title=data.get('title'),
                description=data.get('description', ''),
                category=data.get('category', 'enrollment'),
                start_date=start_date,
                end_date=end_date,
                start_time=start_time,
                end_time=end_time,
                batch=data.get('batch') if data.get('batch') else None,
                trimester=data.get('trimester') if data.get('trimester') else None,
                created_by=request.user
            )
            
            # Create notifications for departmental events - notify all applicants
            if event.category == 'departmental' and event.start_date <= date.today() and event.end_date >= date.today():
                try:
                    from .models import Applicant, Notification
                    # Get all active applicants (users who are not staff/admin)
                    applicants = Applicant.objects.filter(is_superuser=False, is_staff=False)
                    
                    for applicant in applicants:
                        Notification.objects.create(
                            recipient=applicant,
                            sender=None,  # System notification
                            notification_type='departmental_event',
                            title=f'New Departmental Event: {event.title}',
                            message=f'A new departmental event "{event.title}" is now active. Dates: {event.start_date.strftime("%B %d, %Y")} - {event.end_date.strftime("%B %d, %Y")}',
                            is_read=False
                        )
                except Exception as e:
                    # Don't fail event creation if notification fails
                    print(f"Error creating departmental event notifications: {e}")
            
            return JsonResponse({
                'success': True,
                'message': 'Event created successfully',
                'event': {
                    'id': event.id,
                    'title': event.title,
                    'description': event.description,
                    'category': event.category,
                    'start_date': event.start_date.strftime('%Y-%m-%d'),
                    'end_date': event.end_date.strftime('%Y-%m-%d') if event.end_date else None,
                    'start_time': event.start_time.strftime('%H:%M') if event.start_time else None,
                    'end_time': event.end_time.strftime('%H:%M') if event.end_time else None,
                    'batch': event.batch,
                    'trimester': event.trimester,
                    'status': event.status
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@csrf_exempt
def get_events(request):
    """Get all events or filtered events"""
    try:
        category = request.GET.get('category', 'all')
        batch = request.GET.get('batch', 'all')
        trimester = request.GET.get('trimester', 'all')
        
        events = Event.objects.all()
        
        if category != 'all':
            events = events.filter(category=category)
        if batch != 'all':
            events = events.filter(batch=batch)
        if trimester != 'all':
            events = events.filter(trimester=trimester)
        
        events_data = []
        for event in events:
            events_data.append({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'category': event.category,
                'start_date': event.start_date.strftime('%Y-%m-%d'),
                'end_date': event.end_date.strftime('%Y-%m-%d') if event.end_date else None,
                'start_time': event.start_time.strftime('%H:%M') if event.start_time else None,
                'end_time': event.end_time.strftime('%H:%M') if event.end_time else None,
                'batch': event.batch,
                'trimester': event.trimester,
                'status': event.status,
                'created_at': event.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'events': events_data,
            'count': len(events_data)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def update_event(request, event_id):
    """Update an existing event"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event = Event.objects.get(id=event_id)
            
            event.title = data.get('title', event.title)
            event.description = data.get('description', event.description)
            event.category = data.get('category', event.category)
            # Parse date and time fields properly for updates
            if data.get('start_date'):
                event.start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
            if data.get('end_date'):
                event.end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
            if data.get('start_time'):
                event.start_time = datetime.strptime(data.get('start_time'), '%H:%M').time()
            if data.get('end_time'):
                event.end_time = datetime.strptime(data.get('end_time'), '%H:%M').time()
            event.batch = data.get('batch', event.batch)
            event.trimester = data.get('trimester', event.trimester)
            event.status = data.get('status', event.status)
            
            event.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Event updated successfully'
            })
            
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Event not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@csrf_exempt
def delete_event(request, event_id):
    """Delete an event"""
    if request.method == 'POST':
        try:
            event = Event.objects.get(id=event_id)
            event.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Event deleted successfully'
            })
            
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Event not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@csrf_exempt
def archive_event(request, event_id):
    """Archive an event"""
    if request.method == 'POST':
        try:
            event = Event.objects.get(id=event_id)
            event.status = 'archived'
            event.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Event archived successfully'
            })
            
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Event not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


# Batch Cycle Management Views
@csrf_exempt
def get_batch_cycle_status(request):
    """Get the current batch cycle status"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=401)
        cycle = BatchCycle.get_active_cycle()
        
        return JsonResponse({
            'success': True,
            'cycle': {
                'current_batch': cycle.current_batch,
                'cycle_state': cycle.cycle_state,
                'cycle_state_display': cycle.get_cycle_state_display(),
                'current_semester': cycle.current_semester,
                'completed_semesters': cycle.completed_semesters,
                'can_start_enrollment': cycle.can_start_enrollment(),
                'batch_started_at': cycle.batch_started_at.isoformat() if cycle.batch_started_at else None,
                'active_event_id': cycle.active_enrollment_event.id if cycle.active_enrollment_event else None
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_POST
def check_enrollment_events(request):
    """Check for ended enrollment events and activate batches"""
    try:
        if not check_admin_permission(request.user, 'manage_enrollments'):
            return JsonResponse({'success': False, 'error': 'You do not have permission to manage enrollments.'}, status=403)
        now = timezone.now()
        today = now.date()
        current_time = now.time()
        
        # Get active batch cycle
        cycle = BatchCycle.get_active_cycle()
        
        # Find enrollment events that have ended but haven't activated a batch yet
        ended_events = Event.objects.filter(
            category='enrollment',
            status='active',
            batch_activated=False,
            end_date__lte=today
        )
        
        activated_count = 0
        for event in ended_events:
            # Check if end_date has passed (with time if available)
            event_ended = False
            
            if event.end_date < today:
                event_ended = True
            elif event.end_date == today and event.end_time:
                if current_time >= event.end_time:
                    event_ended = True
            elif event.end_date == today and not event.end_time:
                event_ended = True
            
            if event_ended and cycle.can_start_enrollment():
                # Activate batch from this event
                cycle.activate_batch_from_event(event)
                event.status = 'completed'
                event.save()
                activated_count += 1
                break  # Only activate one batch at a time
        
        return JsonResponse({
            'success': True,
            'message': f'Checked enrollment events. Activated {activated_count} batch(es).',
            'activated_count': activated_count,
            'current_batch': cycle.current_batch,
            'cycle_state': cycle.cycle_state
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_POST
def complete_semester(request):
    """Mark a semester as completed for the current batch"""
    try:
        if not check_admin_permission(request.user, 'manage_enrollments'):
            return JsonResponse({'success': False, 'error': 'You do not have permission to manage enrollments.'}, status=403)
        data = json.loads(request.body)
        semester = data.get('semester')
        
        if not semester or semester not in ['1', '2', '3']:
            return JsonResponse({'success': False, 'error': 'Valid semester (1, 2, or 3) is required'})
        
        cycle = BatchCycle.get_active_cycle()
        cycle.complete_semester(semester)
        
        # Check if all semesters are completed
        all_completed = all(cycle.completed_semesters.values())
        
        message = f'Semester {semester} marked as completed.'
        if all_completed:
            message += ' All semesters completed. Waiting for next enrollment event.'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'completed_semesters': cycle.completed_semesters,
            'cycle_state': cycle.cycle_state,
            'all_completed': all_completed
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_POST
def progress_to_next_batch(request):
    """Progress to the next batch in the cycle (after all semesters completed)"""
    try:
        if not check_admin_permission(request.user, 'manage_enrollments'):
            return JsonResponse({'success': False, 'error': 'You do not have permission to manage enrollments.'}, status=403)
        cycle = BatchCycle.get_active_cycle()
        
        # Check if all semesters are completed
        if not all(cycle.completed_semesters.values()):
            return JsonResponse({
                'success': False,
                'error': 'Cannot progress to next batch. Not all semesters are completed.'
            })
        
        old_batch = cycle.current_batch
        cycle.progress_to_next_batch()
        
        return JsonResponse({
            'success': True,
            'message': f'Progressed from Batch {old_batch} to Batch {cycle.current_batch}',
            'current_batch': cycle.current_batch,
            'cycle_state': cycle.cycle_state
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def auto_check_and_activate_batch(request):
    """Automatically check for ended enrollment events and activate batches"""
    try:
        if not check_admin_permission(request.user, 'manage_enrollments'):
            return JsonResponse({'success': False, 'error': 'You do not have permission to manage enrollments.'}, status=403)
        now = timezone.now()
        today = now.date()
        current_time = now.time()
        
        # Get active batch cycle
        cycle = BatchCycle.get_active_cycle()
        
        # Find enrollment events that have ended but haven't activated a batch yet
        ended_events = Event.objects.filter(
            category='enrollment',
            status='active',
            batch_activated=False,
            end_date__lte=today
        )
        
        activated_count = 0
        for event in ended_events:
            # Check if end_date has passed (with time if available)
            event_ended = False
            
            if event.end_date < today:
                event_ended = True
            elif event.end_date == today and event.end_time:
                if current_time >= event.end_time:
                    event_ended = True
            elif event.end_date == today and not event.end_time:
                event_ended = True
            
            if event_ended and cycle.can_start_enrollment():
                # Activate batch from this event
                cycle.activate_batch_from_event(event)
                event.status = 'completed'
                event.save()
                activated_count += 1
                break  # Only activate one batch at a time
        
        return JsonResponse({
            'success': True,
            'activated_count': activated_count,
            'cycle': {
                'current_batch': cycle.current_batch,
                'cycle_state': cycle.cycle_state,
                'cycle_state_display': cycle.get_cycle_state_display(),
                'current_semester': cycle.current_semester,
                'completed_semesters': cycle.completed_semesters,
                'can_start_enrollment': cycle.can_start_enrollment(),
                'batch_started_at': cycle.batch_started_at.isoformat() if cycle.batch_started_at else None,
                'active_event_id': cycle.active_enrollment_event.id if cycle.active_enrollment_event else None
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_POST
def check_event_reminders(request):
    """
    Create reminder notifications for events:
    - Ending soon (within 3 days)
    - Upcoming (starting within 3 days)

    Notes:
    - This endpoint is triggered periodically from the admin dashboard.
    - De-duplicates notifications per (recipient, type, event title + date window).
    """
    try:
        now = timezone.now()
        today = now.date()
        
        # Find events within the next 3 days
        three_days_later = today + timedelta(days=3)
        
        # Upcoming events (starting within 3 days)
        events_starting_soon = Event.objects.filter(
            status='active',
            start_date__gte=today,
            start_date__lte=three_days_later
        )

        events_ending_soon = Event.objects.filter(
            status='active',
            end_date__gte=today,
            end_date__lte=three_days_later
        )
        
        reminders_created = 0
        
        # Get all admin users for admin notifications
        admin_users = Applicant.objects.filter(is_superuser=True)
        
        # Get all applicants for departmental event notifications
        applicants = Applicant.objects.filter(is_superuser=False, is_staff=False)
        
        # Upcoming reminders (admins, all categories)
        for event in events_starting_soon:
            days_until_start = (event.start_date - today).days

            for admin in admin_users:
                # Check if notification already exists for this event/admin/type (ignore read state)
                existing_notification = Notification.objects.filter(
                    recipient=admin,
                    notification_type='event_upcoming',
                    title__icontains=event.title,
                    message__icontains=event.start_date.strftime("%B %d, %Y"),
                ).first()

                if not existing_notification:
                    days_text = 'today' if days_until_start == 0 else f'in {days_until_start} day{"s" if days_until_start != 1 else ""}'
                    date_range = event.start_date.strftime("%B %d, %Y")
                    if event.end_date and event.end_date != event.start_date:
                        date_range = f'{event.start_date.strftime("%B %d, %Y")} - {event.end_date.strftime("%B %d, %Y")}'

                    Notification.objects.create(
                        recipient=admin,
                        sender=None,  # System notification
                        notification_type='event_upcoming',
                        title=f'Upcoming Event: {event.title}',
                        message=f'The event "{event.title}" starts {days_text}. Schedule: {date_range}',
                        is_read=False
                    )
                    reminders_created += 1

            # Also notify applicants for Enrollment and Departmental events starting within 3 days
            if event.category in ['enrollment', 'departmental']:
                for applicant in applicants:
                    existing_app_notif = Notification.objects.filter(
                        recipient=applicant,
                        notification_type='event_upcoming',
                        title__icontains=event.title,
                        message__icontains=event.start_date.strftime("%B %d, %Y"),
                    ).first()
                    if not existing_app_notif:
                        days_text = 'today' if days_until_start == 0 else f'in {days_until_start} day{"s" if days_until_start != 1 else ""}'
                        date_range = event.start_date.strftime("%B %d, %Y")
                        if event.end_date and event.end_date != event.start_date:
                            date_range = f'{event.start_date.strftime("%B %d, %Y")} - {event.end_date.strftime("%B %d, %Y")}'
                        Notification.objects.create(
                            recipient=applicant,
                            sender=None,
                            notification_type='event_upcoming',
                            title=f'Upcoming Event: {event.title}',
                            message=f'The event "{event.title}" starts {days_text}. Schedule: {date_range}',
                            is_read=False
                        )
                        reminders_created += 1

        # Ending reminders (existing behavior)
        for event in events_ending_soon:
            days_until_end = (event.end_date - today).days
            
            if event.category == 'enrollment':
                # Create notification for each admin if not already created
                for admin in admin_users:
                    # Check if notification already exists for this event and admin
                    existing_notification = Notification.objects.filter(
                        recipient=admin,
                        notification_type='event_reminder',
                        title__icontains=event.title,
                    ).first()
                    
                    if not existing_notification:
                        days_text = 'today' if days_until_end == 0 else f'in {days_until_end} day{"s" if days_until_end != 1 else ""}'
                        
                        Notification.objects.create(
                            recipient=admin,
                            sender=None,  # System notification
                            notification_type='event_reminder',
                            title=f'Event Ending Soon: {event.title}',
                            message=f'The event "{event.title}" is ending {days_text}. End date: {event.end_date.strftime("%B %d, %Y")}',
                            is_read=False
                        )
                        reminders_created += 1
            elif event.category == 'departmental':
                # Create notification for each applicant if not already created
                for applicant in applicants:
                    # Check if notification already exists for this event and applicant
                    existing_notification = Notification.objects.filter(
                        recipient=applicant,
                        notification_type='departmental_event',
                        title__icontains=event.title,
                    ).first()
                    
                    if not existing_notification:
                        days_text = 'today' if days_until_end == 0 else f'in {days_until_end} day{"s" if days_until_end != 1 else ""}'
                        
                        Notification.objects.create(
                            recipient=applicant,
                            sender=None,  # System notification
                            notification_type='departmental_event',
                            title=f'Departmental Event Ending Soon: {event.title}',
                            message=f'The departmental event "{event.title}" is ending {days_text}. End date: {event.end_date.strftime("%B %d, %Y")}',
                            is_read=False
                        )
                        reminders_created += 1
        
        # Training session reminders (starting within 3 days)
        trainings_starting_soon = Training.objects.filter(
            start_date__gte=today,
            start_date__lte=three_days_later
        )

        for training in trainings_starting_soon:
            days_until_start = (training.start_date - today).days
            days_text = 'today' if days_until_start == 0 else f'in {days_until_start} day{"s" if days_until_start != 1 else ""}'
            date_text = training.start_date.strftime("%B %d, %Y")

            # Notify the trainer (owner)
            existing_trainer_notif = Notification.objects.filter(
                recipient=training.trainer,
                notification_type='training_upcoming',
                title__icontains=training.program_name,
                message__icontains=date_text,
            ).first()
            if not existing_trainer_notif:
                Notification.objects.create(
                    recipient=training.trainer,
                    sender=None,
                    notification_type='training_upcoming',
                    title=f'Upcoming Training Session: {training.program_name}',
                    message=f'Your training session "{training.program_name}" starts {days_text} on {date_text}.',
                    is_read=False
                )
                reminders_created += 1

            # Notify approved trainees for the same program
            approved_trainees = ApprovedApplicant.objects.filter(
                program__program_name=training.program_name,
                status='active'
            ).select_related('applicant')

            for approved in approved_trainees:
                recipient = approved.applicant
                existing_student_notif = Notification.objects.filter(
                    recipient=recipient,
                    notification_type='training_upcoming',
                    title__icontains=training.program_name,
                    message__icontains=date_text,
                ).first()
                if not existing_student_notif:
                    Notification.objects.create(
                        recipient=recipient,
                        sender=None,
                        notification_type='training_upcoming',
                        title=f'Upcoming Training Session: {training.program_name}',
                        message=f'A training session for {training.program_name} starts {days_text} on {date_text}.',
                        is_read=False
                    )
                    reminders_created += 1

        return JsonResponse({
            'success': True,
            'reminders_created': reminders_created,
            'events_checked': (events_ending_soon.count() + events_starting_soon.count())
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
