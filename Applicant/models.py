from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

# Custom user model
class Applicant(AbstractUser):
    def __str__(self):
        return self.username

# Example of another model that has a ForeignKey relationship to Applicant
class SocialAccount(models.Model):
    user = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='socialaccounts')
    provider = models.CharField(max_length=255)
    account_id = models.CharField(max_length=255)

    def __str__(self):
        return f"Social account for {self.user.username} via {self.provider}"

# Example for Email Address model, related to Applicant
class EmailAddress(models.Model):
    user = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='email_addresses')  # Use related_name to avoid clash
    email = models.EmailField(unique=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.email

# Example of a model that uses ForeignKey for Applicant with SET_NULL on delete (user will not be deleted, but this will unlink the user)
class UserProfile(models.Model):
    user = models.ForeignKey(Applicant, on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles')
    bio = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"Profile for {self.user.username}"

# Example for model that uses a ForeignKey for Group
class UserGroup(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='user_groups')  # Use related_name to avoid clash
    group_name = models.CharField(max_length=255)

    def __str__(self):
        return self.group_name

#programs
class Programs(models.Model):
    program_name = models.CharField(max_length=255)
    program_detail = models.CharField(max_length=255)
    program_sched = models.CharField(max_length=255)
    program_trainor = models.CharField(max_length=255, null=True, blank=True)
    program_competencies = models.JSONField(default=dict, null=True, blank=True)  # Changed from program_skill to program_competencies

    def __str__(self):
        return f'{self.program_name} {self.program_sched}'

# New model for multiple images
class ProgramImage(models.Model):
    program = models.ForeignKey(Programs, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='program_images/')

    def __str__(self):
        return f'Image for {self.program.program_name}'

from django.db import models

class JobPost(models.Model):
    AVAILABILITY_CHOICES = [
        ('1 Week', '1 Week'),
        ('2 Weeks', '2 Weeks'),
        ('1 Month', '1 Month'),
        ('2 Months', '2 Months'),
        ('3 Months', '3 Months'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    job_title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    job_description = models.TextField()
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')  # <-- new field
    program = models.ForeignKey('Programs', on_delete=models.SET_NULL, null=True, blank=True)
    skills = models.JSONField(default=list)
    email_or_link = models.CharField(max_length=300)
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.job_title} {self.company} {self.address}'

#for adding the list of applicant
# class ProgramApplication(models.Model):
#     applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='program_applications')
#     program = models.ForeignKey(Programs, on_delete=models.CASCADE, related_name='applications')
    
#     applied_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('applicant', 'program')  # Prevent multiple applications to the same program

#     def __str__(self):
#         return f'{self.applicant.username} applied to {self.program.program_name}'

class ProgramApplication(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Declined', 'Declined'),
    ]

    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='program_applications')
    program = models.ForeignKey(Programs, on_delete=models.CASCADE, related_name='applications')
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')  # <-- Add this
    decline_reason = models.TextField(blank=True, null=True)  # <-- Add this
    
    # Fields for tracking incomplete/incorrect information
    marked_fields = models.JSONField(blank=True, null=True, default=dict)  # Store field names that need correction
    is_under_review = models.BooleanField(default=False)  # Flag to indicate if application is under review
    review_notes = models.TextField(blank=True, null=True)  # Admin notes about what needs correction
    reviewed_at = models.DateTimeField(null=True, blank=True)  # When the review was done

    class Meta:
        unique_together = ('applicant', 'program')

    def __str__(self):
        return f'{self.applicant.username} applied to {self.program.program_name}'


class ApprovedApplicant(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('finished', 'Finished'),
        ('dropped', 'Dropped'),
    ]
    
    APPLICATION_TYPE_CHOICES = [
        ('online', 'Online'),
        ('walkin', 'Walk-in'),
    ]
    
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='approved_programs')
    program = models.ForeignKey(Programs, on_delete=models.CASCADE, related_name='approved_applicants')
    approved_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    application_type = models.CharField(max_length=20, choices=APPLICATION_TYPE_CHOICES, default='online')  # Track application origin
    progress = models.IntegerField(default=0)  # Progress percentage
    total_present = models.IntegerField(default=0)
    total_absent = models.IntegerField(default=0)
    
    # Batch cycle tracking
    batch_number = models.CharField(max_length=10, null=True, blank=True)  # e.g., "1", "2", "3"
    enrollment_year = models.IntegerField(null=True, blank=True)  # e.g., 2025
    enrollment_semester = models.CharField(max_length=10, null=True, blank=True)  # Semester at enrollment: "1", "2", "3"

    class Meta:
        unique_together = ('applicant', 'program')

    def __str__(self):
        batch_info = f' - Batch {self.batch_number}, {self.enrollment_year}' if self.batch_number and self.enrollment_year else ''
        return f'{self.applicant.username} - {self.program.program_name}{batch_info}'


class ApplicantPasser(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='passed_programs')
    program = models.ForeignKey(Programs, on_delete=models.CASCADE, related_name='passed_applicants')
    trainee_name = models.CharField(max_length=255)
    program_name = models.CharField(max_length=255)
    final_progress = models.IntegerField(default=0)  # Final progress percentage
    total_present = models.IntegerField(default=0)
    total_absent = models.IntegerField(default=0)
    enrollment_date = models.DateTimeField()  # Original enrollment date
    completion_date = models.DateTimeField(auto_now_add=True)  # When marked as finished
    
    class Meta:
        unique_together = ('applicant', 'program')
        ordering = ['-completion_date']

    def __str__(self):
        return f'{self.trainee_name} - {self.program_name} (Passed)'


# Signal to create notification when ApplicantPasser is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=ApplicantPasser)
def create_program_completion_notification(sender, instance, created, **kwargs):
    """Automatically create a notification when an applicant passes a program"""
    if created:  # Only when a new ApplicantPasser is created
        # Import here to avoid circular imports
        from django.apps import apps
        Notification = apps.get_model('Applicant', 'Notification')
        
        # Create notification for the applicant
        Notification.objects.create(
            recipient=instance.applicant,
            sender=None,  # System notification
            notification_type='program_completion',
            title='Program Completion',
            message=f'Congratulations! You have successfully completed the {instance.program_name} program.',
            is_read=False
        )


from django.db import models
from django.conf import settings  # Import settings instead of User
from django.utils import timezone

# Your existing models (Programs, ProgramApplication, etc.)
# ... keep all your existing models ...

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('application', 'Program Application'),
        ('approval', 'Application Approval'),
        ('rejection', 'Application Rejection'),
        ('program_completion', 'Program Completion'),
    ]
    
    # Use settings.AUTH_USER_MODEL instead of User
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"




class ClientClassification(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class DisabilityType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class DisabilityCause(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class EducationalAttainment(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Learner_Profile(models.Model):

    user = models.ForeignKey(Applicant, on_delete=models.CASCADE, null=True, blank=True, related_name='learner_profile')

    entry_date = models.DateField(null=True, blank=True)

    id_picture = models.ImageField(upload_to='uploads/id_pictures/', null=True, blank=True)


    # Name fields
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)

    # Address details
    region = models.CharField(max_length=100)
    region_name = models.CharField(max_length=255, null=True, blank=True)

    province = models.CharField(max_length=100)
    province_name = models.CharField(max_length=255, null=True, blank=True)

    city = models.CharField(max_length=100)
    city_name = models.CharField(max_length=255, null=True, blank=True)

    barangay = models.CharField(max_length=100)
    barangay_name = models.CharField(max_length=255, null=True, blank=True)

    district = models.CharField(max_length=100, blank=True, null=True)

    street = models.CharField(max_length=255)  # <- Must be here
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField()
    nationality = models.CharField(max_length=255, default='Filipino')

    #new add column
    sex = models.CharField(max_length=10, default='Not Specified')
    civil_status = models.CharField(max_length=20, null=True, blank=True)
    employment_status = models.CharField(max_length=20, null=True, blank=True)
    monthly_income = models.CharField(max_length=50, null=True, blank=True)
    date_hired = models.DateField(null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)

    birthplace_regionb_name = models.CharField(max_length=255, null=True, blank=True)
    birthplace_provinceb_name = models.CharField(max_length=255, null=True, blank=True)
    birthplace_cityb_name = models.CharField(max_length=255, null=True, blank=True)

    educational_attainment = models.CharField(max_length=100, null=True, blank=True)
    parent_guardian = models.CharField(max_length=255, null=True, blank=True)
    permanent_address = models.CharField(max_length=255, null=True, blank=True)

    # New fields from form
    classifications = models.ManyToManyField(ClientClassification, blank=True)
    other_classification = models.CharField(max_length=255, null=True, blank=True)

    disability_types = models.ManyToManyField(DisabilityType, blank=True)
    disability_causes = models.ManyToManyField(DisabilityCause, blank=True)

    course_or_qualification = models.CharField(max_length=255, null=True, blank=True)
    scholarship_package = models.CharField(max_length=255, null=True, blank=True)

    # Privacy disclaimer
    agree_to_privacy = models.BooleanField(default=False)

    # Applicant signature section
    applicant_signature = models.ImageField(upload_to='signatures/', null=True, blank=True)
    applicant_name = models.CharField(max_length=255, null=True, blank=True)
    date_accomplished = models.DateField(null=True, blank=True)


    def __str__(self):
        return f"{self.last_name}, {self.first_name}"


class TrainerProfile(models.Model):
    user = models.OneToOneField(Applicant, on_delete=models.CASCADE)  # Use Applicant instead
    programs = models.ManyToManyField(Programs, related_name='trainers', blank=True)  # Support multiple programs
    # Keep the old 'program' field for backward compatibility during migration
    program = models.ForeignKey(Programs, on_delete=models.SET_NULL, null=True, blank=True, related_name='legacy_trainers')

    def __str__(self):
        program_names = ', '.join([p.program_name for p in self.programs.all()])
        return f"{self.user} - {program_names if program_names else 'No Programs'}"
    


from django.db import models
from django.contrib.auth import get_user_model

# Get the custom user model
User = get_user_model()

# In your models.py, update the Training model:
class Training(models.Model):
    CATEGORY_CHOICES = [
        ('activity', 'Activity'),
        ('examination', 'Examination'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
    ]
    
    program_name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)  # ✅ Add this if missing
    task_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    room_lab = models.CharField(max_length=100)
    trainer = models.ForeignKey('Applicant', on_delete=models.CASCADE, limit_choices_to={'is_staff': True})
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='activity')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Batch Cycle tracking - Added for consistency with BatchCycle logic
    batch_number = models.CharField(max_length=10, null=True, blank=True)  # e.g., "1", "2", "3"
    semester = models.CharField(max_length=10, null=True, blank=True)  # e.g., "1", "2", "3" for 1st, 2nd, 3rd semester
    enrollment_year = models.IntegerField(null=True, blank=True)  # e.g., 2025
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Training Session'
        verbose_name_plural = 'Training Sessions'

    def __str__(self):
        return f"{self.program_name} - {self.start_date} ({self.trainer.get_full_name() or self.trainer.username})"

class Attendance(models.Model):
    ATTENDANCE_CHOICES = [
        ('present', 'Present'),
        ('missed', 'Missed'),
    ]
    
    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    attendance_date = models.DateField(null=True, blank=True)  # New field for multi-day training
    status = models.CharField(max_length=10, choices=ATTENDANCE_CHOICES, default='missed')
    recorded_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recorded_attendances')
    
    class Meta:
        unique_together = ['training', 'student', 'attendance_date']  # Updated to include date
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'
    
    def __str__(self):
        date_str = f" - {self.attendance_date}" if self.attendance_date else ""
        return f"{self.student.username} - {self.training.program_name}{date_str} - {self.status}"
    

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

# Add a Task model to your models.py
class Task(models.Model):
    name = models.CharField(max_length=255)
    task_id = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class TaskCompletion(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    student = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['task', 'student']


class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    full_name = models.CharField(max_length=100)
    # Add other employer-specific fields as needed
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.full_name


# Walk-in Application Models
class WalkInApplication(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Declined', 'Declined'),
    ]

    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='walkin_applications')
    program = models.ForeignKey(Programs, on_delete=models.CASCADE, related_name='walkin_applications')
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    decline_reason = models.TextField(blank=True, null=True)
    is_walkin = models.BooleanField(default=True)  # To distinguish from regular applications
    
    # Additional walk-in specific fields
    queue_number = models.IntegerField(null=True, blank=True)
    processed_by = models.ForeignKey(Applicant, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_walkins')
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('applicant', 'program')
        ordering = ['-applied_at']

    def __str__(self):
        return f'Walk-in: {self.applicant.username} applied to {self.program.program_name}'


class ApprovedWalkIn(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('finished', 'Finished'),
        ('dropped', 'Dropped'),
    ]
    
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='approved_walkin_programs')
    program = models.ForeignKey(Programs, on_delete=models.CASCADE, related_name='approved_walkins')
    original_application = models.ForeignKey(WalkInApplication, on_delete=models.CASCADE, related_name='approval')
    approved_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(Applicant, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_walkins')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    progress = models.IntegerField(default=0)  # Progress percentage
    total_present = models.IntegerField(default=0)
    total_absent = models.IntegerField(default=0)
    
    # Batch cycle tracking
    batch_number = models.CharField(max_length=10, null=True, blank=True)  # e.g., "1", "2", "3"
    enrollment_year = models.IntegerField(null=True, blank=True)  # e.g., 2025

    class Meta:
        unique_together = ('applicant', 'program')
        ordering = ['-approved_at']

    def __str__(self):
        batch_info = f' - Batch {self.batch_number}, {self.enrollment_year}' if self.batch_number and self.enrollment_year else ''
        return f'Approved Walk-in: {self.applicant.username} - {self.program.program_name}{batch_info}'


class WalkInPasser(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='passed_walkin_programs')
    program = models.ForeignKey(Programs, on_delete=models.CASCADE, related_name='passed_walkins')
    original_application = models.ForeignKey(WalkInApplication, on_delete=models.CASCADE, related_name='completion')
    trainee_name = models.CharField(max_length=255)
    program_name = models.CharField(max_length=255)
    final_progress = models.IntegerField(default=0)  # Final progress percentage
    total_present = models.IntegerField(default=0)
    total_absent = models.IntegerField(default=0)
    enrollment_date = models.DateTimeField()  # Original enrollment date
    completion_date = models.DateTimeField(auto_now_add=True)  # When marked as finished
    
    class Meta:
        unique_together = ('applicant', 'program')
        ordering = ['-completion_date']

    def __str__(self):
        return f'Walk-in Passed: {self.trainee_name} - {self.program_name}'


# DMS (Document Management System) Models
class DMSReview(models.Model):
    APPLICATION_TYPE_CHOICES = [
        ('program', 'Program Application'),
        ('walkin', 'Walk-in Application'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('incomplete', 'Incomplete'),
        ('ready_for_approval', 'Ready for Approval'),
    ]
    
    # Generic foreign key to handle both ProgramApplication and WalkInApplication
    application_type = models.CharField(max_length=20, choices=APPLICATION_TYPE_CHOICES)
    application_id = models.PositiveIntegerField()  # ID of the related application
    
    # Application details (copied for easier access)
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='dms_reviews')
    program = models.ForeignKey(Programs, on_delete=models.CASCADE, related_name='dms_reviews')
    
    # Review status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(Applicant, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    
    # Document completeness tracking
    has_id_picture = models.BooleanField(default=False)
    has_learner_profile = models.BooleanField(default=False)
    has_signature = models.BooleanField(default=False)
    has_required_documents = models.BooleanField(default=False)
    
    # Review notes
    review_notes = models.TextField(blank=True, null=True)
    missing_documents = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('application_type', 'application_id')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'DMS Review: {self.applicant.username} - {self.program.program_name} ({self.get_status_display()})'
    
    @property
    def is_complete(self):
        """Check if all required documents are present"""
        return all([
            self.has_id_picture,
            self.has_learner_profile,
            self.has_signature,
            self.has_required_documents
        ])
    
    def get_original_application(self):
        """Get the original application object"""
        if self.application_type == 'program':
            return ProgramApplication.objects.get(id=self.application_id)
        elif self.application_type == 'walkin':
            return WalkInApplication.objects.get(id=self.application_id)
        return None


class DMSApproval(models.Model):
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('pending_final_approval', 'Pending Final Approval'),
    ]
    
    # Link to the DMS Review
    dms_review = models.OneToOneField(DMSReview, on_delete=models.CASCADE, related_name='approval')
    
    # Application details (copied for easier access)
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='dms_approvals')
    program = models.ForeignKey(Programs, on_delete=models.CASCADE, related_name='dms_approvals')
    application_type = models.CharField(max_length=20, choices=DMSReview.APPLICATION_TYPE_CHOICES)
    
    # Approval details
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_final_approval')
    approved_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(Applicant, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_applications')
    
    # Final approval tracking
    final_approved_at = models.DateTimeField(null=True, blank=True)
    final_approved_by = models.ForeignKey(Applicant, on_delete=models.SET_NULL, null=True, blank=True, related_name='final_approved_applications')
    
    # Approval notes
    approval_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'DMS Approval: {self.applicant.username} - {self.program.program_name} ({self.get_status_display()})'


# Document Management Models for Manuals and Policy
class DocumentCategory(models.Model):
    CATEGORY_CHOICES = [
        ('manual', 'Manual'),
        ('policy', 'Policy'),
    ]
    
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Document Categories'
        ordering = ['category_type', 'name']
    
    def __str__(self):
        return f"{self.get_category_type_display()} - {self.name}"


class ManualDocument(models.Model):
    BATCH_CHOICES = [
        ('batch_1', 'Batch 1'),
        ('batch_2', 'Batch 2'),
        ('batch_3', 'Batch 3'),
        ('batch_4', 'Batch 4'),
        ('batch_5', 'Batch 5'),
    ]
    
    SEMESTER_CHOICES = [
        ('semester_1', 'Semester 1'),
        ('semester_2', 'Semester 2'),
        ('semester_3', 'Semester 3'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('draft', 'Draft'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    document_file = models.FileField(upload_to='documents/manuals/')
    category = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE, limit_choices_to={'category_type': 'manual'})
    program = models.ForeignKey(Programs, on_delete=models.CASCADE, null=True, blank=True)
    batch = models.CharField(max_length=20, choices=BATCH_CHOICES, null=True, blank=True)
    semester = models.CharField(max_length=20, choices=SEMESTER_CHOICES, null=True, blank=True)
    version = models.CharField(max_length=10, default='1.0')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    uploaded_by = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='uploaded_manuals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Manual Document'
        verbose_name_plural = 'Manual Documents'
    
    def __str__(self):
        return f"{self.title} - {self.get_batch_display() or 'No Batch'} - {self.get_semester_display() or 'No Semester'}"


class PolicyDocument(models.Model):
    BATCH_CHOICES = [
        ('batch_1', 'Batch 1'),
        ('batch_2', 'Batch 2'),
        ('batch_3', 'Batch 3'),
        ('batch_4', 'Batch 4'),
        ('batch_5', 'Batch 5'),
    ]
    
    SEMESTER_CHOICES = [
        ('semester_1', 'Semester 1'),
        ('semester_2', 'Semester 2'),
        ('semester_3', 'Semester 3'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('draft', 'Draft'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    document_file = models.FileField(upload_to='documents/policies/')
    category = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE, limit_choices_to={'category_type': 'policy'})
    program = models.ForeignKey(Programs, on_delete=models.CASCADE, null=True, blank=True)
    batch = models.CharField(max_length=20, choices=BATCH_CHOICES, null=True, blank=True)
    semester = models.CharField(max_length=20, choices=SEMESTER_CHOICES, null=True, blank=True)
    version = models.CharField(max_length=10, default='1.0')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    uploaded_by = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='uploaded_policies')
    effective_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Policy Document'
        verbose_name_plural = 'Policy Documents'
    
    def __str__(self):
        return f"{self.title} - {self.get_batch_display() or 'No Batch'} - {self.get_semester_display() or 'No Semester'}"


# Archive model for training sessions
class ArchivedTraining(models.Model):
    CATEGORY_CHOICES = [
        ('activity', 'Activity'),
        ('examination', 'Examination'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
    ]
    
    # Original training data
    original_training_id = models.IntegerField()  # Store the original Training ID
    program_name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    task_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    room_lab = models.CharField(max_length=100)
    trainer = models.ForeignKey('Applicant', on_delete=models.CASCADE, limit_choices_to={'is_staff': True})
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='activity')
    description = models.TextField(blank=True, null=True)
    
    # Archive metadata
    archived_at = models.DateTimeField(auto_now_add=True)
    archived_by = models.ForeignKey('Applicant', on_delete=models.CASCADE, related_name='archived_trainings')
    archive_reason = models.TextField(blank=True, null=True)
    
    # Original timestamps
    original_created_at = models.DateTimeField()
    original_updated_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-archived_at']
        verbose_name = 'Archived Training Session'
        verbose_name_plural = 'Archived Training Sessions'

    def __str__(self):
        return f"Archived: {self.program_name} - {self.start_date} ({self.trainer.get_full_name() or self.trainer.username})"


# TrainingArchive model as requested by user
class TrainingArchive(models.Model):
    CATEGORY_CHOICES = [
        ('activity', 'Activity'),
        ('examination', 'Examination'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
    ]
    
    # Original training data
    original_training_id = models.IntegerField()  # Store the original Training ID
    program_name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    task_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    room_lab = models.CharField(max_length=100)
    trainer = models.ForeignKey('Applicant', on_delete=models.CASCADE, limit_choices_to={'is_staff': True})
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='activity')
    description = models.TextField(blank=True, null=True)
    
    # Archive metadata
    archived_at = models.DateTimeField(auto_now_add=True)
    archived_by = models.ForeignKey('Applicant', on_delete=models.CASCADE, related_name='training_archives')
    archive_reason = models.TextField(blank=True, null=True)
    
    # Original timestamps
    original_created_at = models.DateTimeField()
    original_updated_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-archived_at']
        verbose_name = 'Training Archive'
        verbose_name_plural = 'Training Archives'

    def __str__(self):
        return f"Archive: {self.program_name} - {self.start_date} ({self.trainer.get_full_name() or self.trainer.username})"


# Event model for Enrollment Management
class Event(models.Model):
    CATEGORY_CHOICES = [
        ('enrollment', 'Enrollment'),
        ('departmental', 'Departmental'),
    ]
    
    BATCH_CHOICES = [
        ('1', 'Batch 1'),
        ('2', 'Batch 2'),
        ('3', 'Batch 3'),
    ]
    
    TRIMESTER_CHOICES = [
        ('1', '1st Semester'),
        ('2', '2nd Semester'),
        ('3', '3rd Semester'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('completed', 'Completed'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='enrollment')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    batch = models.CharField(max_length=10, choices=BATCH_CHOICES, null=True, blank=True)
    trimester = models.CharField(max_length=10, choices=TRIMESTER_CHOICES, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    batch_activated = models.BooleanField(default=False)  # Track if this event activated a batch
    created_by = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date', '-created_at']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
    
    def __str__(self):
        return f"{self.title} - {self.start_date} ({self.get_category_display()})"


# Batch Cycle Management Model
class BatchCycle(models.Model):
    BATCH_CHOICES = [
        ('1', 'Batch 1'),
        ('2', 'Batch 2'),
        ('3', 'Batch 3'),
    ]
    
    SEMESTER_CHOICES = [
        ('1', '1st Semester'),
        ('2', '2nd Semester'),
        ('3', '3rd Semester'),
    ]
    
    STATE_CHOICES = [
        ('waiting_enrollment', 'Waiting for Enrollment Event'),
        ('enrollment_active', 'Enrollment Event Active'),
        ('batch_active', 'Batch Active'),
        ('trimester_1', '1st Semester Active'),
        ('trimester_2', '2nd Semester Active'),
        ('trimester_3', '3rd Semester Active'),
        ('trimester_completed', 'Trimester Completed - Waiting for Next Enrollment'),
    ]
    
    # Current active batch (1, 2, or 3)
    current_batch = models.CharField(max_length=10, choices=BATCH_CHOICES, default='1')
    
    # Current state of the batch cycle
    cycle_state = models.CharField(max_length=30, choices=STATE_CHOICES, default='waiting_enrollment')
    
    # Current active semester/trimester within the batch
    current_semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES, default='1')
    
    # Track which semesters have been completed (JSON format)
    # Example: {"1": true, "2": true, "3": false}
    completed_semesters = models.JSONField(default=dict, blank=True)
    
    # Reference to the active enrollment event
    active_enrollment_event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name='active_batch_cycle')
    
    # Tracking dates
    batch_started_at = models.DateTimeField(null=True, blank=True)
    last_semester_completed_at = models.DateTimeField(null=True, blank=True)
    
    # System tracking
    is_active = models.BooleanField(default=True)  # Only one active cycle at a time
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Batch Cycle'
        verbose_name_plural = 'Batch Cycles'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Batch {self.current_batch} - {self.get_cycle_state_display()}"
    
    @classmethod
    def get_active_cycle(cls):
        """Get or create the active batch cycle"""
        # First, try to get an active cycle
        cycle = cls.objects.filter(is_active=True).first()
        
        if cycle:
            # If there are multiple active cycles, deactivate the older ones
            if cls.objects.filter(is_active=True).count() > 1:
                # Keep the most recent one, deactivate the rest
                active_cycles = cls.objects.filter(is_active=True).order_by('-created_at')
                most_recent = active_cycles.first()
                active_cycles.exclude(id=most_recent.id).update(is_active=False)
                cycle = most_recent
            return cycle
        
        # If no active cycle exists, create one
        cycle = cls.objects.create(
            is_active=True,
            current_batch='1',
            cycle_state='waiting_enrollment',
            current_semester='1',
            completed_semesters={'1': False, '2': False, '3': False}
        )
        return cycle
    
    def activate_batch_from_event(self, enrollment_event):
        """Activate batch when enrollment event ends"""
        from django.utils import timezone
        
        self.active_enrollment_event = enrollment_event
        self.cycle_state = 'batch_active'
        self.batch_started_at = timezone.now()
        self.current_semester = '1'
        self.completed_semesters = {'1': False, '2': False, '3': False}
        self.save()
        
        # Mark event as having activated a batch
        enrollment_event.batch_activated = True
        enrollment_event.save()
    
    def complete_semester(self, semester):
        """Mark a semester as completed"""
        from django.utils import timezone
        
        self.completed_semesters[semester] = True
        self.last_semester_completed_at = timezone.now()
        
        # Check if all semesters are completed
        if all(self.completed_semesters.values()):
            self.cycle_state = 'trimester_completed'
        
        self.save()
    
    def progress_to_next_batch(self):
        """Move to the next batch in the cycle (1 -> 2 -> 3 -> 1)"""
        batch_map = {'1': '2', '2': '3', '3': '1'}
        self.current_batch = batch_map.get(self.current_batch, '1')
        self.cycle_state = 'waiting_enrollment'
        self.current_semester = '1'
        self.completed_semesters = {'1': False, '2': False, '3': False}
        self.active_enrollment_event = None
        self.save()
    
    def can_start_enrollment(self):
        """Check if a new enrollment event can be started"""
        return self.cycle_state in ['waiting_enrollment', 'trimester_completed']


# Active Batch and Semester Settings for Trainers
class ActiveSemesterSettings(models.Model):
    BATCH_CHOICES = [
        ('1', 'Batch 1'),
        ('2', 'Batch 2'),
        ('3', 'Batch 3'),
    ]
    
    SEMESTER_CHOICES = [
        ('1', '1st Semester'),
        ('2', '2nd Semester'),
        ('3', '3rd Semester'),
    ]
    
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]
    
    trainer = models.OneToOneField(Applicant, on_delete=models.CASCADE, related_name='semester_settings', limit_choices_to={'is_staff': True})
    active_batch = models.CharField(max_length=10, choices=BATCH_CHOICES, default='1')
    active_semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES, default='1')
    semester_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')
    completed_semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES, null=True, blank=True)  # Track which semester was completed
    completed_at = models.DateTimeField(null=True, blank=True)  # When the semester was marked complete
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Active Semester Setting'
        verbose_name_plural = 'Active Semester Settings'
    
    def __str__(self):
        return f"{self.trainer.username} - Batch {self.active_batch}, Semester {self.active_semester}"
    
    @classmethod
    def get_or_create_for_trainer(cls, trainer):
        """Get or create settings for a trainer"""
        settings, created = cls.objects.get_or_create(
            trainer=trainer,
            defaults={'active_batch': '1', 'active_semester': '1'}
        )
        return settings
    
    def complete_semester(self):
        """Mark current semester as completed"""
        from django.utils import timezone
        self.semester_status = 'completed'
        self.completed_semester = self.active_semester
        self.completed_at = timezone.now()
        self.save()
    
    def get_remark(self):
        """Get the remark for this trainer's program status"""
        if self.semester_status == 'completed':
            semester_map = {'1': '1st', '2': '2nd', '3': '3rd'}
            return f"{semester_map.get(self.completed_semester, '')} Sem Complete"
        return "Ongoing"


# LMSTC Documents Model for Bulk Operations
class LMSTC_Documents(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('applicant_profile', 'Applicant Profile'),
        ('policy_guidelines', 'Policy and Guidelines'),
        ('modules_manuals', 'Modules and Manuals'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    
    BATCH_CHOICES = [
        ('batch_1', 'Batch 1'),
        ('batch_2', 'Batch 2'),
        ('batch_3', 'Batch 3'),
        ('batch_4', 'Batch 4'),
        ('batch_5', 'Batch 5'),
    ]
    
    # Document information
    document_name = models.CharField(max_length=255)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    document_file = models.FileField(upload_to='lmstc_documents/')
    description = models.TextField(blank=True, null=True)
    
    # Categorization
    batch = models.CharField(max_length=20, choices=BATCH_CHOICES, null=True, blank=True)
    program = models.ForeignKey(Programs, on_delete=models.SET_NULL, null=True, blank=True, related_name='lmstc_documents')
    
    # Associated applicant (optional, for applicant profiles)
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, null=True, blank=True, related_name='lmstc_documents')
    
    # Link to Learner_Profile for displaying applicant profile documents
    learner_profile = models.ForeignKey(Learner_Profile, on_delete=models.CASCADE, null=True, blank=True, related_name='lmstc_documents')
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    uploaded_by = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='uploaded_lmstc_documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional metadata
    file_size = models.BigIntegerField(null=True, blank=True)  # Store file size in bytes
    mime_type = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'LMSTC Document'
        verbose_name_plural = 'LMSTC Documents'
    
    def __str__(self):
        return f"{self.document_name} ({self.get_document_type_display()})"
    
    def get_file_size_display(self):
        """Return human-readable file size"""
        if not self.file_size:
            return "Unknown"
        
        # Convert bytes to appropriate unit
        size = float(self.file_size)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"


# Document Audit Log Model
class DocumentAuditLog(models.Model):
    ACTION_CHOICES = [
        ('upload', 'Upload'),
        ('view', 'View'),
        ('download', 'Download'),
        ('edit', 'Edit'),
        ('archive', 'Archive'),
        ('restore', 'Restore'),
        ('delete', 'Delete'),
    ]
    
    # Document reference (can be any document type)
    document_type = models.CharField(max_length=50)  # 'manual', 'policy', 'lmstc_document', 'learner_profile'
    document_id = models.IntegerField()
    document_name = models.CharField(max_length=255)
    
    # Action details
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='document_actions')
    performed_at = models.DateTimeField(auto_now_add=True)
    
    # Additional information
    reason = models.TextField(blank=True, null=True)  # For delete/archive actions
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Previous state (for edit actions)
    previous_data = models.JSONField(blank=True, null=True)
    new_data = models.JSONField(blank=True, null=True)
    
    class Meta:
        ordering = ['-performed_at']
        verbose_name = 'Document Audit Log'
        verbose_name_plural = 'Document Audit Logs'
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.document_name} by {self.performed_by.username}"


# Model to save trainee competencies with checkbox states and percentages
class ApplicantCompetencies(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='competencies')
    program = models.ForeignKey(Programs, on_delete=models.CASCADE, related_name='trainee_competencies')
    
    # JSON fields to store checkbox states for each competency type
    # Format: {"0": true, "1": false, "2": true} where key is the competency index
    basic_competencies = models.JSONField(default=dict, blank=True)
    common_competencies = models.JSONField(default=dict, blank=True)
    core_competencies = models.JSONField(default=dict, blank=True)
    
    # Percentage completion for each competency type
    basic_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    common_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    core_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Overall progress percentage
    overall_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Tracking fields
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('applicant', 'program')
        verbose_name = 'Applicant Competency'
        verbose_name_plural = 'Applicant Competencies'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.applicant.username} - {self.program.program_name} (Overall: {self.overall_percentage}%)"
    
    def calculate_percentages(self):
        """Calculate percentage completion for each competency type based on actual program competencies"""
        # Get the total number of competencies from the program
        program_competencies = self.program.program_competencies or {}
        
        # Count total competencies in the program
        total_basic = len(program_competencies.get('basic_competencies', []))
        total_common = len(program_competencies.get('common_competencies', []))
        total_core = len(program_competencies.get('core_competencies', []))
        
        # Count checked competencies
        checked_basic = sum(1 for v in self.basic_competencies.values() if v)
        checked_common = sum(1 for v in self.common_competencies.values() if v)
        checked_core = sum(1 for v in self.core_competencies.values() if v)
        
        # Calculate percentages based on program total, not dictionary keys
        self.basic_percentage = round((checked_basic / total_basic * 100), 2) if total_basic > 0 else 0.00
        self.common_percentage = round((checked_common / total_common * 100), 2) if total_common > 0 else 0.00
        self.core_percentage = round((checked_core / total_core * 100), 2) if total_core > 0 else 0.00
        
        # Calculate overall percentage
        total_competencies = total_basic + total_common + total_core
        total_checked = checked_basic + checked_common + checked_core
        self.overall_percentage = round((total_checked / total_competencies * 100), 2) if total_competencies > 0 else 0.00
    
    def save(self, *args, **kwargs):
        """Override save to automatically calculate percentages"""
        self.calculate_percentages()
        super().save(*args, **kwargs)


# Support Ticket Model
class SupportTicket(models.Model):
    CATEGORY_CHOICES = [
        ('academic', 'Academic/Training Issues'),
        ('technical', 'Technical Issues'),
        ('administrative', 'Administrative Issues'),
        ('complaint', 'Complaint'),
        ('other', 'Other'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low - General inquiry'),
        ('medium', 'Medium - Standard issue'),
        ('high', 'High - Urgent matter'),
    ]
    
    RECIPIENT_CHOICES = [
        ('admin', 'Admin Support'),
        ('trainer', 'My Trainer'),
        ('both', 'Both Admin & Trainer'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    # Basic ticket information
    ticket_id = models.CharField(max_length=20, unique=True, editable=False)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    recipient = models.CharField(max_length=10, choices=RECIPIENT_CHOICES, default='admin')
    
    # Ticket status and tracking
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    created_by = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='created_tickets')
    assigned_to = models.ForeignKey(Applicant, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    
    # File attachment
    attachment = models.FileField(upload_to='ticket_attachments/', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Response tracking
    admin_response = models.TextField(blank=True, null=True)
    trainer_response = models.TextField(blank=True, null=True)
    response_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Support Ticket'
        verbose_name_plural = 'Support Tickets'
    
    def __str__(self):
        return f"#{self.ticket_id} - {self.subject} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            # Generate unique ticket ID
            import random
            import string
            from django.utils import timezone
            
            # Format: TKT-YYYYMMDD-XXXX (e.g., TKT-20241017-A1B2)
            date_str = timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            self.ticket_id = f"TKT-{date_str}-{random_str}"
            
            # Ensure uniqueness
            while SupportTicket.objects.filter(ticket_id=self.ticket_id).exists():
                random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                self.ticket_id = f"TKT-{date_str}-{random_str}"
        
        super().save(*args, **kwargs)
    
    def get_priority_badge_class(self):
        """Return CSS class for priority badge"""
        priority_classes = {
            'low': 'bg-green-100 text-green-800',
            'medium': 'bg-yellow-100 text-yellow-800',
            'high': 'bg-red-100 text-red-800',
        }
        return priority_classes.get(self.priority, 'bg-gray-100 text-gray-800')
    
    def get_status_badge_class(self):
        """Return CSS class for status badge"""
        status_classes = {
            'open': 'bg-blue-100 text-blue-800',
            'in_progress': 'bg-yellow-100 text-yellow-800',
            'resolved': 'bg-green-100 text-green-800',
            'closed': 'bg-gray-100 text-gray-800',
        }
        return status_classes.get(self.status, 'bg-gray-100 text-gray-800')


# Ticket Response Model for conversation tracking
class TicketResponse(models.Model):
    RESPONDER_TYPE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
        ('trainer', 'Trainer'),
    ]
    
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='ticket_responses')
    responder_type = models.CharField(max_length=10, choices=RESPONDER_TYPE_CHOICES)
    message = models.TextField()
    attachment = models.FileField(upload_to='ticket_response_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Ticket Response'
        verbose_name_plural = 'Ticket Responses'
    
    def __str__(self):
        return f"Response to #{self.ticket.ticket_id} by {self.responder.username}"
        super().save(*args, **kwargs)