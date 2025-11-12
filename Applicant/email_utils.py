from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_user_email(user):
    """
    Get the user's email address from various sources:
    1. From their learner profile (registration form)
    2. From their user account email
    3. From their social account (Google)
    """
    try:
        # First try to get email from learner profile (registration_f1.html)
        if hasattr(user, 'learner_profile') and user.learner_profile.exists():
            profile = user.learner_profile.first()
            if profile and profile.email:
                return profile.email
        
        # Then try user's email field (for regular login)
        if user.email:
            return user.email
        
        # Finally try social account email (Google auth)
        if hasattr(user, 'socialaccount_set'):
            social_accounts = user.socialaccount_set.all()
            for account in social_accounts:
                if account.extra_data.get('email'):
                    return account.extra_data['email']
        
        return None
    except Exception as e:
        logger.error(f"Error getting email for user {user.username}: {str(e)}")
        return None

def send_application_status_email(application, application_type='program'):
    """
    Send email notification when application is saved to ProgramApplication or WalkInApplication
    
    Args:
        application: ProgramApplication or WalkInApplication instance
        application_type: 'program' or 'walkin'
    """
    try:
        user_email = get_user_email(application.applicant)
        
        if not user_email:
            logger.warning(f"No email found for user {application.applicant.username}")
            return False
        
        # For ProgramApplication and WalkInApplication - send "under review" message
        template_name = 'emails/application_under_review.html'
        subject = f'Application Under Review - {application.program.program_name}'
        
        # Prepare context for email template
        context = {
            'applicant_name': application.applicant.get_full_name() or application.applicant.username,
            'program_name': application.program.program_name,
            'application_type': 'Walk-in' if application_type == 'walkin' else 'Online',
            'applied_date': application.applied_at.strftime('%B %d, %Y'),
        }
        
        # Render email content
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Email sent successfully to {user_email} for {application_type} application {application.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email for {application_type} application {application.id}: {str(e)}")
        return False

def send_approval_notification_email(approved_applicant):
    """
    Send email notification when applicant is approved (ApprovedApplicant created)
    
    Args:
        approved_applicant: ApprovedApplicant instance
    """
    try:
        user_email = get_user_email(approved_applicant.applicant)
        
        if not user_email:
            logger.warning(f"No email found for user {approved_applicant.applicant.username}")
            return False
        
        template_name = 'emails/application_approved.html'
        subject = f'Congratulations! Your {approved_applicant.program.program_name} Application was Approved'
        
        # Prepare context for email template
        context = {
            'applicant_name': approved_applicant.applicant.get_full_name() or approved_applicant.applicant.username,
            'program_name': approved_applicant.program.program_name,
            'approved_date': approved_applicant.approved_at.strftime('%B %d, %Y'),
            'login_url': 'http://127.0.0.1:8000/Login/',
        }
        
        # Render email content
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Approval email sent successfully to {user_email} for approved applicant {approved_applicant.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send approval email for approved applicant {approved_applicant.id}: {str(e)}")
        return False

def send_welcome_email(user):
    """
    Send welcome email when user registers
    """
    try:
        user_email = get_user_email(user)
        
        if not user_email:
            logger.warning(f"No email found for user {user.username}")
            return False
        
        context = {
            'user_name': user.get_full_name() or user.username,
        }
        
        html_message = render_to_string('emails/welcome.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject='Welcome to DLL LMSTC',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Welcome email sent successfully to {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to user {user.username}: {str(e)}")
        return False
