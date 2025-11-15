from django.urls import path
from . import views
from . import ocr_views
from . import job_views
from . import job_matching_views
from . import document_views
from . import learner_views
from . import event_views
from . import program_api_views
from . import id_photo_views
from . import excel_export_views
from . import trainor_program_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Home and basic pages
    path('', views.Home, name='Index'),
    path('Applicant/', views.applicant, name='Applicant'),
    path('Home/', views.Home, name='Home'),
    path('About/', views.About, name='About'),
    path('About_user/', views.About_user, name='About_user'),
    path('Program/', views.Program, name='Program'),
    path('Program_user/', views.Program_user, name='Program_user'),
    path('Contact/', views.Contact, name='Contact'),
    path('Contact_user/', views.Contact_user, name='Contact_user'),
    
    # Authentication
    path('Login/', views.Login, name='Login'),
    path('Register/', views.Register, name='Register'),
    path('logout_view/', views.logout_view, name='logout_view'),
    path("redirect-after-login/", views.custom_redirect_view, name="custom_redirect_view"),
    path('Option/', views.Option, name='Option'),
    
    # Password Reset
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # Program Information
    path('Prog_Info/<int:id>/', views.Prog_Info, name='Prog_Info'),
    path('Prog_Info_user/<int:id>/', views.Prog_Info_user, name='Prog_Info_user'),
    path('apply/<int:program_id>/', views.apply_program, name='apply_program'),
    path('apply-program/<int:program_id>/', views.apply_program, name='apply_program'),
    
    # Dashboard URLs
    path('Login_Nextpage/', views.Login_Nextpage, name='Login_Nextpage'),
    path('Dashboard/', views.Dashboard, name='Dashboard'),
    path('Dashboard_admin/', views.Dashboard_admin, name='Dashboard_admin'),
    path('Dashboard_admin/<int:application_id>/', views.Dashboard_admin, name='Dashboard_admin'),
    path('Dashboard_trainor/', views.Dashboard_trainor, name='Dashboard_trainor'),
    path('Homepage_user/', views.Homepage_user, name='Homepage_user'),
    path('dashboard_view', views.dashboard_view, name='dashboard_view'),
    
    # Job Management
    path('api/philjobnet-jobs/', job_views.get_philjobnet_jobs, name='get_philjobnet_jobs'),
    
    # Job Matching with Skill Analysis (NEW)
    path('api/matched-jobs/', job_matching_views.get_matched_jobs, name='get_matched_jobs'),
    path('api/user-competencies/', job_matching_views.get_user_competencies_summary, name='get_user_competencies_summary'),
    path('api/test-skill-match/', job_matching_views.test_skill_match, name='test_skill_match'),

    # Certification page
    path('certification/', views.certification_view, name='certification'),
    path('add_job/', views.add_job, name='add_job'),
    path('job_list/', views.job_list, name='job_list'),
    path('archive_jobs/', views.archive_jobs, name='archive_jobs'),
    path('update_job/<int:job_id>/', views.update_job, name='update_job'),
    
    # Profile Management
    path('learner-form/', views.learner_profile_form, name='learner_form'),
    path('walkin-registration/', views.walkin_registration, name='walkin_registration'),
    path('walkin-step1-registration/', views.walkin_step1_registration, name='walkin_step1_registration'),
    path('api/profile/<int:profile_id>/', views.get_profile_data, name='get_profile_data'),
    path('profile/<int:pk>/', views.view_profile, name='view_profile'),
    path('profile_views', views.profile_views, name='profile_views'),
    path('update-profile/', views.update_profile, name='update_profile'),
    
    # Application Management
    path('applications_list', views.applications_list, name='applications_list'),
    path('approve-application/<int:application_id>/', views.approve_application, name='approve_application'),
    path('reject-application/<int:application_id>/', views.reject_application, name='reject_application'),
    path('decline-application/', views.decline_application, name='decline_application'),
    path('mark-incomplete-fields/', views.mark_incomplete_fields, name='mark_incomplete_fields'),
    path('update-marked-fields/', views.update_marked_fields, name='update_marked_fields'),
    path('resubmit-for-review/', views.resubmit_for_review, name='resubmit_for_review'),
    path('cancel-application/', views.cancel_application, name='cancel_application'),
    path('clear-modal-session/', views.clear_modal_session, name='clear_modal_session'),
    
    # API Endpoints
    path('register_v1/', views.register_v1, name='register_v1'),
    path('api/applicant/<int:applicant_id>/', views.get_applicant_datas, name='get_applicant_datas'),
    
    # ✅ NOTIFICATION URLs (Fixed and consolidated)
    path('get-notifications/', views.get_notifications, name='get_notifications'),
    path('mark-all-notifications-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('mark-notification-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    
    # ✅ ADD THIS MISSING URL PATTERN
    path('send-application-notification/', views.send_application_notification_view, name='send_application_notification'),
    
    # Employer URLs
    path('signup/', views.employer_signup, name='employer_signup'),
    path('login/', views.login_view, name='login'),
    path('Employer_signup/', views.Employer_signup, name='Employer_signup'),
    path('Employer_login/', views.Employer_login, name='Employer_login'),
    path('Employer_Dashboard/', views.Employer_Dashboard, name='Employer_Dashboard'),
    path('employer_signup/', views.employer_signup, name='employer_signup'),
    
    # Training Management URLs
    path('training/', views.training_management, name='training_management'),
    path('training/edit/<int:training_id>/', views.edit_training, name='edit_training'),
    path('training/delete/<int:training_id>/', views.delete_training, name='delete_training'),
    path('training/get/<int:training_id>/', views.get_training_data, name='get_training_data'),
    path('archive-training/', views.archive_training, name='archive_training'),
    
    # Semester Settings for Trainers
    path('save-semester-settings/', views.save_semester_settings, name='save_semester_settings'),
    path('end-semester/', views.end_semester, name='end_semester'),  # Trainor ends semester
    path('end-batch/', views.end_batch, name='end_batch'),  # Admin ends batch
    
    # Attendance URLs
    path('save-attendance/', views.save_attendance, name='save_attendance'),
    path('get-attendance/<int:training_id>/', views.get_attendance, name='get_attendance'),
    path('get-attendance-summary/<int:training_id>/', views.get_attendance_summary, name='get_attendance_summary'),
    path('get-student-attendance/<int:student_id>/', views.get_student_attendance_summary, name='get_student_attendance_summary'),
    
    # Task
    path('add-task/', views.add_task, name='add_task'),
    path('delete-task/', views.delete_task, name='delete_task'),
    path('save-task-completion/', views.save_task_completion, name='save_task_completion'),
    
    # Competency Management
    path('save-competency-state/', views.save_competency_state, name='save_competency_state'),
    path('get-competency-states/', views.get_competency_states, name='get_competency_states'),
    
    
    # Status update
    path('update-status/', views.update_status, name='update_status'),
    
    # Program Management
    path('add-program/', views.add_program, name='add_program'),
    path('edit-program/<int:program_id>/', views.edit_program, name='edit_program'),
    path('delete-program/<int:program_id>/', views.delete_program, name='delete_program'),
    
    # Walk-in Application Management
    path('approve-walkin/<int:application_id>/', views.approve_walkin, name='approve_walkin'),
    path('decline-walkin/<int:application_id>/', views.decline_walkin, name='decline_walkin'),
    # TODO: These views need to be implemented
    # path('create-walkin-account/', views.create_walkin_account, name='create_walkin_account'),
    # path('apply-walkin-program/', views.apply_walkin_program, name='apply_walkin_program'),
    # path('approve-walkin-application/<int:application_id>/', views.approve_walkin_application, name='approve_walkin_application'),
    
    # OCR Processing URLs
    path('process-excel-ocr/', ocr_views.process_excel_ocr, name='process_excel_ocr'),
    path('process-default-excel/', ocr_views.process_default_excel, name='process_default_excel'),
    path('save-excel-data/', ocr_views.save_excel_data, name='save_excel_data'),
    
    # Bulk Review and Approval URLs
    path('get_bulk_review_data/', views.get_bulk_review_data, name='get_bulk_review_data'),
    path('process_bulk_review/', views.process_bulk_review, name='process_bulk_review'),
    path('get_bulk_approval_data/', views.get_bulk_approval_data, name='get_bulk_approval_data'),
    path('process_bulk_approval/', views.process_bulk_approval, name='process_bulk_approval'),
    
    # Document Management URLs
    path('upload-document/', document_views.upload_document, name='upload_document'),
    path('search-documents/', document_views.search_documents, name='search_documents'),
    path('get-document-categories/', document_views.get_document_categories, name='get_document_categories'),
    
    # LMSTC Documents URLs
    path('bulk-upload-lmstc-documents/', document_views.bulk_upload_lmstc_documents, name='bulk_upload_lmstc_documents'),
    path('get-lmstc-documents/', document_views.get_lmstc_documents, name='get_lmstc_documents'),
    path('get-bulk-download-documents/', document_views.get_bulk_download_documents, name='get_bulk_download_documents'),
    
    # Document Operations URLs
    path('archive-document/', document_views.archive_document, name='archive_document'),
    path('restore-document/', document_views.restore_document, name='restore_document'),
    path('delete-document/', document_views.delete_document, name='delete_document'),
    path('bulk-archive-documents/', document_views.bulk_archive_documents, name='bulk_archive_documents'),
    path('bulk-delete-documents/', document_views.bulk_delete_documents, name='bulk_delete_documents'),
    path('get-archived-documents/', document_views.get_archived_documents, name='get_archived_documents'),
    path('get-document-audit-logs/', document_views.get_document_audit_logs, name='get_document_audit_logs'),
    
    # Excel Export URLs
    path('download-applicants-excel/', excel_export_views.download_applicants_excel, name='download_applicants_excel'),
    path('download-bulk-documents-excel/', excel_export_views.download_bulk_documents_excel, name='download_bulk_documents_excel'),
    
    # Learner Profile URLs
    path('get_learner_profile/<int:profile_id>/', learner_views.get_learner_profile, name='get_learner_profile'),
    path('download_learner_profile/<int:profile_id>/', learner_views.download_learner_profile, name='download_learner_profile'),
    path('download-profile-pdf/', learner_views.download_profile_pdf, name='download_profile_pdf'),
    path('download-registration-form/<int:profile_id>/', learner_views.registration_form_pdf, name='download_registration_form'),
    
    # Event Management URLs
    path('api/events/create/', event_views.create_event, name='create_event'),
    path('api/events/', event_views.get_events, name='get_events'),
    path('api/events/update/<int:event_id>/', event_views.update_event, name='update_event'),
    path('api/events/delete/<int:event_id>/', event_views.delete_event, name='delete_event'),
    path('api/events/archive/<int:event_id>/', event_views.archive_event, name='archive_event'),
    
    # Batch Cycle Management URLs
    path('api/batch-cycle/status/', event_views.get_batch_cycle_status, name='get_batch_cycle_status'),
    path('api/batch-cycle/check-enrollment/', event_views.check_enrollment_events, name='check_enrollment_events'),
    path('api/batch-cycle/complete-semester/', event_views.complete_semester, name='complete_semester'),
    path('api/batch-cycle/next-batch/', event_views.progress_to_next_batch, name='progress_to_next_batch'),
    path('api/batch-cycle/auto-check/', event_views.auto_check_and_activate_batch, name='auto_check_batch'),
    
    # ID Photo and Ticket Management URLs
    path('update-id-photo/', id_photo_views.update_id_photo, name='update_id_photo'),
    path('ticket/<int:ticket_id>/', id_photo_views.view_ticket, name='view_ticket'),
    
    # Support Ticket URLs
    path('create-ticket/', views.create_ticket, name='create_ticket'),
    path('get-user-tickets/', views.get_user_tickets, name='get_user_tickets'),
    path('get-ticket-details/<str:ticket_id>/', views.get_ticket_details, name='get_ticket_details'),
    path('get-all-tickets/', views.get_all_tickets, name='get_all_tickets'),
    path('update-ticket-status/', views.update_ticket_status, name='update_ticket_status'),
    
    # Program API URLs
    path('api/program/<int:program_id>/applicants/', program_api_views.get_program_applicants, name='get_program_applicants'),
    
    # Trainor Program Management URLs
    path('api/trainer/<int:trainer_id>/programs/', trainor_program_views.get_trainer_programs, name='get_trainer_programs'),
    path('api/trainer/<int:trainer_id>/assign-program/', trainor_program_views.assign_program_to_trainer, name='assign_program_to_trainer'),
    path('api/trainer/<int:trainer_id>/unassign-program/', trainor_program_views.unassign_program_from_trainer, name='unassign_program_from_trainer'),
    path('api/trainer/<int:trainer_id>/delete/', trainor_program_views.delete_trainer_account, name='delete_trainer_account'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)