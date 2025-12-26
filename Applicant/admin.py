from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Applicant
from .models import Programs, ProgramImage
from .models import JobPost
from .models import ProgramApplication, TrainerProfile, ApprovedApplicant, Attendance, EmployerProfile, Task, Event, BatchCycle, StaffMember

from .models import Learner_Profile, ClientClassification, DisabilityType, DisabilityCause, EducationalAttainment, SupportTicket

admin.site.register(JobPost)
admin.site.register(Event)
admin.site.register(SupportTicket)
admin.site.register(BatchCycle)

admin.site.register(Applicant, UserAdmin)

class Program_Admin(admin.ModelAdmin):
  list_display = ("program_name", "program_sched")
  ordering = ("program_name",)

admin.site.register(Programs, Program_Admin)    

admin.site.register(ProgramImage)

admin.site.register(Attendance)

admin.site.register(Task)

@admin.register(ProgramApplication)
class ProgramApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'program', 'applied_at')
    search_fields = ('applicant__username', 'program__program_name')


admin.site.register(Learner_Profile)
admin.site.register(ClientClassification)
admin.site.register(DisabilityType)
admin.site.register(DisabilityCause)
admin.site.register(EducationalAttainment)
admin.site.register(EmployerProfile)

@admin.register(TrainerProfile)
class TrainerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'program']
    list_filter = ['program']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

admin.site.register(StaffMember)

admin.site.register(ApprovedApplicant)

from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'sender', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'recipient__username', 'sender__username']
    readonly_fields = ['created_at']
    list_per_page = 25
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient', 'sender')
    


# Add this to your admin.py file
from .models import Training

@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ['program_name', 'start_date', 'room_lab', 'trainer']
    list_filter = ['start_date', 'trainer']
    search_fields = ['program_name', 'room_lab', 'trainer__username']
    date_hierarchy = 'start_date'

# LMSTC Documents Admin
from .models import LMSTC_Documents

@admin.register(LMSTC_Documents)
class LMSTCDocumentsAdmin(admin.ModelAdmin):
    list_display = ['document_name', 'document_type', 'batch', 'program', 'uploaded_by', 'status', 'uploaded_at']
    list_filter = ['document_type', 'status', 'batch', 'uploaded_at']
    search_fields = ['document_name', 'description', 'uploaded_by__username', 'applicant__username']
    readonly_fields = ['uploaded_at', 'updated_at', 'file_size', 'mime_type']
    date_hierarchy = 'uploaded_at'
    list_per_page = 25
    
    fieldsets = (
        ('Document Information', {
            'fields': ('document_name', 'document_type', 'document_file', 'description')
        }),
        ('Categorization', {
            'fields': ('batch', 'program', 'applicant')
        }),
        ('Status & Metadata', {
            'fields': ('status', 'uploaded_by', 'file_size', 'mime_type', 'uploaded_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('program', 'applicant', 'uploaded_by')