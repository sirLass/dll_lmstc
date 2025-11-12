from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProgramApplication, WalkInApplication, ApprovedApplicant, Applicant
from .email_utils import send_application_status_email, send_approval_notification_email, send_welcome_email
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=ProgramApplication)
def send_program_application_email(sender, instance, created, **kwargs):
    """Send email when ProgramApplication is created"""
    if created:
        try:
            logger.info(f"Sending under review email for program application {instance.pk}")
            send_application_status_email(instance, 'program')
        except Exception as e:
            logger.error(f"Error in program application email signal: {str(e)}")

@receiver(post_save, sender=WalkInApplication)
def send_walkin_application_email(sender, instance, created, **kwargs):
    """Send email when WalkInApplication is created"""
    if created:
        try:
            logger.info(f"Sending under review email for walkin application {instance.pk}")
            send_application_status_email(instance, 'walkin')
        except Exception as e:
            logger.error(f"Error in walkin application email signal: {str(e)}")

@receiver(post_save, sender=ApprovedApplicant)
def send_approval_email(sender, instance, created, **kwargs):
    """Send email when ApprovedApplicant is created (application approved)"""
    if created:
        try:
            logger.info(f"Sending approval email for approved applicant {instance.pk}")
            send_approval_notification_email(instance)
        except Exception as e:
            logger.error(f"Error in approval email signal: {str(e)}")

@receiver(post_save, sender=Applicant)
def send_user_welcome_email(sender, instance, created, **kwargs):
    """Send welcome email when new user registers"""
    if created:
        try:
            logger.info(f"Sending welcome email for new user: {instance.username}")
            send_welcome_email(instance)
        except Exception as e:
            logger.error(f"Error sending welcome email for user {instance.username}: {str(e)}")
