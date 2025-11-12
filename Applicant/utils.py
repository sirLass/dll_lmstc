from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model  # Use this instead of importing User
from django.utils import timezone
from .models import Notification

# Get the user model dynamically
User = get_user_model()

def send_application_notification(applicant, program):
    """Send email and create notification when user applies to program"""
    
    # Get all admin users (you can modify this logic based on your admin setup)
    admin_users = User.objects.filter(is_staff=True, is_superuser=True)
    
    # Email content for admins
    subject = f"New Program Application - {program.program_name}"
    message = f"""
    Hello Admin,
    
    A new application has been submitted:
    
    Applicant: {applicant.get_full_name() or applicant.username}
    Email: {applicant.email}
    Program: {program.program_name}
    Application Date: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    Please review the application in the admin panel.
    
    Best regards,
    Your Application System
    """
    
    # Send email to all admins
    admin_emails = [admin.email for admin in admin_users if admin.email]
    
    if admin_emails:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=False,
            )
            print(f"Email sent successfully to {len(admin_emails)} admins")
        except Exception as e:
            print(f"Failed to send email: {e}")
    
    # Create in-app notifications for all admins
    for admin in admin_users:
        Notification.objects.create(
            recipient=admin,
            sender=applicant,
            notification_type='application',
            title=f"New Application: {program.program_name}",
            message=f"{applicant.get_full_name() or applicant.username} applied for {program.program_name}"
        )
    
    # Create notification for the applicant
    Notification.objects.create(
        recipient=applicant,
        sender=None,  # System notification
        notification_type='application',
        title=f"Application Submitted: {program.program_name}",
        message=f"Your application for {program.program_name} has been submitted successfully and is under review."
    )
    
    print(f"Created notifications for {len(admin_users)} admins and the applicant")

def mark_notification_as_read(notification_id, user):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, recipient=user)
        notification.is_read = True
        notification.save()
        return True
    except Notification.DoesNotExist:
        return False

def get_unread_notifications(user):
    """Get unread notifications for a user"""
    return Notification.objects.filter(recipient=user, is_read=False)


from django.core.mail import send_mail

def notify_decline(application):
    subject = "Application Declined"
    message = f"Hello {application.applicant.username},\n\n" \
              f"Your application for {application.program.program_name} has been declined.\n" \
              f"Reason: {application.decline_reason}\n\nThank you."
    recipient = application.applicant.email
    send_mail(subject, message, 'admin@yourdomain.com', [recipient])
