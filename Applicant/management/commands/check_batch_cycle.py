from django.core.management.base import BaseCommand
from django.utils import timezone
from Applicant.models import Event, BatchCycle


class Command(BaseCommand):
    help = 'Check for ended enrollment events and automatically activate batches'

    def handle(self, *args, **kwargs):
        """
        This command checks for enrollment events that have ended and automatically
        activates the corresponding batch in the batch cycle.
        """
        now = timezone.now()
        today = now.date()
        current_time = now.time()
        
        # Get active batch cycle
        cycle = BatchCycle.get_active_cycle()
        
        self.stdout.write(f"Current Batch Cycle Status:")
        self.stdout.write(f"  - Current Batch: {cycle.current_batch}")
        self.stdout.write(f"  - Cycle State: {cycle.get_cycle_state_display()}")
        self.stdout.write(f"  - Current Semester: {cycle.current_semester}")
        self.stdout.write(f"  - Can Start Enrollment: {cycle.can_start_enrollment()}")
        
        # Find enrollment events that have ended but haven't activated a batch yet
        ended_events = Event.objects.filter(
            category='enrollment',
            status='active',
            batch_activated=False,
            end_date__lte=today
        )
        
        if not ended_events.exists():
            self.stdout.write(self.style.SUCCESS('No ended enrollment events found.'))
            return
        
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
                self.stdout.write(f"Activating Batch {cycle.current_batch} from event: {event.title}")
                cycle.activate_batch_from_event(event)
                event.status = 'completed'
                event.save()
                activated_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f"✓ Successfully activated Batch {cycle.current_batch} from event '{event.title}'"
                ))
                break  # Only activate one batch at a time
        
        if activated_count == 0:
            self.stdout.write(self.style.WARNING(
                'No batches activated. Either events have not ended or cycle cannot start enrollment.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Successfully activated {activated_count} batch(es)."
            ))
