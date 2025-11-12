from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from .models import Applicant
from django.contrib.auth.hashers import make_password
from django.contrib import messages
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()

from django.db.models import Count, Max
from django.db import models

from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET
from django.shortcuts import render
from .models import Programs
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib import messages
from .models import JobPost, ProgramApplication, ApprovedApplicant, Notification, Task, ApplicantPasser, WalkInApplication, ApprovedWalkIn, DMSReview, DMSApproval, Event, Training, ArchivedTraining, ProgramImage, SupportTicket, TicketResponse, BatchCycle, BatchCycle
from .models import Learner_Profile, ClientClassification, DisabilityType, DisabilityCause, EducationalAttainment
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST
import json
import string
import random
# import pandas as pd  # Temporarily commented out due to missing dependency
import os
from django.conf import settings
from .philjobnet_scraper import scrape_philjobnet_jobs
import logging


#newly
def logout_view(request):
    logout(request)
    return redirect('Login')

# View to render certification.html
def certification_view(request):
    template = loader.get_template('certification.html')
    return HttpResponse(template.render())


#Example
def applicant(request):
  template = loader.get_template('first.html')
  return HttpResponse(template.render())

# def Home(request):
#   template = loader.get_template('Homepage(Tailwind).html')
#   return HttpResponse(template.render())
  
def About(request):
  # Get all unique trainor names from Programs
  programs = Programs.objects.exclude(program_trainor__isnull=True).exclude(program_trainor='')
  trainors = programs.values_list('program_trainor', flat=True).distinct()
  
  context = {
      'trainors': trainors
  }
  
  template = loader.get_template('About.html')
  return HttpResponse(template.render(context, request))

# def About_user(request):
#   template = loader.get_template('About_user.html')
#   return HttpResponse(template.render())

from django.contrib.auth.decorators import login_required

# @never_cache
# @login_required
# def About_user(request):
#   programs = Programs.objects.all()
#   return render(request, 'About_user.html', {'Programss': programs})

@never_cache
def About_user(request):
    # Check if the user is authenticated, if not redirect to login
    if not request.user.is_authenticated:
        return redirect('Login')  # Redirect to login page if user is not logged in

    # Retrieve all programs if the user is authenticated
    programs = Programs.objects.all()
    
    # Get all unique trainor names from Programs
    trainor_programs = Programs.objects.exclude(program_trainor__isnull=True).exclude(program_trainor='')
    trainors = trainor_programs.values_list('program_trainor', flat=True).distinct()
    
    # Check if user has a Learner_Profile
    has_learner_profile = Learner_Profile.objects.filter(user=request.user).exists()
    
    # Get user's Google profile picture if available
    user_profile_picture = None
    try:
        from allauth.socialaccount.models import SocialAccount
        social_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
        if social_account and social_account.extra_data:
            user_profile_picture = social_account.extra_data.get('picture')
    except Exception as e:
        # If there's any error, just use the default
        pass
    
    # Render the About_user page with the programs data
    response = render(request, 'About_user.html', {
        'Programss': programs,
        'has_learner_profile': has_learner_profile,
        'trainors': trainors,
        'user_profile_picture': user_profile_picture
    })
    
    # Prevent caching (this will ensure the page is not cached in the browser)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response

def Program(request):
  programs = Programs.objects.all()
  return render(request, 'Programs.html', {'Programss': programs})

def Home(request):
  programs = Programs.objects.all()
  
  # Get enrollment event information
  from .enrollment_validation import get_enrollment_info
  enrollment_info = get_enrollment_info()
  
  return render(request, 'Homepage(Tailwind).html', {
      'Programss': programs,
      'enrollment_info': enrollment_info
  })

#tempo
def Program_list(request):
    programs = Programs.objects.all()
    return render(request, 'Dashboard_admin.html', {'Programss': programs})


# def Program_user(request):
#   programs = Programs.objects.all()
#   return render(request, 'Programs_user.html', {'Programss': programs})

def Program(request):
    programs = Programs.objects.prefetch_related('images').all()
    return render(request, 'Programs.html', {'Programss': programs})

@never_cache
def Program_user(request):
    # Check if the user is authenticated, if not redirect to login
    if not request.user.is_authenticated:
        return redirect('Login')  # Redirect to login page if user is not logged in

    # Retrieve all programs if the user is authenticated
    programs = Programs.objects.all()
    
    # Check if user has a Learner_Profile
    has_learner_profile = Learner_Profile.objects.filter(user=request.user).exists()
    
    # Get user's Google profile picture if available
    user_profile_picture = None
    try:
        from allauth.socialaccount.models import SocialAccount
        social_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
        if social_account and social_account.extra_data:
            user_profile_picture = social_account.extra_data.get('picture')
    except Exception as e:
        # If there's any error, just use the default
        pass
    
    # Render the Programs_user page with the programs data
    response = render(request, 'Programs_user.html', {
        'Programss': programs,
        'has_learner_profile': has_learner_profile,
        'user_profile_picture': user_profile_picture
    })
    
    # Prevent caching (this will ensure the page is not cached in the browser)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response

def Prog_Info(request, id):
    # Retrieve the program by its ID
    program = get_object_or_404(Programs, id=id)
    # Render the template with the program data
    return render(request, 'Program Information.html', {'program': program})

def Prog_Info_user(request, id):
    # Retrieve the program by its ID
    program = get_object_or_404(Programs, id=id)
    
    # Check if user has reached the application limit
    has_reached_limit = False
    has_learner_profile = False
    
    if request.user.is_authenticated:
        # Get total applications (both pending and approved)
        total_applications = ProgramApplication.objects.filter(applicant=request.user).count()
        total_approved = ApprovedApplicant.objects.filter(applicant=request.user).count()
        has_reached_limit = (total_applications + total_approved) >= 2
        
        # Check if user has a Learner_Profile
        has_learner_profile = Learner_Profile.objects.filter(user=request.user).exists()
    
    # Check enrollment status
    from .enrollment_validation import get_enrollment_info
    enrollment_info = get_enrollment_info()
    
    # Get user's Google profile picture if available
    user_profile_picture = None
    if request.user.is_authenticated:
        try:
            from allauth.socialaccount.models import SocialAccount
            social_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
            if social_account and social_account.extra_data:
                user_profile_picture = social_account.extra_data.get('picture')
        except Exception as e:
            # If there's any error, just use the default
            pass
    
    # Render the template with the program data and limit status
    return render(request, 'Program Information_user.html', {
        'program': program,
        'has_reached_limit': has_reached_limit,
        'has_learner_profile': has_learner_profile,
        'enrollment_info': enrollment_info,
        'user_profile_picture': user_profile_picture
    })   

def Contact(request):
  template = loader.get_template('Contact.html')
  return HttpResponse(template.render())

@never_cache
def Contact_user(request):
    # Check if the user is authenticated, if not redirect to login
    if not request.user.is_authenticated:
        return redirect('Login')  # Redirect to login page if user is not logged in

    # Retrieve all programs if the user is authenticated
    programs = Programs.objects.all()
    
    # Render the Contact_user page with the programs data
    response = render(request, 'Contact_user.html', {'Programss': programs})
    
    # Prevent caching (this will ensure the page is not cached in the browser)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response

def Register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("Register")

        # Check if username already exists
        if Applicant.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different username.")
            return redirect("Register")

        # Check if email already exists
        if Applicant.objects.filter(email=email).exists():
            messages.error(request, "Email already exists. Please use a different email.")
            return redirect("Register")

        # Create and save the user
        applicant = Applicant(username=username, email=email, password=make_password(password))
        applicant.save()

        messages.success(request, "Account created successfully! You can now log in.")
        return redirect("Login")

    return render(request, "Register.html")


def Login_Nextpage(request):
    username = request.session.get("username", "Guest")  # Get username from session
    return render(request, "Dashboard.html", {"username": username})

#Example
def Option(request):
  template = loader.get_template('OptionRegister.html')
  return HttpResponse(template.render())


def Employer_signup(request):
  template = loader.get_template('employer-signup.html')
  return HttpResponse(template.render())

def Employer_login(request):
  template = loader.get_template('employer-login.html')
  return HttpResponse(template.render())

def Employer_Dashboard(request):
  template = loader.get_template('Dashboard_employer.html')
  return HttpResponse(template.render())

def Login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            request.session["username"] = user.username

            messages.success(request, "Welcome to Online DLL LMSTC")

            # Redirect based on user role
            if user.is_superuser:
                return redirect("Dashboard_admin")
            elif user.is_staff:
                return redirect("Dashboard_trainor")
            else:
                # ✅ Check if user is an approved applicant
                is_approved = ApprovedApplicant.objects.filter(applicant=user).exists()

                if is_approved:
                    return redirect("Dashboard")
                else:
                    return redirect("Homepage_user")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("Login")

    return render(request, "Login.html")


@login_required
def custom_redirect_view(request):
    user = request.user

    if user.is_superuser:
        return redirect("Dashboard_admin")
    elif user.is_staff:
        return redirect("Dashboard_trainor")
    else:
        has_applied = ProgramApplication.objects.filter(applicant=user).exists()
        if has_applied:
            return redirect("Dashboard")
        else:
            return redirect("Homepage_user")


from django.shortcuts import render, redirect
from .models import Learner_Profile, ProgramApplication, ApprovedApplicant, JobPost, Programs
from .models import Training 

def Dashboard(request):
    if not request.user.is_authenticated:
        return redirect('Login')

    if request.user.is_superuser or request.user.is_staff:
        return redirect('Dashboard_admin')

    username = request.user.username

    # ✅ Check if Learner_Profile exists for this user
    try:
        profile = Learner_Profile.objects.get(user=request.user)
    except Learner_Profile.DoesNotExist:
        return redirect('learner_profile')  # Replace with your actual form URL name

    # ✅ Get all applications and approved programs
    applications = ProgramApplication.objects.filter(applicant=request.user).select_related('program')
    approved_programs = ApprovedApplicant.objects.filter(applicant=request.user).select_related('program')

    # ✅ Get approved program IDs
    approved_program_ids = set(
        approved_programs.values_list('program_id', flat=True)
    )

    # ✅ Can apply if fewer than 2 programs approved
    can_apply = len(approved_program_ids) < 2

    # ✅ Check if user is a passer (has completed any program) - MOVED HERE
    is_passer = ApplicantPasser.objects.filter(applicant=request.user).exists()

    # ✅ Skill Matching: Filter JobPost by matching job_opportunities from completed programs
    jobss = []
    if is_passer:
        # Get all programs the user has passed
        passed_programs = ApplicantPasser.objects.filter(applicant=request.user).select_related('program')
        
        # Collect all job opportunities from passed programs
        user_job_opportunities = set()
        for passer in passed_programs:
            if passer.program.program_competencies:
                job_opps = passer.program.program_competencies.get('job_opportunities', [])
                user_job_opportunities.update([job.lower().strip() for job in job_opps])
        
        # Get all active job posts
        all_jobs = JobPost.objects.filter(status='Active')
        
        # Match jobs where skills overlap with user's job opportunities
        for job in all_jobs:
            if job.skills and isinstance(job.skills, list):
                job_skills = set([skill.lower().strip() for skill in job.skills])
                # Check if any job skill matches user's job opportunities
                if user_job_opportunities.intersection(job_skills):
                    jobss.append(job)
    else:
        # For non-passers, use the old logic (filter by approved programs)
        jobss = JobPost.objects.filter(program_id__in=approved_program_ids, status='Active')

    programs = Programs.objects.all()
    approved_count = applications.filter(status='approved').count()
    total_programs = applications.count() + approved_programs.count()
    total_apps = len(applications) + len(approved_programs)
    pending_count = applications.filter(status="Pending").count()

    # ✅ Check if user has reached maximum limit (2 programs total including pending)
    has_reached_limit = total_programs >= 2

    # Add notification count to context
    unread_count = get_unread_notifications(request.user).count() if request.user.is_authenticated else 0

    show_modal = request.session.pop('show_application_modal', False)
    applied_program = request.session.pop('applied_program_name', '')

    # 🔥 DON'T POP SESSION VARIABLES YET - Keep them for the template
    show_modal = request.session.get('show_application_modal', False)
    applied_program_name = request.session.get('applied_program_name', '')

    # Get all classifications, disability types, and disability causes for the edit form
    all_classifications = ClientClassification.objects.all()
    all_disability_types = DisabilityType.objects.all()
    all_disability_causes = DisabilityCause.objects.all()
    
    trainings = Training.objects.all()
    
    # Get competencies data from approved programs
    program_competencies = {
        'basic': [],
        'common': [],
        'core': []
    }
    
    # Get competencies from the first approved program (if any)
    if approved_programs.exists():
        first_approved_program = approved_programs.first()
        if first_approved_program.program.program_competencies:
            competencies_data = first_approved_program.program.program_competencies
            program_competencies['basic'] = competencies_data.get('basic', [])
            program_competencies['common'] = competencies_data.get('common', [])
            program_competencies['core'] = competencies_data.get('core', [])
    
    # Get competencies progress from ApplicantCompetencies model
    from .models import ApplicantCompetencies
    competencies_progress = ApplicantCompetencies.objects.filter(
        applicant=request.user,
        program__in=[ap.program for ap in approved_programs]
    ).first()
    
    # Get user's support tickets
    from .models import SupportTicket
    user_tickets = SupportTicket.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    
    # Get marked fields from applications that need correction
    marked_fields = {}
    review_notes = None
    for app in applications:
        if app.is_under_review and app.marked_fields:
            marked_fields = app.marked_fields
            review_notes = app.review_notes
            break  # Get the first one that needs review
    
    # Get current batch cycle information
    from datetime import datetime
    from .models import BatchCycle, ActiveSemesterSettings
    batch_cycle = BatchCycle.get_active_cycle()
    current_batch = batch_cycle.current_batch
    current_year = datetime.now().year
    
    # Get the trainor's current active semester (not the enrollment semester)
    # This ensures students see what semester the trainor has currently set
    current_semester = batch_cycle.current_semester  # Default fallback
    if approved_programs.exists():
        first_approved = approved_programs.first()
        # Get the trainor's current active semester
        if first_approved.program and first_approved.program.program_trainor:
            try:
                trainer_user = Applicant.objects.filter(
                    username=first_approved.program.program_trainor,
                    is_staff=True
                ).first()
                
                if trainer_user:
                    semester_settings = ActiveSemesterSettings.get_or_create_for_trainer(trainer_user)
                    current_semester = semester_settings.active_semester
            except Exception as e:
                pass
    
    # Set default percentages
    basic_percentage = 0
    common_percentage = 0
    core_percentage = 0
    overall_percentage = 0
    
    if competencies_progress:
        basic_percentage = float(competencies_progress.basic_percentage)
        common_percentage = float(competencies_progress.common_percentage)
        core_percentage = float(competencies_progress.core_percentage)
        overall_percentage = float(competencies_progress.overall_percentage)
    
    # Get user's Google profile picture if available
    user_profile_picture = None
    try:
        from allauth.socialaccount.models import SocialAccount
        social_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
        if social_account and social_account.extra_data:
            user_profile_picture = social_account.extra_data.get('picture')
    except Exception as e:
        # If there's any error, just use the default
        pass
    
    # Get program info and trainer name for certification
    program_info = None
    trainer_name = None
    if approved_programs.exists():
        # Get the first approved program for certificate display
        first_approved = approved_programs.first()
        program_info = first_approved.program
        trainer_name = first_approved.program.program_trainor if first_approved.program else None
    
    context = {
        "user_profile_picture": user_profile_picture,
        "username": username,
        "applications": applications,
        "approved_program_ids": approved_program_ids,
        "approved_count": approved_count,
        "profile": profile,
        "jobss": jobss,  # ✅ Updated jobss list
        "Programss": programs,
        "can_apply": can_apply,
        "approveprog": approved_programs,  # ✅ Cleaned duplicate
        "total_programs": total_programs,
        "total_apps": total_apps,
        "pending_count": pending_count,
        "has_reached_limit": has_reached_limit,  # ✅ New context variable
        "is_passer": is_passer,  # ✅ Check if user has passed any program
        "trainings": trainings,
        'unread_notifications_count': unread_count,
        'show_modal': show_modal,
        'applied_program': applied_program,
        'applied_program_name': request.session.get('applied_program_name', ''),
        # 'applied_program_name': applied_program_name,  # 🔥 Use this variable name
        
        # Data for edit profile form
        'all_classifications': all_classifications,
        'all_disability_types': all_disability_types,
        'all_disability_causes': all_disability_causes,
        
        # Competencies data
        'program_competencies': program_competencies,
        'basic_percentage': basic_percentage,
        'common_percentage': common_percentage,
        'core_percentage': core_percentage,
        'overall_percentage': overall_percentage,
        'user_tickets': user_tickets,  # Support tickets
        
        # Field review information
        'marked_fields': marked_fields,  # Fields marked as incorrect by admin
        'review_notes': review_notes,  # Admin notes about corrections needed
        
        # Batch cycle information
        'current_batch': current_batch,
        'current_semester': current_semester,
        'current_year': current_year,
        
        # Certification data
        'program_info': program_info,  # Approved program for certificate
        'trainer_name': trainer_name,  # Trainer name for certificate
    }

    # Disable caching
    response = render(request, 'Dashboard.html', context)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Programs, TrainerProfile, ApprovedApplicant

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Programs, TrainerProfile
from Applicant.models import Applicant  # Import your custom user model directly



# @login_required
#     trainings = Training.objects.filter(trainer=request.user)
    
#     # FIXED: Calculate attendance summary for each student
#     for applicant in approved_applicants:
#         # Count present attendance - using the correct field reference
#         total_present = Attendance.objects.filter(
#             student=applicant.applicant,  # This should match the User instance
#             training__trainer=request.user,
#             status='present'
#         ).count()
        
#         # Count absent attendance
#         total_absent = Attendance.objects.filter(
#             student=applicant.applicant,
#             training__trainer=request.user,
#             status='missed'
#         ).count()
        
#         # Calculate total sessions
#         total_sessions = trainings.count()
        
#         # Add these as attributes to the applicant object
#         applicant.total_present = total_present
#         applicant.total_absent = total_absent
#         applicant.total_sessions = total_sessions
        
#         # Debug print to check values
#         print(f"Student: {applicant.applicant.username}")
#         print(f"Present: {total_present}, Absent: {total_absent}, Total Sessions: {total_sessions}")
    
#     if request.method == "POST":
#         # ... rest of your POST handling code remains the same
#         pass
    
#     # GET request - show the form
#     context = {
#         'Programss': programs,
#         'trainer_profile': trainer_profile,
#         'trainer_profiles': trainer_profiles,
#         'approvedapplicant': approved_applicants,
#         'trainings': trainings,  # Add trainings to context
#     }
#     return render(request, "Dashboard_trainor.html", context)

@login_required
def Dashboard_trainor(request):
    # Get all programs for the form dropdown
    programs = Programs.objects.all()
    
    # Get the current user's trainer profile (if it exists)
    trainer_profile = None
    approved_applicants = []
    trainer_programs = []  # All programs assigned to this trainer
    selected_program = None  # Currently selected program
    
    if request.user.is_authenticated:
        try:
            trainer_profile = TrainerProfile.objects.prefetch_related('programs').get(user=request.user)
            # Get all programs assigned to this trainer
            trainer_programs = trainer_profile.programs.all()
            
            # Check for program change request from GET parameter
            change_program_id = request.GET.get('change_program')
            if change_program_id:
                # Verify the program belongs to this trainer
                if trainer_programs.filter(id=change_program_id).exists():
                    request.session['selected_program_id'] = int(change_program_id)
            
            # Get selected program from session or default to first
            selected_program_id = request.session.get('selected_program_id')
            if selected_program_id:
                selected_program = trainer_programs.filter(id=selected_program_id).first()
            
            # If no valid selection, default to first program
            if not selected_program and trainer_programs.exists():
                selected_program = trainer_programs.first()
                request.session['selected_program_id'] = selected_program.id
            
            # Get approved applicants for the selected program only
            if selected_program:
                approved_applicants = ApprovedApplicant.objects.filter(
                    program=selected_program
                ).select_related('applicant', 'program').order_by('-approved_at')
        except TrainerProfile.DoesNotExist:
            trainer_profile = None

    # Get all trainer profiles for display (if needed for admin purposes)
    trainer_profiles = TrainerProfile.objects.select_related('user', 'program').all()
    
    # ✅ GET ALL TRAININGS (from all trainers) - This is what the calendar needs
    all_trainings = Training.objects.select_related('trainer').all().order_by('start_date')
    
    # ✅ GET ONLY CURRENT TRAINER'S TRAININGS
    my_trainings = Training.objects.filter(trainer=request.user).order_by('start_date')
    
    # ✅ GET ALL TRAINERS for the filter dropdown
    all_trainers = Applicant.objects.filter(is_staff=True, trainerprofile__isnull=False).distinct()

    # ✅ GET APPLICANT PASSERS
    applicant_passers = ApplicantPasser.objects.all().order_by('-completion_date')

    # Calculate attendance summary for each student
    for applicant in approved_applicants:
        total_present = Attendance.objects.filter(
            student=applicant.applicant,
            training__trainer=request.user,
            status='present'
        ).count()
        
        total_absent = Attendance.objects.filter(
            student=applicant.applicant,
            training__trainer=request.user,
            status='missed'
        ).count()
        
        total_sessions = my_trainings.count()
        
        applicant.total_present = total_present
        applicant.total_absent = total_absent
        applicant.total_sessions = total_sessions

    # ✅ HANDLES TRAINER REGISTRATION FORM
    if request.method == "POST":
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        program_ids = request.POST.getlist('expertise')  # Support multiple selections
        
        if not all([fullname, email, password]):
            messages.error(request, "All fields are required.")
            return redirect('Dashboard_admin')
        
        if not program_ids:
            messages.error(request, "At least one program must be selected.")
            return redirect('Dashboard_admin')
        
        if Applicant.objects.filter(email=email).exists():
            messages.error(request, "A user with that email already exists.")
            return redirect('Dashboard_admin')

        # Create a unique username based on the email
        username = email.split('@')[0]
        base_username = username
        counter = 1
        while Applicant.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Create the Applicant account
        user = Applicant.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=fullname,  # You can split into first/last if desired
            is_staff=True  # make this user a staff member
        )

        # Create the TrainerProfile and assign multiple programs
        trainer_profile = TrainerProfile.objects.create(user=user)
        for program_id in program_ids:
            program = Programs.objects.get(id=program_id)
            trainer_profile.programs.add(program)
        
        # Also set the first program as the legacy program field for backward compatibility
        if program_ids:
            trainer_profile.program = Programs.objects.get(id=program_ids[0])
            trainer_profile.save()

        messages.success(request, f"Trainer {fullname} registered successfully with {len(program_ids)} program(s).")
        return redirect('Dashboard_admin')

    # Get or create active semester settings for the trainer
    from .models import ActiveSemesterSettings, BatchCycle
    semester_settings = ActiveSemesterSettings.get_or_create_for_trainer(request.user)
    
    # Get the active batch cycle (managed by admin via Event model)
    batch_cycle = BatchCycle.get_active_cycle()
    
    # Get display text for semester
    semester_display_map = {
        '1': '1st Sem',
        '2': '2nd Sem',
        '3': '3rd Sem'
    }
    
    # Batch display text
    batch_display_map = {
        '1': 'Batch 1',
        '2': 'Batch 2',
        '3': 'Batch 3'
    }
    
    # Generate year range from 2023 to current year
    from datetime import datetime
    current_year = datetime.now().year
    year_range = range(2023, current_year + 1)
    
    # Get user's Google profile picture if available
    user_profile_picture = None
    try:
        from allauth.socialaccount.models import SocialAccount
        social_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
        if social_account and social_account.extra_data:
            user_profile_picture = social_account.extra_data.get('picture')
    except Exception as e:
        # If there's any error, just use the default
        pass
    
    # GET request - show the form and data
    context = {
        'user_profile_picture': user_profile_picture,
        'Programss': programs,
        'trainer_profile': trainer_profile,
        'trainer_profiles': trainer_profiles,
        'approvedapplicant': approved_applicants,
        'trainings': my_trainings,  # Keep this for backward compatibility
        # ✅ ADD THESE FOR THE CALENDAR
        'all_trainings': all_trainings,  # All training sessions from all trainers
        'my_trainings': my_trainings,    # Current trainer's sessions only
        'all_trainers': all_trainers,    # All trainers for the filter dropdown
        'applicant_passers': applicant_passers,  # Passed applicants data
        # ✅ ADD MULTIPLE PROGRAMS SUPPORT
        'trainer_programs': trainer_programs,  # All programs assigned to this trainer
        'selected_program': selected_program,  # Currently selected program
        'trainer_program': selected_program,  # For backward compatibility with competencies
        # ✅ ADD ACTIVE BATCH (from BatchCycle - admin controlled via Event model)
        'active_batch': batch_cycle.current_batch,
        'active_batch_display': batch_display_map.get(batch_cycle.current_batch, 'Batch 1'),
        'batch_cycle_state': batch_cycle.cycle_state,
        # ✅ ADD ACTIVE SEMESTER SETTINGS (trainer can manage)
        'active_semester': semester_settings.active_semester,
        'active_semester_display': semester_display_map.get(semester_settings.active_semester, '1st Sem'),
        # ✅ ADD BATCH CYCLE INFO
        'batch_cycle': batch_cycle,
        # ✅ ADD YEAR RANGE FOR REPORTS DROPDOWN
        'year_range': year_range,
        'programs': programs,  # For Reports section filters
    }
    
    return render(request, "Dashboard_trainor.html", context)


@csrf_exempt
@login_required
def save_semester_settings(request):
    """Save active semester settings for trainer (batch is managed by admin via Event model)"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            semester = data.get('semester', '1')
            
            # Validate semester input
            if semester not in ['1', '2', '3']:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid semester value'
                })
            
            # Get or create settings for the trainer
            from .models import ActiveSemesterSettings, BatchCycle
            settings, created = ActiveSemesterSettings.objects.get_or_create(
                trainer=request.user,
                defaults={'active_semester': semester}
            )
            
            # Update if already exists (only semester, batch comes from BatchCycle)
            if not created:
                settings.active_semester = semester
                settings.semester_status = 'ongoing'  # Reset status when changing semester
                settings.save()
            
            # Get current batch from BatchCycle (admin controlled)
            batch_cycle = BatchCycle.get_active_cycle()
            
            return JsonResponse({
                'success': True,
                'message': 'Semester settings saved successfully',
                'semester': semester,
                'active_batch': batch_cycle.current_batch  # Return current batch for display
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
@login_required
def end_semester(request):
    """Handle End Semester action from trainor - mark current semester as completed"""
    if request.method == 'POST':
        try:
            from .models import ActiveSemesterSettings, BatchCycle
            
            # Get the trainer's semester settings
            settings = ActiveSemesterSettings.get_or_create_for_trainer(request.user)
            
            # Check if currently on 3rd semester
            if settings.active_semester != '3':
                return JsonResponse({
                    'success': False,
                    'error': 'Can only end semester when on 3rd semester'
                })
            
            # Mark the semester as completed
            settings.complete_semester()
            
            return JsonResponse({
                'success': True,
                'message': 'Semester ended successfully. Marked as complete.',
                'completed_semester': settings.completed_semester,
                'remark': settings.get_remark()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
@login_required
def end_batch(request):
    """Handle End Batch action from admin - progress to next batch cycle when all programs are complete"""
    if request.method == 'POST':
        try:
            from .models import ActiveSemesterSettings, BatchCycle, Programs, TrainerProfile
            
            # Check if user is admin
            if not request.user.is_superuser:
                return JsonResponse({
                    'success': False,
                    'error': 'Only admin can end the batch'
                })
            
            # Get all programs and check if all are completed
            programs = Programs.objects.all()
            all_complete = True
            incomplete_programs = []
            
            for program in programs:
                # Get trainer for this program
                trainer_profile = TrainerProfile.objects.filter(program=program).first()
                if trainer_profile:
                    # Get semester settings for the trainer
                    semester_settings = ActiveSemesterSettings.get_or_create_for_trainer(trainer_profile.user)
                    
                    # Check if semester is completed
                    if semester_settings.semester_status != 'completed':
                        all_complete = False
                        incomplete_programs.append(program.program_name)
            
            # If not all programs are complete, return error
            if not all_complete:
                return JsonResponse({
                    'success': False,
                    'error': f'Cannot end batch. The following programs have not completed their semester: {", ".join(incomplete_programs)}'
                })
            
            # Get batch cycle and progress to next batch
            batch_cycle = BatchCycle.get_active_cycle()
            batch_cycle.progress_to_next_batch()
            
            # Reset all trainer semester settings for the next batch cycle
            for program in programs:
                trainer_profile = TrainerProfile.objects.filter(program=program).first()
                if trainer_profile:
                    semester_settings = ActiveSemesterSettings.get_or_create_for_trainer(trainer_profile.user)
                    semester_settings.active_semester = '1'
                    semester_settings.semester_status = 'ongoing'
                    semester_settings.completed_semester = None
                    semester_settings.completed_at = None
                    semester_settings.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Batch ended successfully! Progressed to Batch {batch_cycle.current_batch}. All programs reset to 1st semester.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@require_GET
def get_applicant_datas(request, applicant_id):
    try:
        # Get the applicant
        applicant = Applicant.objects.get(id=applicant_id)
        
        # Get the applicant's profile
        try:
            profile = ApplicantProfile.objects.get(applicant=applicant)
            
            # Build response data
            data = {
                'id': applicant.id,
                'username': applicant.username,
                'email': applicant.email,
                'first_name': applicant.first_name,
                'last_name': applicant.last_name,
                
                # Profile data
                'entry_date': profile.entry_date.strftime('%Y-%m-%d') if profile.entry_date else None,
                'middle_name': profile.middle_name,
                'region_name': profile.region_name,
                'province_name': profile.province_name,
                'city_name': profile.city_name,
                'barangay_name': profile.barangay_name,
                'district': profile.district,
                'street': profile.street,
                'contact_number': profile.contact_number,
                'nationality': profile.nationality,
                'sex': profile.sex,
                'civil_status': profile.civil_status,
                'employment_status': profile.employment_status,
                'monthly_income': profile.monthly_income,
                'date_hired': profile.date_hired.strftime('%Y-%m-%d') if profile.date_hired else None,
                'company_name': profile.company_name,
                'birthdate': profile.birthdate.strftime('%Y-%m-%d') if profile.birthdate else None,
                'age': profile.age,
                'birthplace_regionb_name': profile.birthplace_regionb_name,
                'birthplace_provinceb_name': profile.birthplace_provinceb_name,
                'birthplace_cityb_name': profile.birthplace_cityb_name,
                'educational_attainment': profile.educational_attainment,
                'parent_guardian': profile.parent_guardian,
                'permanent_address': profile.permanent_address,
                'course_or_qualification': profile.course_or_qualification,
                'applicant_name': profile.applicant_name,
                'date_accomplished': profile.date_accomplished.strftime('%Y-%m-%d') if profile.date_accomplished else None,
                
                # Handle profile picture
                'id_picture': profile.id_picture.url if profile.id_picture else None,
                
                # Handle classifications (assuming ManyToMany relationship)
                'classifications': [
                    {'id': c.id, 'name': c.name} 
                    for c in profile.classifications.all()
                ] if hasattr(profile, 'classifications') else [],
                
                # Handle disability type (assuming ForeignKey relationship)
                'disability_type': {
                    'id': profile.dtype.id,
                    'name': profile.dtype.name
                } if profile.dtype else None,
                
                # Handle disability causes (assuming ManyToMany relationship)
                'disability_causes': [
                    {'id': c.id, 'name': c.name} 
                    for c in profile.disability_causes.all()
                ] if hasattr(profile, 'disability_causes') else [],
            }
            
            return JsonResponse(data)
            
        except ApplicantProfile.DoesNotExist:
            return JsonResponse({
                'id': applicant.id,
                'username': applicant.username,
                'email': applicant.email,
                'first_name': applicant.first_name,
                'last_name': applicant.last_name,
                'error': 'No profile found for this applicant'
            })
            
    except Applicant.DoesNotExist:
        return JsonResponse({'error': 'Applicant not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


from .models import Programs 
from datetime import timedelta
from django.utils import timezone



from .models import ClientClassification
from django.contrib.admin.views.decorators import staff_member_required
from collections import defaultdict

@never_cache
def Dashboard_admin(request, application_id=None):
    if not request.user.is_authenticated:
        return redirect('Login')
    
    
    messages.info(request, "Welcome to Admin Dashboard")

    username = request.user.username
    programs = Programs.objects.all()
    counted_program = Programs.objects.all().count()
    
    # Get current batch cycle first
    batch_cycle = BatchCycle.objects.filter(is_active=True).first()
    if not batch_cycle:
        batch_cycle = BatchCycle.objects.create(
            current_batch='1',
            cycle_state='waiting_enrollment',
            is_active=True
        )
    
    # Filter counts by current batch cycle
    current_batch = batch_cycle.current_batch
    
    # Count applicants in current batch (approved applicants + approved walk-ins)
    counted_applicant = (
        ApprovedApplicant.objects.filter(batch_number=current_batch).values('applicant').distinct().count() +
        ApprovedWalkIn.objects.filter(batch_number=current_batch).values('applicant').distinct().count()
    )
    
    # Count approved applicants in current batch (status='active')
    counted_approved = (
        ApprovedApplicant.objects.filter(batch_number=current_batch, status='active').values('applicant').distinct().count() +
        ApprovedWalkIn.objects.filter(batch_number=current_batch, status='active').values('applicant').distinct().count()
    )
    
    # Count dropouts in current batch (status='dropped')
    counted_dropped = (
        ApprovedApplicant.objects.filter(batch_number=current_batch, status='dropped').values('applicant').distinct().count() +
        ApprovedWalkIn.objects.filter(batch_number=current_batch, status='dropped').values('applicant').distinct().count()
    )
    
    # Walk-in application counts (these remain global as they're pending applications)
    counted_walkin_pending = WalkInApplication.objects.filter(status='Pending').count()
    counted_walkin_approved = ApprovedWalkIn.objects.filter(batch_number=current_batch).values('applicant').distinct().count()
    counted_walkin_total = WalkInApplication.objects.values('applicant__username').distinct().count()

    # programs = Programs.objects.annotate(applied_count=Count('applications'))


    # programs = Programs.objects.annotate(
    #     approved_count=Count('approved_applicants'),
    #     applied_count=Count('applications')
    # )
    # Filter program statistics by current batch
    combined_programs = []
    for p in programs:
        # Count applicants in current batch for this program
        batch_applicants = (
            ApprovedApplicant.objects.filter(program=p, batch_number=current_batch).count() +
            ApprovedWalkIn.objects.filter(program=p, batch_number=current_batch).count()
        )
        
        # Count approved (active) applicants in current batch for this program
        batch_approved = (
            ApprovedApplicant.objects.filter(program=p, batch_number=current_batch, status='active').count() +
            ApprovedWalkIn.objects.filter(program=p, batch_number=current_batch, status='active').count()
        )
        
        # Count finished applicants in current batch for this program
        batch_passed = (
            ApprovedApplicant.objects.filter(program=p, batch_number=current_batch, status='finished').count() +
            ApprovedWalkIn.objects.filter(program=p, batch_number=current_batch, status='finished').count()
        )
        
        combined_programs.append({
            'program_name': p.program_name,
            'applied_count': batch_applicants,  # Total in current batch
            'approved_count': batch_approved,   # Active in current batch
            'passed_count': batch_passed,       # Finished in current batch
        })

    applicant = ProgramApplication.objects.all().order_by('applied_at')
    jobs = JobPost.objects.all()
    profiles = Learner_Profile.objects.all()
    classic = ClientClassification.objects.all()
    ProgAPP = ProgramApplication.objects.all()



    paginator = Paginator(applicant, 5)  # Show 10 applications per page
    page_number = request.GET.get('page') or 1
    page_obj = paginator.get_page(page_number)

    now = timezone.now()


    # === Handle form submission with skills ===
    if request.method == "POST":
        job_id = request.POST.get("job_id")  # adjust this based on your form
        skills = request.POST.getlist('skills')
        print("Submitted skills:", skills)

        try:
            job = JobPost.objects.get(id=job_id)
            job.skills = ",".join(skills)  # store skills as comma-separated string
            job.save()
        except JobPost.DoesNotExist:
            print(f"JobPost with id {job_id} not found.")

    # === Job filtering logic ===
    active_jobs = []
    duration_map = {
        '1 Week': timedelta(weeks=1),
        '2 Weeks': timedelta(weeks=2),
        '1 Month': timedelta(days=30),
        '2 Months': timedelta(days=60),
        '3 Months': timedelta(days=90),
    }

    all_jobs = JobPost.objects.all()
    for job in all_jobs:
        availability_duration = duration_map.get(job.availability)
        if availability_duration and job.status == 'Active':
            if job.posted_at + availability_duration > now:
                active_jobs.append(job)

    # Get all applications for the applicant list (not paginated)
    applications = ProgramApplication.objects.select_related('applicant', 'program').order_by('-applied_at')
    
    # Get walk-in applications separately
    walkin_applications = WalkInApplication.objects.select_related('applicant', 'program').order_by('-applied_at')
    
    # Filter approved applicants by current batch
    approved_applicants = ApprovedApplicant.objects.filter(
        batch_number=current_batch
    ).select_related('applicant', 'program').order_by('-approved_at')
    
    approved_walkins = ApprovedWalkIn.objects.filter(
        batch_number=current_batch
    ).select_related('applicant', 'program').order_by('-approved_at')

    # Group approved applicants by program ID
    program_approvals = defaultdict(list)
    for entry in approved_applicants:
        program_approvals[entry.program.id].append(entry)

    # Attach profile to each application
    for app in applications:
        try:
            app.profile = Learner_Profile.objects.get(user=app.applicant)
        except Learner_Profile.DoesNotExist:
            app.profile = None

    # Attach profile to each walk-in application
    for app in walkin_applications:
        try:
            app.profile = Learner_Profile.objects.get(user=app.applicant)
        except Learner_Profile.DoesNotExist:
            app.profile = None

    for app in approved_applicants:
        try:
            app.profile = Learner_Profile.objects.get(user=app.applicant)
        except Learner_Profile.DoesNotExist:
            app.profile = None

    for app in approved_walkins:
        try:
            app.profile = Learner_Profile.objects.get(user=app.applicant)
        except Learner_Profile.DoesNotExist:
            app.profile = None
            
    archived_jobs = JobPost.objects.filter(status='Inactive')

    if application_id:
        ProgAPP = get_object_or_404(ProgramApplication, id=application_id)
    else:
        ProgAPP = ProgramApplication.objects.last() 

    # counted_programs = Programs.objects.annotate(applicant_count=Count('applications'))

    trainers = TrainerProfile.objects.select_related('user', 'program').all()

    # Context data for walk-in modal
    classifications = ClientClassification.objects.all()
    disability_types = DisabilityType.objects.all()
    disability_causes = DisabilityCause.objects.all()
    
    # Query all events from the database
    events = Event.objects.all().order_by('-start_date')
    
    # Get LMSTC Documents for Document Search (Applicant Profiles)
    from .models import LMSTC_Documents
    lmstc_documents = LMSTC_Documents.objects.filter(
        document_type='applicant_profile'
    ).select_related('applicant', 'program', 'uploaded_by', 'learner_profile').order_by('-uploaded_at')
    
    # Get all Learner_Profiles for Document Search
    # This will display all applicant profiles in the Document Search table
    all_learner_profiles = Learner_Profile.objects.select_related('user').all().order_by('-entry_date')
    
    # Document Management counts
    total_documents_count = LMSTC_Documents.objects.count()
    approved_learners_count = Learner_Profile.objects.filter(user__approved_programs__isnull=False).distinct().count()
    pending_learners_count = Learner_Profile.objects.filter(user__program_applications__status='Pending').distinct().count()
    
    # Support Ticket data
    all_tickets = SupportTicket.objects.select_related('created_by', 'assigned_to').order_by('-created_at')
    total_tickets_count = all_tickets.count()
    open_tickets_count = all_tickets.filter(status='open').count()
    resolved_tickets_count = all_tickets.filter(status='resolved').count()
    high_priority_tickets_count = all_tickets.filter(priority='high').count()
    
    # Get program monitoring data with trainer semester information
    from .models import ActiveSemesterSettings
    
    program_monitoring = []
    batch_cycle = BatchCycle.get_active_cycle()
    
    # Get all batch cycles for Document Search dropdown
    batch_cycles = BatchCycle.objects.all()
    
    # Generate years range for Applicant Profiles filter (dynamic based on actual data)
    from datetime import datetime
    current_year = datetime.now().year
    # Get the earliest entry date from learner profiles
    earliest_profile = Learner_Profile.objects.order_by('entry_date').first()
    if earliest_profile and earliest_profile.entry_date:
        start_year = earliest_profile.entry_date.year
    else:
        start_year = current_year - 5  # Default to 5 years ago if no data
    years_range = range(start_year, current_year + 2)  # From earliest to next year
    
    # Check if all programs are complete
    all_programs_complete = True
    programs_with_trainers = 0
    
    for program in programs:
        # Get the trainer for this program
        trainer_profile = TrainerProfile.objects.filter(program=program).first()
        
        if trainer_profile:
            programs_with_trainers += 1
            # Get semester settings for the trainer
            semester_settings = ActiveSemesterSettings.get_or_create_for_trainer(trainer_profile.user)
            
            # Check if this program is completed
            if semester_settings.semester_status != 'completed':
                all_programs_complete = False
            
            program_monitoring.append({
                'program_name': program.program_name,
                'program_id': program.id,
                'batch': batch_cycle.current_batch,
                'semester': semester_settings.active_semester,
                'semester_display': dict(ActiveSemesterSettings.SEMESTER_CHOICES).get(semester_settings.active_semester, '1st Semester'),
                'remark': semester_settings.get_remark(),
                'trainer_name': trainer_profile.user.get_full_name() or trainer_profile.user.username,
                'semester_status': semester_settings.semester_status,
            })
        else:
            # Program without assigned trainer - not counted as complete
            all_programs_complete = False
            program_monitoring.append({
                'program_name': program.program_name,
                'program_id': program.id,
                'batch': batch_cycle.current_batch,
                'semester': '1',
                'semester_display': '1st Semester',
                'remark': 'No Trainer Assigned',
                'trainer_name': 'N/A',
                'semester_status': 'ongoing',
            })
    
    # Only show End Batch button if there are programs with trainers and all are complete
    can_end_batch = all_programs_complete and programs_with_trainers > 0

    # Get user's Google profile picture if available
    user_profile_picture = None
    try:
        from allauth.socialaccount.models import SocialAccount
        social_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
        if social_account and social_account.extra_data:
            user_profile_picture = social_account.extra_data.get('picture')
    except Exception as e:
        # If there's any error, just use the default
        pass
    
    context = {
        "Dashboard_username": username,
        "user_profile_picture": user_profile_picture,  # Add user's Google profile picture
        "Programss": programs,
        "jobss": active_jobs,
        "archived_jobs": archived_jobs,
        'counted_programs': counted_program,
        'counted_applicants': counted_applicant,
        'counted_dropped': counted_dropped,  # Add dropout count
        'applicants': applicant.order_by('applied_at'),
        'Jobss': jobs,
        'profile': profiles,
        'classic': classic,
        'applicants': applications,
        'walkin_applicants': walkin_applications,  # Add walk-in applications
        'approved_walkins': approved_walkins,
        'batch_cycle': batch_cycle,      # Add approved walk-ins
        'apply': page_obj,
        'ProgAPP': ProgAPP,
        'counted_approved': counted_approved,
        'counted_walkin_pending': counted_walkin_pending,
        'counted_walkin_approved': counted_walkin_approved,
        'counted_walkin_total': counted_walkin_total,
        # 'approve': approve,
        'approved_applicants': approved_applicants,
        'program_approvals': dict(program_approvals),  # 
        'combined_programs': combined_programs,
        'trainers': trainers,
        # Document search filter data
        'programs': programs,  # For program filter dropdown
        'trainors': trainers,  # For trainor filter dropdown
        # Walk-in modal context data
        'classifications': classifications,
        'disability_types': disability_types,
        'disability_causes': disability_causes,
        # Events data
        'events': events,
        # Program monitoring data
        'program_monitoring': program_monitoring,
        'current_batch': batch_cycle.current_batch,
        'can_end_batch': can_end_batch,  # Flag to show End Batch button
        # LMSTC Documents for Document Search
        'lmstc_documents': lmstc_documents,
        # All Learner Profiles for Document Search
        'all_learner_profiles': all_learner_profiles,
        # Document Management counts
        'total_documents_count': total_documents_count,
        'approved_learners_count': approved_learners_count,
        'pending_learners_count': pending_learners_count,
        # Support Ticket data
        'all_tickets': all_tickets,
        'total_tickets_count': total_tickets_count,
        'open_tickets_count': open_tickets_count,
        'resolved_tickets_count': resolved_tickets_count,
        'high_priority_tickets_count': high_priority_tickets_count,
        # Batch cycles for Document Search filter
        'batch_cycles': batch_cycles,
        # Years range for Applicant Profiles filter
        'years_range': years_range,

    }
    

    response = render(request, "Dashboard_admin.html", context)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = Applicant.objects.get(email=email)
            
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link
            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            
            # Email content
            subject = 'Password Reset Request - DLL LMSTC'
            message = f'''
Hello {user.first_name or user.username},

You have requested to reset your password for your DLL LMSTC account.

Click the link below to reset your password:
{reset_link}

This link will expire in 1 hour for security reasons.

If you did not request this password reset, please ignore this email.

Best regards,
DLL LMSTC Team
            '''
            
            # Send email
            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, f'Password reset link has been sent to {email}. Please check your inbox and spam folder.')
            except Exception as e:
                messages.error(request, 'Failed to send email. Please try again later or contact support.')
                
        except Applicant.DoesNotExist:
            # Don't reveal if email exists or not for security
            messages.success(request, f'If an account with email {email} exists, a password reset link has been sent.')
            
        return redirect('forgot_password')
    
    return render(request, 'forgot_password.html')

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Applicant.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Applicant.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'password_reset_confirm.html', {'validlink': True})
            
            if len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
                return render(request, 'password_reset_confirm.html', {'validlink': True})
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            messages.success(request, 'Your password has been reset successfully. You can now log in with your new password.')
            return redirect('Login')
        
        return render(request, 'password_reset_confirm.html', {'validlink': True})
    else:
        messages.error(request, 'The password reset link is invalid or has expired.')
        return render(request, 'password_reset_confirm.html', {'validlink': False})

def your_view(request):
    programs = Programs.objects.all()

    # Dictionary mapping each program ID to a list of approved applicants
    program_approvals = {
        program.id: ApprovedApplicant.objects.filter(program=program).select_related('applicant')
        for program in programs
    }

    return render(request, 'Dashboard_admin.html', {
        'Programss': programs,
        'program_approvals': program_approvals,
    })


def applicant_details_view(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    approved = get_object_or_404(ApprovedApplication, profile=profile)
    profile_instance = profile  # if needed for .classifications.all
    all_classifications = Classification.objects.all()

    context = {
        'profile': profile,
        'approved': approved,
        'profile_instance': profile_instance,
        'all_classifications': all_classifications,
    }
    return render(request, 'Dashboard_admin.html', context)


#newly added
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def get_profile_data(request, profile_id):
    """API endpoint to get profile data for modal"""
    if request.method == 'GET':
        try:
            profile = get_object_or_404(Learner_Profile, pk=profile_id)
            
            # Prepare profile data as dictionary
            profile_data = {
                'id': profile.pk,
                'last_name': getattr(profile, 'last_name', ''),
                'first_name': getattr(profile, 'first_name', ''),
                'middle_name': getattr(profile, 'middle_name', ''),
                'region': getattr(profile, 'region', ''),
                'region_name': getattr(profile, 'region_name', ''),
                'province': getattr(profile, 'province', ''),
                'province_name': getattr(profile, 'province_name', ''),
                'city': getattr(profile, 'city', ''),
                'city_name': getattr(profile, 'city_name', ''),
                'barangay': getattr(profile, 'barangay', ''),
                'barangay_name': getattr(profile, 'barangay_name', ''),
                'district': getattr(profile, 'district', ''),
                'street': getattr(profile, 'street', ''),
                'email': getattr(profile, 'email', ''),
                'contact_number': getattr(profile, 'contact_number', ''),
                'nationality': getattr(profile, 'nationality', ''),
                'sex': getattr(profile, 'sex', ''),
                'civil_status': getattr(profile, 'civil_status', ''),
                'employment_status': getattr(profile, 'employment_status', ''),
                'monthly_income': getattr(profile, 'monthly_income', ''),
                'date_hired': profile.date_hired.strftime('%Y-%m-%d') if getattr(profile, 'date_hired', None) else '',
                'company_name': getattr(profile, 'company_name', ''),
                'age': getattr(profile, 'age', ''),
                'birthdate': profile.birthdate.strftime('%Y-%m-%d') if getattr(profile, 'birthdate', None) else '',
                
                'birthplace_region': getattr(profile, 'birthplace_region', ''),
                'birthplace_regionb_name': getattr(profile, 'birthplace_regionb_name', ''),
                
                'birthplace_province': getattr(profile, 'birthplace_province', ''),
                'birthplace_provinceb_name': getattr(profile, 'birthplace_provinceb_name', ''),
                
                'educational_attainment': getattr(profile, 'educational_attainment', ''),
                
                'birthplace_city': getattr(profile, 'birthplace_city', ''),
                'birthplace_cityb_name': getattr(profile, 'birthplace_cityb_name', ''),
                
                'parent_guardian': getattr(profile, 'parent_guardian', ''),
                'permanent_address': getattr(profile, 'permanent_address', ''),
                'course_or_qualification': getattr(profile, 'course_or_qualification', ''),
                'applicant_name': getattr(profile, 'applicant_name', ''),
                'date_accomplished': profile.date_accomplished.strftime('%Y-%m-%d') if getattr(profile, 'date_accomplished', None) else '',
                'id_picture': profile.id_picture.url if getattr(profile, 'id_picture', None) else '',
                'entry_date': profile.entry_date.strftime('%Y-%m-%d') if getattr(profile, 'entry_date', None) else '',
            }
            
            # Add user data if user exists
            if hasattr(profile, 'user') and profile.user:
                profile_data.update({
                    'username': getattr(profile.user, 'username', ''),
                    'user_first_name': getattr(profile.user, 'first_name', ''),
                    'user_last_name': getattr(profile.user, 'last_name', ''),
                    'user_email': getattr(profile.user, 'email', ''),
                })
            
            return JsonResponse(profile_data)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@never_cache
def Homepage_user(request):
    # Check if the user is authenticated, if not redirect to login
    if not request.user.is_authenticated:
        return redirect('Login')  # Ensure the user is redirected to login page if they are not logged in

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            request.session["username"] = user.username

            # Check if the user is an admin
            if user.is_superuser:
                response = redirect("Dashboard_admin")
            else:
                response = redirect("Home")

            # Add no-cache headers
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            return response
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("Login")
       # Retrieve all programs if the user is authenticated
    programs = Programs.objects.all()
    
    # Check if user has a Learner_Profile
    has_learner_profile = Learner_Profile.objects.filter(user=request.user).exists()
    
    # Get user's Google profile picture if available
    user_profile_picture = None
    try:
        from allauth.socialaccount.models import SocialAccount
        social_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
        if social_account and social_account.extra_data:
            user_profile_picture = social_account.extra_data.get('picture')
    except Exception as e:
        # If there's any error, just use the default
        pass
    
    # Render the About_user page with the programs data
    response = render(request, 'Homepage_user.html', {
        'Programss': programs,
        'has_learner_profile': has_learner_profile,
        'user_profile_picture': user_profile_picture
    })

    
    # Prevent caching (this will ensure the page is not cached in the browser)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response

#this is the function for saving the data from forms
from django.shortcuts import render, redirect
from .models import JobPost, Programs

def add_job(request):
    if request.method == 'POST':
        # Get data from the form
        job_title = request.POST.get('job_title')
        company = request.POST.get('company')
        address = request.POST.get('address')
        job_description = request.POST.get('job_description')
        availability = request.POST.get('availability')
        program_id = request.POST.get('expertise')
        # skills = request.POST.getlist('skills[]')  # assuming JavaScript sends array
        # skills = request.POST.getlist('skills')
        skills = request.POST.getlist('skills[]')


        email_or_link = request.POST.get('email_or_link')

        # Get program object
        program = Programs.objects.get(id=program_id) if program_id else None

        # Join skills into a comma-separated string
        skills_str = ', '.join(skills)

        # Create JobPost object
        JobPost.objects.create(
            job_title=job_title,
            company=company,
            address=address,
            job_description=job_description,
            availability=availability,
            program=program,
            skills=skills_str,
            email_or_link=email_or_link
        )

        return redirect('Dashboard_admin')  # Change this to your dashboard view name

    # Optional: If GET request, render the dashboard
    programs = Programs.objects.all()
    jobs = JobPost.objects.all().order_by('-posted_at')
    return render(request, 'Dashboard_admin.html', {'Programss': programs, 'jobss': jobs})

#calling the data from database for jobs
def job_list(request):
    jobs = JobPost.objects.all()
    print("Jobs from DB:", jobs)  # DEBUG LINE
    return render(request, 'Dashboard_admin.html', {'jobss': jobs})


def remove_jobs(request):
    if request.method == 'POST':
        job_ids = request.POST.getlist('job_ids[]')  # or 'job_ids' depending on input names
        for job_id in job_ids:
            job = JobPost.objects.get(id=job_id)
            job.status = 'archived'  # or move to an ArchivedJobs model
            job.save()
        return redirect('Dashboard_admin')  # redirect after POST
    
from django.views.decorators.http import require_POST
    
@require_POST
def archive_jobs(request):
    job_ids = request.POST.getlist('job_ids[]')
    JobPost.objects.filter(id__in=job_ids).update(status='Inactive')
    return redirect('Dashboard_admin')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import ProgramApplication, Programs, Applicant


# def apply_program(request, program_id):
#     program = get_object_or_404(Programs, id=program_id)
#     user = request.user

#     # Prevent duplicate applications
#     application, created = ProgramApplication.objects.get_or_create(applicant=user, program=program)

#     if created:
#         messages.success(request, f"You have successfully applied for the {program.program_name} program.")
#     else:
#         messages.info(request, f"You have already applied for the {program.program_name} program.")

#     return redirect('learner_form')  # Redirect to the program info page

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Programs, ProgramApplication

# @login_required
# def apply_program(request, program_id):
#     program = get_object_or_404(Programs, id=program_id)
#     user = request.user

#     has_applied_before = ProgramApplication.objects.filter(applicant=user).exists()

#     # ✅ First-time applicant
#     if not has_applied_before:
#         ProgramApplication.objects.create(applicant=user, program=program)
#         messages.success(request, f"You have successfully applied for the {program.program_name} program.")
#         return redirect('learner_form')

#     # ✅ User already has applied before, allow to apply more but redirect to dashboard
#     already_applied_to_this = ProgramApplication.objects.filter(applicant=user, program=program).exists()
#     if already_applied_to_this:
#         messages.info(request, f"You already applied for {program.program_name}.")
#     else:
#         ProgramApplication.objects.create(applicant=user, program=program)
#         messages.success(request, f"Application submitted for {program.program_name}.")

#     return redirect('Dashboard')

# @login_required
# def apply_program(request, program_id):
#     program = get_object_or_404(Programs, id=program_id)
#     user = request.user

#     # Count how many programs the user already applied to
#     application_count = ProgramApplication.objects.filter(applicant=user).count()

#     if application_count >= 2:
#         messages.error(request, "You have reached the maximum of 2 program slots.")
#         return redirect('Dashboard')  # or wherever you want to redirect them

#     # Check if user already applied to this specific program
#     already_applied_to_this = ProgramApplication.objects.filter(applicant=user, program=program).exists()

#     if already_applied_to_this:
#         messages.info(request, f"You already applied for {program.program_name}.")
#     else:
#         ProgramApplication.objects.create(applicant=user, program=program)
#         messages.success(request, f"Application submitted for {program.program_name}.")

#         # Redirect to learner form only if it's the user's first application
#         if application_count == 0:
#             return redirect('learner_form')

#     return redirect('Dashboard')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Programs, ProgramApplication, Notification
from .utils import send_application_notification, mark_notification_as_read, get_unread_notifications

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .utils import send_application_notification, get_unread_notifications, mark_notification_as_read

@login_required
def apply_program(request, program_id):
    program = get_object_or_404(Programs, id=program_id)
    user = request.user

    # Count how many programs the user already applied to
    application_count = ProgramApplication.objects.filter(applicant=user).count()

    if application_count >= 2:
        messages.error(request, "You have reached the maximum of 2 program slots.")
        return redirect('Dashboard')

    # Check if user already applied to this specific program
    already_applied_to_this = ProgramApplication.objects.filter(applicant=user, program=program).exists()

    if already_applied_to_this:
        messages.info(request, f"You already applied for {program.program_name}.")
    else:
        # Create the application
        ProgramApplication.objects.create(applicant=user, program=program)
        messages.success(request, f"Application submitted for {program.program_name}.")

        # Set session flag for modal
        request.session['show_application_modal'] = True
        request.session['applied_program_name'] = program.program_name
        
        # Send notification and email to admins
        send_application_notification(user, program)

        # Create notification for the applicant
        create_application_notification(request.user, program)

        # Redirect to learner form only if it's the user's first application
        if application_count == 0:
            return redirect('learner_form')

    return redirect('Dashboard')

def get_training_data(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Get all trainings and format them for JSON response
        all_trainings = Training.objects.all()  # Replace with your model
        training_data = []
        
        for training in all_trainings:
            training_data.append({
                'id': training.id,
                'name': training.program_name,
                'date': training.start_date.strftime('%Y-%m-%d'),
                'time': training.task_time.strftime('%H:%M') if training.task_time else '09:00',
                'endTime': training.end_time.strftime('%H:%M') if training.end_time else '10:00',
                'room': training.room_lab,
                'trainer': training.trainer.get_full_name() or training.trainer.username,
                'trainerId': training.trainer.id,
                'category': training.category or 'activity',
                'description': training.description or '',
                'isOwn': training.trainer.id == request.user.id
            })
        
        return JsonResponse({
            'success': True,
            'all_trainings': training_data
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

# 🔥 ADD THIS VIEW TO CLEAR SESSION
@login_required
@require_POST
def clear_modal_session(request):
    """Clear the modal session flags"""
    try:
        if 'show_application_modal' in request.session:
            del request.session['show_application_modal']
        if 'applied_program_name' in request.session:
            del request.session['applied_program_name']
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

# Add these utility functions at the top of your views.py after imports
def get_unread_notifications(user):
    """Get unread notifications for a user"""
    return Notification.objects.filter(recipient=user, is_read=False)

def create_application_notification(user, program):
    """Create notification when user applies for a program"""
    # Notify all admin users
    admin_users = Applicant.objects.filter(is_superuser=True)
    for admin in admin_users:
        Notification.objects.create(
            recipient=admin,
            sender=user,
            notification_type='application',
            title=f'New Application: {program.program_name}',
            message=f'{user.username} has applied for {program.program_name}.'
        )

def send_application_notification(user, program):
    """Send notification to admins about new application"""
    create_application_notification(user, program)

@login_required
def get_notifications(request):
    """API endpoint to get notifications for the current user"""
    try:
        notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')[:20]
        
        notifications_data = []
        for notification in notifications:
            notifications_data.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'notification_type': notification.notification_type,
                'is_read': notification.is_read,
                'created_at': notification.created_at.strftime('%b %d, %Y %I:%M %p'),
                'sender': notification.sender.username if notification.sender else 'System'
            })
        
        unread_count = notifications.filter(is_read=False).count()
        
        return JsonResponse({
            'notifications': notifications_data,
            'unread_count': unread_count
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    try:
        notification = get_object_or_404(
            Notification, 
            id=notification_id, 
            recipient=request.user
        )
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
@ensure_csrf_cookie
def mark_all_notifications_read(request):
    """Mark all notifications as read for the current user"""
    try:
        Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def create_program_completion_notification(applicant, program_name):
    """Create a notification when applicant completes a program"""
    try:
        Notification.objects.create(
            recipient=applicant,
            sender=None,  # System notification
            notification_type='program_completion',
            title='Program Completion',
            message=f'Congratulations! You have successfully completed the {program_name} program.',
            is_read=False
        )
    except Exception as e:
        print(f"Error creating program completion notification: {str(e)}")

@staff_member_required
@login_required
def approve_application(request, application_id):
    from datetime import datetime
    application = get_object_or_404(ProgramApplication, id=application_id)

    # Get the current batch cycle
    batch_cycle = BatchCycle.get_active_cycle()
    current_year = datetime.now().year

    # Determine application type based on the class
    app_type = 'online' if application.__class__.__name__ == 'ProgramApplication' else 'walkin'
    
    # Get the trainer's current semester for this program
    current_semester = batch_cycle.current_semester  # Default fallback
    try:
        trainer_profile = TrainerProfile.objects.filter(program=application.program).first()
        if trainer_profile:
            semester_settings = ActiveSemesterSettings.get_or_create_for_trainer(trainer_profile.user)
            current_semester = semester_settings.active_semester
    except Exception as e:
        # Use batch cycle default if any error occurs
        pass

    # Create a new ApprovedApplicant entry with batch cycle information
    ApprovedApplicant.objects.create(
        applicant=application.applicant,
        program=application.program,
        application_type=app_type,  # Dynamically set based on application type
        batch_number=batch_cycle.current_batch,
        enrollment_year=current_year,
        enrollment_semester=current_semester  # Save the semester at enrollment time
    )

    # Create notification for the applicant
    Notification.objects.create(
        recipient=application.applicant,
        sender=request.user,  # The admin who approved
        notification_type='approval',
        title=f"Application Approved: {application.program.program_name}",
        message=f"Congratulations! Your application for {application.program.program_name} has been approved. You are enrolled in Batch {batch_cycle.current_batch}, Year {current_year}."
    )

    # Delete the original ProgramApplication entry
    application.delete()

    messages.success(request, f"{application.applicant.username} has been approved for {application.program.program_name}.")
    return redirect('Dashboard_admin')

@staff_member_required
@login_required
def reject_application(request, application_id):
    application = get_object_or_404(ProgramApplication, id=application_id)
    
    # Create notification for the applicant
    Notification.objects.create(
        recipient=application.applicant,
        sender=request.user,
        notification_type='rejection',
        title=f"Application Status: {application.program.program_name}",
        message=f"Thank you for your interest in {application.program.program_name}. Unfortunately, your application was not approved at this time."
    )
    
    # Delete the application
    application.delete()
    
    messages.info(request, f"Application for {application.program.program_name} has been rejected.")
    return redirect('Dashboard_admin')


def decline_application(request):
    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        decline_reason = request.POST.get('decline_reason')
        application = get_object_or_404(ProgramApplication, id=application_id)

        # Update the status and reason
        application.status = 'Declined'
        application.decline_reason = decline_reason
        application.save()

        # OPTIONAL: Send notification email or store message
        # from .utils import notify_decline
        # notify_decline(application)

        messages.success(request, f"{application.applicant.username}'s application has been declined.")
        return redirect('Dashboard_admin')  # Replace with actual view name

from django.core.paginator import Paginator
from django.shortcuts import render

@login_required
def applications_list(request):
    applications = ProgramApplication.objects.all().order_by('-applied_at')  # or filter as needed

    paginator = Paginator(applications, 5)  # Show 10 applications per page
    page_number = request.GET.get('page') or 1
    page_obj = paginator.get_page(page_number)

    return render(request, 'Dashboard_admin.html', {
        'applicants': page_obj,
    })



from django.shortcuts import get_object_or_404, render
from .models import Learner_Profile

def view_profile(request, pk):
    profile = get_object_or_404(Learner_Profile, pk=pk)
    return render(request, 'Dashboard_admin.html', {'profile': profile})



from django.utils.dateparse import parse_date
from .models import ProgramApplication, Programs

def view_applications(request):
    status = request.GET.get('status')
    program_id = request.GET.get('program')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    applicants = ProgramApplication.objects.all()

    if status:
        applicants = applicants.filter(status=status)
    if program_id:
        applicants = applicants.filter(program_id=program_id)
    if start_date:
        applicants = applicants.filter(applied_at__date__gte=parse_date(start_date))
    if end_date:
        applicants = applicants.filter(applied_at__date__lte=parse_date(end_date))

    programs = Programs.objects.all()  # For the program filter dropdown

    return render(request, 'Dashboard_admin.html', {
        'applicants': applicants,
        'all_programs': programs,
    })

def view_applications(request):
    status = request.GET.get('status')

    if status:
        applicants = ProgramApplication.objects.filter(status=status)
    else:
        applicants = ProgramApplication.objects.all()

    return render(request, 'your_template.html', {
        'applicants': applicants
    })



@login_required
def view_applicants(request, program_id):
    program = get_object_or_404(Programs, id=program_id)
    applicants = ProgramApplication.objects.filter(program=program)

    context = {
        'applicants': applicants,
        'program': program
    }

    return render(request, 'Application.html', context)


def update_job(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)
    
    if request.method == 'POST':
        job.job_title = request.POST.get('job_title')
        job.company = request.POST.get('company')
        job.address = request.POST.get('address')
        job.job_description = request.POST.get('description')
        job.availability = request.POST.get('availability')
        job.program = request.POST.get('program')
        job.skills = request.POST.get('skills')
        job.email_or_link = request.POST.get('email_or_link')
        job.save()

        return redirect('Dashboard_admin')  # Redirect to your dashboard or any other page

    return render(request, 'Dashboard_admin.html', {'job': job})




from django.shortcuts import render, redirect
from .models import Learner_Profile, ClientClassification, DisabilityType, DisabilityCause
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from datetime import datetime
from .forms import LearnerProfileForm

@login_required
def cancel_application(request):
    """Cancel the user's pending application and redirect to program selection page"""
    try:
        # Find and delete the user's pending application
        application = ProgramApplication.objects.filter(
            applicant=request.user,
            status='Pending'
        ).first()
        
        if application:
            program_name = application.program.program_name
            application.delete()
            messages.success(request, f"Your application for {program_name} has been cancelled successfully. You can now apply to a different program.")
        else:
            messages.info(request, "No pending application found.")
            
    except Exception as e:
        messages.error(request, f"Error cancelling application: {str(e)}")
    
    # Redirect to the programs page
    return redirect('Program_user')


def learner_profile_form(request):
    if request.method == 'POST':
        # Handle form submission manually since the HTML form doesn't match the Django form exactly
        try:
            # Create a new Learner_Profile instance
            profile_instance = Learner_Profile()
            profile_instance.user = request.user
            
            # Handle basic fields
            profile_instance.entry_date = request.POST.get('entry_date') or None
            profile_instance.last_name = request.POST.get('last_name', '').upper()
            profile_instance.first_name = request.POST.get('first_name', '').upper()
            profile_instance.middle_name = request.POST.get('middle_name', '').upper()
            profile_instance.extension_name = request.POST.get('extension_name', '').upper()
            
            # Handle address fields
            profile_instance.region = request.POST.get('region', '')
            profile_instance.province = request.POST.get('province', '')
            profile_instance.city = request.POST.get('city', '')  # This comes from municipality in the form
            profile_instance.barangay = request.POST.get('barangay', '')  # Get the barangay code/ID
            profile_instance.barangay_name = request.POST.get('barangay_name', '')  # Get the actual barangay name
            profile_instance.district = request.POST.get('district', '').upper()
            profile_instance.street = request.POST.get('street', '').upper()  # This comes from house-street in the form
            
            # Handle contact info
            profile_instance.email = request.POST.get('email', '').upper()
            profile_instance.contact_number = request.POST.get('contact_number', '')
            profile_instance.nationality = request.POST.get('nationality', 'Filipino').upper()
            
            # Handle personal info
            profile_instance.sex = request.POST.get('sex', 'Not Specified')
            profile_instance.civil_status = request.POST.get('civil_status', '')
            profile_instance.employment_status = request.POST.get('employment_status', '')
            profile_instance.monthly_income = request.POST.get('monthly_income', '').upper()
            profile_instance.date_hired = request.POST.get('date_hired') or None
            profile_instance.company_name = request.POST.get('company_name', '').upper()
            
            # Handle birthdate
            birth_day = request.POST.get('birth_day')
            birth_month = request.POST.get('birth_month')
            birth_year = request.POST.get('birth_year')
            if birth_day and birth_month and birth_year:
                try:
                    # Convert month name to number if it's a name
                    if not birth_month.isdigit():
                        months = {
                            'January': 1, 'February': 2, 'March': 3, 'April': 4,
                            'May': 5, 'June': 6, 'July': 7, 'August': 8,
                            'September': 9, 'October': 10, 'November': 11, 'December': 12
                        }
                        birth_month = months.get(birth_month, 1)
                    
                    profile_instance.birthdate = datetime.strptime(f"{birth_year}-{int(birth_month):02d}-{int(birth_day):02d}", "%Y-%m-%d").date()
                except ValueError:
                    profile_instance.birthdate = None
            else:
                profile_instance.birthdate = None
            
            # Handle age (calculated from birthdate)
            if profile_instance.birthdate:
                today = datetime.today().date()
                profile_instance.age = today.year - profile_instance.birthdate.year - ((today.month, today.day) < (profile_instance.birthdate.month, profile_instance.birthdate.day))
            else:
                profile_instance.age = None
            
            # Handle birthplace
            profile_instance.birthplace_regionb_name = request.POST.get('birthplace-region-name', '')
            profile_instance.birthplace_provinceb_name = request.POST.get('birthplace-province-name', '')
            profile_instance.birthplace_cityb_name = request.POST.get('birthplace-city-name', '')
            # Handle parent/guardian info
            profile_instance.parent_guardian = request.POST.get('parent_guardian', '').upper()
            profile_instance.permanent_address = request.POST.get('permanent_address', '').upper()
            
            # Handle course info
            profile_instance.course_or_qualification = request.POST.get('course_or_qualification', '').upper()
            profile_instance.scholarship_package = request.POST.get('scholarship_package', '').upper()
            
            # Handle educational attainment
            profile_instance.educational_attainment = request.POST.get('educational_attainment', '').upper()
            
            # Handle privacy agreement
            agree_to_privacy = request.POST.get("agree_to_privacy") == "True"
            profile_instance.agree_to_privacy = agree_to_privacy
            
            # Handle applicant signature info
            profile_instance.applicant_name = request.POST.get('applicant_name', '').upper()
            profile_instance.date_accomplished = request.POST.get('date_accomplished') or None
            
            # Handle file uploads
            if 'id_picture' in request.FILES:
                profile_instance.id_picture = request.FILES['id_picture']
            
            if 'applicant_signature' in request.FILES:
                profile_instance.applicant_signature = request.FILES['applicant_signature']
            
            # Save the profile instance first
            profile_instance.save()
            
            # Handle many-to-many fields after saving
            # Client classifications
            classification_ids = request.POST.getlist('client-classification')
            if classification_ids:
                # Handle "Others" classification
                other_classification = request.POST.get('others-classification-specify', '').strip()
                if other_classification:
                    # Store the "Others" classification in the model field
                    profile_instance.other_classification = other_classification
                    # Remove "Others" from the classification_ids if it's there
                    classification_ids = [id for id in classification_ids if id != "Others"]
                
                # Convert to integers and set classifications
                try:
                    classification_ids = [int(id) for id in classification_ids if id.isdigit()]
                    profile_instance.classifications.set(classification_ids)
                except (ValueError, TypeError):
                    pass  # Handle the error appropriately
            
            # Disability types
            disability_type_ids = request.POST.getlist('disability-type')
            if disability_type_ids:
                try:
                    disability_type_ids = [int(id) for id in disability_type_ids if id.isdigit()]
                    profile_instance.disability_types.set(disability_type_ids)
                except (ValueError, TypeError):
                    pass  # Handle the error appropriately
            
            # Disability causes
            disability_cause_ids = request.POST.getlist('disability-cause')
            if disability_cause_ids:
                try:
                    disability_cause_ids = [int(id) for id in disability_cause_ids if id.isdigit()]
                    profile_instance.disability_causes.set(disability_cause_ids)
                except (ValueError, TypeError):
                    pass  # Handle the error appropriately
            
            return redirect('Dashboard')  # Redirect to a success page
        except Exception as e:
            # Handle any errors that occur during form processing
            print(f"Error processing form: {e}")
            # You might want to add error messaging to the context here
            pass
    
    # GET request - show empty form
    context = {
        'classifications': ClientClassification.objects.all(),
        'disability_types': DisabilityType.objects.all(),
        'disability_causes': DisabilityCause.objects.all(),
    }
    return render(request, 'registration_f1.html', context)


def walkin_step1_registration(request):
    """Handle walk-in step 1 registration - create user and apply to program"""
    if request.method == 'POST':
        try:
            # Get basic info from step 1
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            middle_name = request.POST.get('middle_name', '').strip()
            program_id = request.POST.get('selected_program')
            
            if not first_name or not last_name or not program_id:
                return JsonResponse({
                    'success': False,
                    'error': "First name, last name, and program selection are required."
                })
            
            # Generate username (fullname with no spaces)
            username = f"{first_name.lower()}{middle_name.lower()}{last_name.lower()}".replace(' ', '')
            
            # Check if username already exists, add number if needed
            base_username = username
            counter = 1
            while Applicant.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            # Create basic user account
            user = Applicant.objects.create_user(
                username=username,
                email=f"{username}@walkin.local",
                password='DLLlmstc',
                first_name=first_name,
                last_name=last_name
            )
            
            # Get the program and create application using apply_program logic
            program = get_object_or_404(Programs, id=program_id)
            
            # Create program application
            application = ProgramApplication.objects.create(applicant=user, program=program)
            
            # Create walk-in application for tracking
            from .models import WalkInApplication
            from django.utils import timezone
            from django.db import models
            today = timezone.now().date()
            last_queue = WalkInApplication.objects.filter(
                applied_at__date=today
            ).aggregate(models.Max('queue_number'))['queue_number__max']
            next_queue = (last_queue or 0) + 1
            
            WalkInApplication.objects.create(
                applicant=user,
                program=program,
                status='Pending',
                queue_number=next_queue,
                processed_by=request.user if request.user.is_authenticated else None
            )
            
            # Return success with redirect URL to form.html
            return JsonResponse({
                'success': True,
                'username': username,
                'password': 'DLLlmstc',
                'redirect_url': f'/learner_form/?walkin=true&username={username}'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def walkin_registration(request):
    """Handle walk-in registration from admin dashboard modal"""
    if request.method == 'POST':
        try:
            # Get basic info from step 1
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            middle_name = request.POST.get('middle_name', '').strip()
            program_id = request.POST.get('selected_program')
            
            if not first_name or not last_name or not program_id:
                messages.error(request, "First name, last name, and program selection are required.")
                return redirect('Dashboard_admin')
            
            # Generate username (fullname with no spaces)
            username = f"{first_name.lower()}{middle_name.lower()}{last_name.lower()}".replace(' ', '')
            
            # Check if username already exists, add number if needed
            base_username = username
            counter = 1
            while Applicant.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            # Create user account with standard password
            user = Applicant.objects.create_user(
                username=username,
                email=request.POST.get('email', f"{username}@walkin.local"),
                password='DLLlmstc',
                first_name=first_name,
                last_name=last_name
            )
            
            # Create learner profile
            profile_instance = Learner_Profile()
            profile_instance.user = user
            
            # Extract form data from registration form
            profile_instance.entry_date = request.POST.get('entry_date') or None
            profile_instance.last_name = last_name.upper()
            profile_instance.first_name = first_name.upper()
            profile_instance.middle_name = middle_name.upper()
            profile_instance.sex = request.POST.get('sex', '')
            profile_instance.civil_status = request.POST.get('civil_status', '')
            profile_instance.employment_status = request.POST.get('employment_status', '')
            profile_instance.monthly_income = request.POST.get('monthly_income', '')
            profile_instance.date_hired = request.POST.get('date_hired') or None
            profile_instance.company_name = request.POST.get('company_name', '').upper()
            
            # Handle birthdate from separate fields
            birth_month = request.POST.get('birth_month')
            birth_day = request.POST.get('birth_day')
            birth_year = request.POST.get('birth_year')
            if birth_month and birth_day and birth_year:
                try:
                    profile_instance.birthdate = f"{birth_year}-{birth_month.zfill(2)}-{birth_day.zfill(2)}"
                except:
                    pass
            
            profile_instance.age = request.POST.get('age') or None
            profile_instance.educational_attainment = request.POST.get('educational_attainment', '')
            profile_instance.parent_guardian = request.POST.get('parent_guardian', '').upper()
            profile_instance.permanent_address = request.POST.get('permanent_address', '').upper()
            
            # Address fields
            profile_instance.region = request.POST.get('region', '')
            profile_instance.region_name = request.POST.get('region_name', '')
            profile_instance.province = request.POST.get('province', '')
            profile_instance.province_name = request.POST.get('province_name', '')
            profile_instance.city = request.POST.get('city', '')
            profile_instance.city_name = request.POST.get('city_name', '')
            profile_instance.barangay = request.POST.get('barangay', '')
            profile_instance.barangay_name = request.POST.get('barangay_name', '')
            profile_instance.district = request.POST.get('district', '')
            profile_instance.street = request.POST.get('street', '').upper()
            profile_instance.contact_number = request.POST.get('contact_number', '')
            profile_instance.email = request.POST.get('email', '')
            profile_instance.nationality = request.POST.get('nationality', 'Filipino').upper()
            
            # Birthplace fields
            profile_instance.birthplace_regionb_name = request.POST.get('birthplace_regionb_name', '')
            profile_instance.birthplace_provinceb_name = request.POST.get('birthplace_provinceb_name', '')
            profile_instance.birthplace_cityb_name = request.POST.get('birthplace_cityb_name', '')
            
            # Privacy agreement
            profile_instance.agree_to_privacy = request.POST.get('agree_to_privacy') == 'on'
            
            # Handle file uploads
            if 'id_picture' in request.FILES:
                profile_instance.id_picture = request.FILES['id_picture']
            if 'applicant_signature' in request.FILES:
                profile_instance.applicant_signature = request.FILES['applicant_signature']
            
            profile_instance.applicant_name = f"{first_name} {last_name}".upper()
            profile_instance.date_accomplished = request.POST.get('date_accomplished') or None
            
            profile_instance.save()

            # Handle many-to-many fields
            classification_ids = request.POST.getlist('client-classification')
            if classification_ids:
                profile_instance.classifications.set(classification_ids)

            disability_type_ids = request.POST.getlist('disability-type')
            if disability_type_ids:
                profile_instance.disability_types.set(disability_type_ids)

            disability_cause_ids = request.POST.getlist('disability-cause')
            if disability_cause_ids:
                profile_instance.disability_causes.set(disability_cause_ids)

            # Create both walk-in application and regular program application
            try:
                program = Programs.objects.get(id=program_id)
                # Import the new model at the top if not already imported
                from .models import WalkInApplication
                
                # Get the next queue number for today
                from django.utils import timezone
                today = timezone.now().date()
                last_queue = WalkInApplication.objects.filter(
                    applied_at__date=today
                ).aggregate(models.Max('queue_number'))['queue_number__max']
                next_queue = (last_queue or 0) + 1
                
                # Create walk-in application
                WalkInApplication.objects.create(
                    applicant=user,
                    program=program,
                    status='Pending',
                    queue_number=next_queue,
                    processed_by=request.user if request.user.is_authenticated else None
                )
                
                # Also create regular program application so the name appears in the main table
                ProgramApplication.objects.create(
                    applicant=user,
                    program=program,
                    status='Pending'
                )
                
                # Check if this is an AJAX request
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'username': username,
                        'full_name': f"{first_name} {middle_name} {last_name}".strip(),
                        'message': f"Walk-in registration for {first_name} {last_name} completed successfully!"
                    })
                
                # Store credentials in session for display
                request.session['walkin_credentials'] = {
                    'username': username,
                    'password': 'DLLlmstc',
                    'full_name': f"{first_name} {middle_name} {last_name}".strip()
                }
                
                messages.success(request, f"Walk-in registration for {first_name} {last_name} completed successfully!")
                
                # Check if this came from the form.html (walk-in registration form)
                if request.META.get('HTTP_REFERER') and 'walkin=true' in request.META.get('HTTP_REFERER', ''):
                    # Return a success page that will close the tab
                    return render(request, 'walkin_success.html', {
                        'username': username,
                        'full_name': f"{first_name} {middle_name} {last_name}".strip(),
                        'close_tab': True
                    })
                
                return redirect('Dashboard_admin')
                
            except Programs.DoesNotExist:
                messages.error(request, "Selected program not found.")
                return redirect('Dashboard_admin')

        except Exception as e:
            print(f"Error saving walk-in registration: {e}")
            messages.error(request, f"An error occurred while saving the walk-in registration: {str(e)}")
            return redirect('Dashboard_admin')
    
    # If not POST, redirect back to admin dashboard
    return redirect('Dashboard_admin')


# In your app's views.py

from django.shortcuts import render
from .models import Learner_Profile # Import your model
from django.contrib.auth.decorators import login_required

@login_required # Ensure the user is logged in
def dashboard_view(request):
    # Assuming Learner_profile has a OneToOneField or ForeignKey to User
    # If it's a OneToOneField to User:
    try:
        profile = Learner_Profile.objects.get(user=request.user)
    except Learner_Profile.DoesNotExist:
        profile = None # Or create a new profile: Learner_profile.objects.create(user=request.user)
    
    # If Learner_profile has a ForeignKey to User, and a user can have multiple profiles:
    # profiles = Learner_profile.objects.filter(user=request.user)
    # If you expect only one, you might still use .get() or .first()
    
    # Example for applications (if applicable)
    # from .models import Application
    # applications = Application.objects.filter(user=request.user) # Assuming Application model exists

    # You might also need these if you have them in your context:
    # classic = ['Some Classification'] # Replace with actual data if dynamic
    # disability_types = YourDisabilityTypeModel.objects.all() # Assuming models for these
    # disability_causes = YourDisabilityCauseModel.objects.all() # Assuming models for these

    context = {
        'username': request.user.username,
        'profile': profile, # THIS IS CRUCIAL!
        # 'applications': applications, # Add if you're using this for the overview section
        # 'classic': classic,
        # 'disability_types': disability_types,
        # 'disability_causes': disability_causes,
    }
    return render(request, 'Dashboard.html', context)


from .models import Learner_Profile

def update_profile(request):
    """Handle profile updates from the dashboard"""
    if request.method == 'POST':
        try:
            # Get the user's profile
            profile = get_object_or_404(Learner_Profile, user=request.user)
            
            # Update profile fields from form data
            profile.entry_date = request.POST.get('entry_date') or profile.entry_date
            profile.last_name = request.POST.get('last_name', profile.last_name)
            profile.first_name = request.POST.get('first_name', profile.first_name)
            profile.middle_name = request.POST.get('middle_name', profile.middle_name)
            profile.region = request.POST.get('region_name', profile.region)
            profile.province = request.POST.get('province_name', profile.province)
            profile.city = request.POST.get('city_name', profile.city)
            profile.barangay_name = request.POST.get('barangay_name', profile.barangay_name)
            profile.district = request.POST.get('district', profile.district)
            profile.street = request.POST.get('street', profile.street)
            profile.email = request.POST.get('email', profile.email)
            profile.contact_number = request.POST.get('contact_number', profile.contact_number)
            profile.nationality = request.POST.get('nationality', profile.nationality)
            profile.monthly_income = request.POST.get('monthly_income', profile.monthly_income)
            profile.date_hired = request.POST.get('date_hired') or profile.date_hired
            profile.company_name = request.POST.get('company_name', profile.company_name)
            profile.birthdate = request.POST.get('birthdate') or profile.birthdate
            profile.age = request.POST.get('age', profile.age)
            profile.birthplace_regionb_name = request.POST.get('birthplace-region-name', profile.birthplace_regionb_name)
            profile.birthplace_provinceb_name = request.POST.get('birthplace-province-name', profile.birthplace_provinceb_name)
            profile.birthplace_cityb_name = request.POST.get('birthplace-city-name', profile.birthplace_cityb_name)
            profile.other_classification = request.POST.get('other_classification', profile.other_classification)
            profile.course_or_qualification = request.POST.get('course_or_qualification', profile.course_or_qualification)
            
            # Save the updated profile
            profile.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('Dashboard')
            
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
            return redirect('Dashboard')
    
    return redirect('Dashboard')

def profile_views(request, pk):
    learner_profile = Learner_Profile.objects.get(pk=pk)
    classifications = learner_profile.classifications.all()  # <- Get selected classifications

    context = {
        'learner_profile': learner_profile,
        'classifications': classifications,  # Pass this to the template
    }

    return render(request, 'Dashboard_admin.html', context)

@csrf_exempt
@require_POST
def send_application_notification_view(request):
    """Send notification when admin wants to notify an applicant"""
    try:
        data = json.loads(request.body)
        application_id = data.get('application_id')
        username = data.get('username')
        
        # Get the application
        application = get_object_or_404(ProgramApplication, id=application_id)
        
        # Create notification
        Notification.objects.create(
            recipient=application.applicant,
            sender=request.user,
            notification_type='admin_message',
            title=f"Update on your {application.program.program_name} application",
            message=f"Hello {username}, there's an update regarding your application for {application.program.program_name}. Please check your dashboard for more details."
        )
        
        return JsonResponse({'success': True, 'message': 'Notification sent successfully'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

#Example
def register_v1(request):
  template = loader.get_template('register_v1.html')
  return HttpResponse(template.render())


from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from .models import Training, Applicant
from .forms import TrainingForm
import json

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Training
from .forms import TrainingForm

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Training, Attendance, ApprovedApplicant
from .forms import TrainingForm
import json
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

# @login_required
# def training_management(request):
#     if request.method == 'POST':
#         form = TrainingForm(request.POST)
#         if form.is_valid():
#             training = form.save(commit=False)
#             training.trainer = request.user  # Ensure trainer is set
#             training.save()
            
#             # Debug: Print to verify the task was saved
#             print(f"✅ Training saved: {training.program_name} on {training.start_date}")
            
#             # If it's an AJAX request, return JSON response
#             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 return JsonResponse({
#                     'success': True,
#                     'training': {
#                         'id': training.id,
#                         'program_name': training.program_name,
#                         'start_date': training.start_date.strftime('%Y-%m-%d'),
#                         'task_time': training.task_time.strftime('%H:%M') if training.task_time else '09:00',
#                         'end_time': training.end_time.strftime('%H:%M') if training.end_time else '10:00',
#                         'room_lab': training.room_lab,
#                         'trainer_name': request.user.get_full_name() or request.user.username,
#                         'category': training.category or 'activity',
#                         'description': training.description or '',
#                     }
#                 })
            
#             return redirect('Dashboard_trainor')
#         else:
#             # Form has errors
#             print(f"❌ Form errors: {form.errors}")
#             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 return JsonResponse({
#                     'success': False,
#                     'errors': form.errors
#                 })
#     else:
#         form = TrainingForm()
    
#     # IMPORTANT: Load ALL trainings for the current user
#     trainings = Training.objects.filter(trainer=request.user).order_by('start_date')
    
#     # Debug: Print loaded trainings
#     print(f"📅 Loading {trainings.count()} trainings for user {request.user.username}")
#     for training in trainings:
#         print(f"   - {training.program_name} on {training.start_date}")
    
#     # Get approved applicants
#     approved_applicants = ApprovedApplicant.objects.filter(program__trainer=request.user)
    
#     context = {
#         'form': form,
#         'trainings': trainings,
#         'approvedapplicant': approved_applicants,
#         'trainer_profile': {'user': request.user},
#     }
    
#     return render(request, 'Dashboard_trainor.html', context)

# @csrf_exempt
# @login_required
# def save_attendance(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             training_id = data.get('training_id')
#             attendance_data = data.get('attendance', [])
            
#             training = get_object_or_404(Training, id=training_id)
            
#             # Process attendance data
#             for item in attendance_data:
#                 student_id = item.get('student_id')
#                 status = item.get('status')
                
#                 if student_id and status:
#                     # Update or create attendance record
#                     Attendance.objects.update_or_create(
#                         training=training,
#                         student_id=student_id,
#                         defaults={
#                             'status': status,
#                             'recorded_by': request.user
#                         }
#                     )
            
#             return JsonResponse({'success': True})
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)})
    
#     return JsonResponse({'success': False, 'error': 'Invalid request method'})

# @login_required
# def get_attendance(request, training_id):
#     training = get_object_or_404(Training, id=training_id)
    
#     # Get all students in the program
#     students = ApprovedApplicant.objects.filter(program__trainer=request.user)
    
#     # Get existing attendance records
#     attendance_records = Attendance.objects.filter(training=training)
    
#     # Create a dictionary of student attendance
#     attendance_data = {}
#     for record in attendance_records:
#         attendance_data[record.student_id] = record.status
    
#     # Prepare data for response
#     student_data = []
#     for student in students:
#         student_data.append({
#             'id': student.applicant.id,
#             'name': student.applicant.get_full_name() or student.applicant.username,
#             'status': attendance_data.get(student.applicant.id, '')
#         })
    
#     return JsonResponse({
#         'training': {
#             'id': training.id,
#             'name': training.program_name,
#             'date': training.start_date.strftime('%Y-%m-%d'),
#             'time': training.task_time.strftime('%H:%M') if training.task_time else '09:00',
#             'end_time': training.end_time.strftime('%H:%M') if training.end_time else '10:00',
#         },
#         'students': student_data
#     })

from django.shortcuts import render
from .models import Training

def training_list(request):
    trainings = Training.objects.all()  # get all training sessions
    return render(request, 'Dashboard.html', {'trainings': trainings})


import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.db.models import Count, Q
from .models import Training, Attendance, ApprovedApplicant
from .forms import TrainingForm
from .models import Applicant  # Import Applicant model for get_student_attendance_summary

# Also fix the save_attendance function to ensure proper saving
@csrf_exempt
@login_required
def save_attendance(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            training_id = data.get('training_id')
            attendance_data = data.get('attendance', [])
            target_date = data.get('target_date')  # Get the target date for multi-day training
            
            training = get_object_or_404(Training, id=training_id)
            
            # Convert target_date string to date object if provided
            attendance_date = None
            if target_date:
                from datetime import datetime
                attendance_date = datetime.strptime(target_date, '%Y-%m-%d').date()
            
            # Process attendance data
            for item in attendance_data:
                student_id = item.get('student_id')
                status = item.get('status')
                
                if student_id and status:
                    # Get the student user object
                    try:
                        student_user = Applicant.objects.get(id=student_id)
                        
                        # Update or create attendance record with date support
                        attendance, created = Attendance.objects.update_or_create(
                            training=training,
                            student=student_user,
                            attendance_date=attendance_date,  # Include the specific date
                            defaults={
                                'status': status,
                                'recorded_by': request.user
                            }
                        )
                        
                        # Debug print
                        action = "Created" if created else "Updated"
                        date_info = f" for {attendance_date}" if attendance_date else ""
                        print(f"{action} attendance: {student_user.username} - {status} for {training.program_name}{date_info}")
                        
                    except Applicant.DoesNotExist:
                        print(f"Student with ID {student_id} not found")
                        continue
            
            # Calculate updated counts after saving (pass the date for multi-day training)
            attendance_counts = calculate_attendance_counts(training, attendance_date)
            
            return JsonResponse({
                'success': True,
                'counts': attendance_counts,
                'message': 'Attendance saved successfully'
            })
        except Exception as e:
            print(f"Error saving attendance: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# Fix the calculate_attendance_counts function
def calculate_attendance_counts(training, attendance_date=None):
    """Calculate present and absent counts for a training session"""
    # Get all students enrolled in the program for this trainer
    enrolled_students = ApprovedApplicant.objects.filter(
        program=training.trainer.trainerprofile.program  # Get students from trainer's program
    ).values_list('applicant', flat=True)
    
    total_students = len(enrolled_students)
    
    # Build filter for attendance records
    attendance_filter = {
        'training': training,
        'attendance_date': attendance_date
    }
    
    # Count present students for this specific training and date
    present_count = Attendance.objects.filter(
        **attendance_filter,
        status='present'
    ).count()
    
    # Count absent students for this specific training and date
    absent_count = Attendance.objects.filter(
        **attendance_filter,
        status='missed'
    ).count()
    
    # Students not yet marked
    not_marked = total_students - (present_count + absent_count)
    
    return {
        'total_present': present_count,
        'total_absent': absent_count,
        'not_marked': not_marked,
        'total_students': total_students
    }

# Add this new view to get individual student attendance
@login_required
def get_student_attendance(request, student_id):
    """Get attendance summary for a specific student"""
    try:
        student = get_object_or_404(Applicant, id=student_id)
        
        # Count present attendance
        total_present = Attendance.objects.filter(
            student=student,
            training__trainer=request.user,
            status='present'
        ).count()
        
        # Count absent attendance
        total_absent = Attendance.objects.filter(
            student=student,
            training__trainer=request.user,
            status='missed'
        ).count()
        
        # Get total sessions
        total_sessions = Training.objects.filter(trainer=request.user).count()
        
        return JsonResponse({
            'success': True,
            'total_present': total_present,
            'total_absent': total_absent,
            'total_sessions': total_sessions
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_attendance(request, training_id):
    training = get_object_or_404(Training, id=training_id)
    
    # Get target date for multi-day training
    target_date = request.GET.get('target_date')
    attendance_date = None
    if target_date:
        from datetime import datetime
        attendance_date = datetime.strptime(target_date, '%Y-%m-%d').date()
    
    # Get all students in the program
    students = ApprovedApplicant.objects.filter(program__trainer=request.user)
    
    # Get existing attendance records for the specific date
    attendance_filter = {'training': training}
    if attendance_date:
        attendance_filter['attendance_date'] = attendance_date
    
    attendance_records = Attendance.objects.filter(**attendance_filter)
    
    # Create a dictionary of student attendance
    attendance_data = {}
    for record in attendance_records:
        attendance_data[record.student_id] = record.status
    
    # Prepare data for response
    student_data = []
    for student in students:
        student_data.append({
            'id': student.applicant.id,
            'name': student.applicant.get_full_name() or student.applicant.username,
            'status': attendance_data.get(student.applicant.id, '')
        })
    
    # Calculate attendance counts for the specific date
    attendance_counts = calculate_attendance_counts(training, attendance_date)
    
    return JsonResponse({
        'training': {
            'id': training.id,
            'name': training.program_name,
            'date': training.start_date.strftime('%Y-%m-%d'),
            'time': training.task_time.strftime('%H:%M') if training.task_time else '09:00',
            'end_time': training.end_time.strftime('%H:%M') if training.end_time else '10:00',
        },
        'students': student_data,
        'counts': attendance_counts,
        'target_date': target_date  # Include target date in response
    })

@login_required
def training_management(request):
    if request.method == 'POST':
        form = TrainingForm(request.POST)
        if form.is_valid():
            training = form.save(commit=False)
            training.trainer = request.user
            training.save()
            
            print(f"✅ Training saved: {training.program_name}")
            print(f"✅ Start date: {training.start_date}")
            print(f"✅ End date: {training.end_date}")  # Debug line
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'training': {
                        'id': training.id,
                        'program_name': training.program_name,
                        'start_date': training.start_date.strftime('%Y-%m-%d'),
                        'end_date': training.end_date.strftime('%Y-%m-%d') if training.end_date else '',  # ✅ Include end_date
                        'task_time': training.task_time.strftime('%H:%M') if training.task_time else '09:00',
                        'end_time': training.end_time.strftime('%H:%M') if training.end_time else '10:00',
                        'room_lab': training.room_lab,
                        'trainer_name': request.user.get_full_name() or request.user.username,
                        'category': training.category or 'activity',
                        'description': training.description or '',
                    }
                })
            
            return redirect('Dashboard_trainor')
        else:
            print(f"❌ Form errors: {form.errors}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
    else:
        form = TrainingForm()

    # Load trainings
    all_trainings = Training.objects.select_related('trainer').all().order_by('start_date')
    my_trainings = Training.objects.filter(trainer=request.user).order_by('start_date')
    
    # Get approved applicants with attendance summary
    approved_applicants = ApprovedApplicant.objects.filter(program__trainer=request.user)
    
    # Add attendance summary for each student
    for applicant in approved_applicants:
        total_present = Attendance.objects.filter(
            student=applicant.applicant,
            training__trainer=request.user,
            status='present'
        ).count()
        
        total_absent = Attendance.objects.filter(
            student=applicant.applicant,
            training__trainer=request.user,
            status='missed'
        ).count()
        
        applicant.total_present = total_present
        applicant.total_absent = total_absent
        applicant.total_sessions = my_trainings.count()

    context = {
        'form': form,
        'trainings': my_trainings,
        'all_trainings': all_trainings,
        'my_trainings': my_trainings,
        'approvedapplicant': approved_applicants,
        'trainer_profile': {'user': request.user},
    }
    
    return render(request, 'Dashboard_trainor.html', context)



@csrf_exempt
@require_POST
@login_required
def add_task(request):
    try:
        data = json.loads(request.body)
        task_name = data.get('task_name')
        task_id = data.get('task_id')
        
        if not task_name or not task_id:
            return JsonResponse({'success': False, 'error': 'Task name and ID are required'})
        
        # Create the task
        task = Task.objects.create(
            name=task_name,
            task_id=task_id,
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'task_database_id': task.id,
            'message': 'Task created successfully'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_POST
@login_required
def delete_task(request):
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        
        if not task_id:
            return JsonResponse({'success': False, 'error': 'Task ID is required'})
        
        # Delete the task and all related completions
        task = Task.objects.get(task_id=task_id, created_by=request.user)
        task.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Task deleted successfully'
        })
        
    except Task.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_POST
@login_required
def save_task_completion(request):
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        task_id = data.get('task_id')
        is_completed = data.get('is_completed', False)
        
        if not student_id or not task_id:
            return JsonResponse({'success': False, 'error': 'Student ID and Task ID are required'})
        
        # Get the task and student
        task = Task.objects.get(task_id=task_id)
        student = Applicant.objects.get(id=student_id)
        
        # Update or create task completion
        completion, created = TaskCompletion.objects.update_or_create(
            task=task,
            student=student,
            defaults={'is_completed': is_completed}
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Task completion saved successfully'
        })
        
    except (Task.DoesNotExist, Applicant.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Task or Student not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Competency Management Views
@csrf_exempt
@require_POST
@login_required
def save_competency_state(request):
    """Save checkbox state for a trainee's competency"""
    try:
        data = json.loads(request.body)
        trainee_id = data.get('trainee_id')
        program_id = data.get('program_id')
        competency_type = data.get('competency_type')  # 'basic', 'common', or 'core'
        competency_index = data.get('competency_index')  # Index of the checkbox
        is_checked = data.get('is_checked', False)
        
        if not trainee_id or not program_id or not competency_type or competency_index is None:
            return JsonResponse({'success': False, 'error': 'Missing required parameters'})
        
        # Get or create the competency record
        from .models import ApplicantCompetencies
        trainee = Applicant.objects.get(id=trainee_id)
        program = Programs.objects.get(id=program_id)
        
        competency, created = ApplicantCompetencies.objects.get_or_create(
            applicant=trainee,
            program=program
        )
        
        # Update the specific competency checkbox state
        competency_index_str = str(competency_index)
        if competency_type == 'basic':
            competency.basic_competencies[competency_index_str] = is_checked
        elif competency_type == 'common':
            competency.common_competencies[competency_index_str] = is_checked
        elif competency_type == 'core':
            competency.core_competencies[competency_index_str] = is_checked
        else:
            return JsonResponse({'success': False, 'error': 'Invalid competency type'})
        
        # Save will automatically calculate percentages via the model's save method
        competency.save()
        
        # Update the ApprovedApplicant progress field so it persists on page reload
        try:
            approved = ApprovedApplicant.objects.get(applicant=trainee, program=program)
            approved.progress = int(competency.overall_percentage)
            approved.save()
        except ApprovedApplicant.DoesNotExist:
            # Try ApprovedWalkIn if ApprovedApplicant doesn't exist
            try:
                approved_walkin = ApprovedWalkIn.objects.get(applicant=trainee, program=program)
                approved_walkin.progress = int(competency.overall_percentage)
                approved_walkin.save()
            except ApprovedWalkIn.DoesNotExist:
                pass
        
        return JsonResponse({
            'success': True,
            'message': 'Competency state saved successfully',
            'basic_percentage': float(competency.basic_percentage),
            'common_percentage': float(competency.common_percentage),
            'core_percentage': float(competency.core_percentage),
            'overall_percentage': float(competency.overall_percentage)
        })
        
    except (Applicant.DoesNotExist, Programs.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Trainee or Program not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@login_required
def get_competency_states(request):
    """Get all competency states for trainees in a program"""
    try:
        program_id = request.GET.get('program_id')
        
        if not program_id:
            return JsonResponse({'success': False, 'error': 'Program ID is required'})
        
        from .models import ApplicantCompetencies
        program = Programs.objects.get(id=program_id)
        
        # Get all competency records for this program
        competencies = ApplicantCompetencies.objects.filter(program=program)
        
        # Build response data
        data = {}
        for comp in competencies:
            data[str(comp.applicant.id)] = {
                'basic_competencies': comp.basic_competencies,
                'common_competencies': comp.common_competencies,
                'core_competencies': comp.core_competencies,
                'basic_percentage': float(comp.basic_percentage),
                'common_percentage': float(comp.common_percentage),
                'core_percentage': float(comp.core_percentage),
                'overall_percentage': float(comp.overall_percentage)
            }
        
        return JsonResponse({
            'success': True,
            'competencies': data
        })
        
    except Programs.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Program not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Additional view to get attendance summary for a specific training
@login_required
def get_attendance_summary(request, training_id):
    training = get_object_or_404(Training, id=training_id)
    
    # Get target date for multi-day training
    target_date = request.GET.get('target_date')
    attendance_date = None
    if target_date:
        from datetime import datetime
        attendance_date = datetime.strptime(target_date, '%Y-%m-%d').date()
    
    counts = calculate_attendance_counts(training, attendance_date)
    
    return JsonResponse({
        'success': True,
        'training_id': training_id,
        'training_name': training.program_name,
        'counts': counts
    })

# Additional view to get attendance summary for a specific student across all trainings
@login_required
def get_student_attendance_summary(request, student_id):
    """Get attendance summary for a specific student across all trainings"""
    try:
        student = get_object_or_404(Applicant, id=student_id)
        
        # Get all trainings for this trainer
        trainings = Training.objects.filter(trainer=request.user)
        
        # Count present and absent for this student
        total_present = Attendance.objects.filter(
            student=student,
            training__trainer=request.user,
            status='present'
        ).count()
        
        total_absent = Attendance.objects.filter(
            student=student,
            training__trainer=request.user,
            status='missed'
        ).count()
        
        total_sessions = trainings.count()
        not_marked = total_sessions - (total_present + total_absent)
        
        return JsonResponse({
            'success': True,
            'student_id': student_id,
            'student_name': student.get_full_name() or student.username,
            'total_present': total_present,
            'total_absent': total_absent,
            'total_sessions': total_sessions,
            'not_marked': not_marked
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})



@login_required
def edit_training(request, training_id):
    """Edit existing training"""
    training = get_object_or_404(Training, id=training_id)
    
    if request.method == 'POST':
        form = TrainingForm(request.POST, instance=training)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('training_management')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    
    return redirect('Dashboard_trainor')

@login_required
def delete_training(request, training_id):
    """Delete training"""
    training = get_object_or_404(Training, id=training_id)
    
    if request.method == 'POST':
        training.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('training_management')
    
    return redirect('Dashboard_trainor')

# Add view to get training data for editing
@login_required
def get_training_data(request, training_id):
    training = get_object_or_404(Training, id=training_id)
    
    return JsonResponse({
        'id': training.id,
        'program_name': training.program_name,
        'start_date': training.start_date.strftime('%Y-%m-%d'),
        'room_lab': training.room_lab,
        'trainer_id': training.trainer.id,
    })


from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.db import transaction
from .models import EmployerProfile
from django.views.decorators.csrf import csrf_protect

User = get_user_model()

def employer_signup(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        contact_person = request.POST.get('contact_person')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Basic validation here (add your own as needed)
        if not (company_name and contact_person and email and password):
            # Return with error messages
            return render(request, 'employer-signup.html', {'error': 'Please fill all fields'})

        # Use atomic transaction to ensure both save or none
        try:
            with transaction.atomic():
                # Create the user - username can be email or company_name or whatever unique id you want
                user = User.objects.create(
                    username=email,  # or another unique identifier
                    email=email,
                    password=make_password(password),  # hash the password properly
                    is_active=True  # or whatever flags you want
                )

                # Create EmployerProfile for this user
                employer_profile = EmployerProfile.objects.create(
                    user=user,
                    full_name=contact_person,
                    # add other fields here if needed, e.g. company_name as well
                )
                
            # Redirect or respond after success
            return redirect('Employer_login')  # or wherever you want

        except Exception as e:
            # Handle exceptions or display errors
            return render(request, 'employer-signup.html', {'error': str(e)})

    else:
        # For GET requests, show the signup form
        return render(request, 'employer-signup.html')



def login_view(request):
    """Simple login view to redirect after signup"""
    if request.method == 'POST':
        # Handle login logic here
        pass
    
    # Get success message from signup
    signup_message = request.GET.get('message', '')
    if signup_message:
        messages.success(request, signup_message)
    
    return render(request, 'Login.html')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Django's authenticate expects username, but we're using email as username
        user = authenticate(username=email, password=password)
        
        if user is not None:
            # Check if user is an employer
            if user.groups.filter(name='Employer').exists():
                login(request, user)
                return redirect('dashboard')  # Redirect to employer dashboard
            else:
                messages.error(request, "This account doesn't have employer access.")
        else:
            messages.error(request, "Invalid email or password.")
    
    return render(request, 'Login.html')

# Add these views to your existing views.py file

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import json

@login_required
def get_notifications(request):
    """API endpoint to get notifications for the current user"""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:10]
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M'),
            'sender_name': notification.sender.get_full_name() if notification.sender else 'System'
        })
    
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': unread_count
    })

@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    try:
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_POST
def send_application_notification_view(request):
    """Send notification when admin wants to notify an applicant"""
    try:
        data = json.loads(request.body)
        application_id = data.get('application_id')
        username = data.get('username')
        
        # Get the application
        application = get_object_or_404(ProgramApplication, id=application_id)
        
        # Create notification
        Notification.objects.create(
            recipient=application.applicant,
            sender=request.user,
            notification_type='admin_message',
            title=f"Update on your {application.program.program_name} application",
            message=f"Hello {username}, there's an update regarding your application for {application.program.program_name}. Please check your dashboard for more details."
        )
        
        return JsonResponse({'success': True, 'message': 'Notification sent successfully'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Update your existing apply_program view to create notifications
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Programs, ProgramApplication, Learner_Profile, Notification


@login_required
def apply_program(request, program_id):
    program = get_object_or_404(Programs, id=program_id)
    user = request.user

    # Count how many ACTIVE (not declined) applications the user has
    active_application_count = ProgramApplication.objects.filter(
        applicant=user
    ).exclude(status='Declined').count()

    # Enforce application limit
    if active_application_count >= 2:
        messages.error(request, "You have reached the maximum of 2 program slots.")
        return redirect('Dashboard')

    # Check if already applied to this program
    already_applied = ProgramApplication.objects.filter(applicant=user, program=program).exists()
    if already_applied:
        messages.info(request, f"You already applied for {program.program_name}.")
        return redirect('Dashboard')

    # Create application - applications accepted anytime
    application = ProgramApplication.objects.create(applicant=user, program=program)
    
    # Determine which batch they'll be assigned to when approved
    from .enrollment_validation import is_enrollment_active, get_enrollment_info
    is_active, enrollment_message, event = is_enrollment_active()
    enrollment_info = get_enrollment_info()
    
    if is_active:
        batch_message = f"Your application will be reviewed for {enrollment_info['batch_display']} enrollment."
    else:
        # Application submitted outside enrollment - will be assigned to next batch
        batch_cycle = BatchCycle.get_active_cycle()
        # Get next batch
        next_batch = {'1': '2', '2': '3', '3': '1'}.get(batch_cycle.current_batch, '1')
        batch_message = f"Enrollment is currently closed. Your application will be queued and reviewed for the next enrollment period (Batch {next_batch})."
    
    messages.success(request, f"Application submitted for {program.program_name}. {batch_message}")

    # Notify admins
    admin_users = User.objects.filter(is_superuser=True)
    for admin in admin_users:
        Notification.objects.create(
            recipient=admin,
            sender=user,
            notification_type='new_application',
            title=f"New Application: {program.program_name}",
            message=f"{user.username} has submitted a new application for {program.program_name}."
        )

    # If user has no LearnerProfile, redirect to learner_form
    has_profile = Learner_Profile.objects.filter(user=user).exists()
    if not has_profile:
        return redirect('learner_form')

    # Otherwise stay on Dashboard
    return redirect('Dashboard')



# Update your decline application view
@staff_member_required
@login_required
def decline_application(request):
    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        application = get_object_or_404(ProgramApplication, id=application_id)
        
        # Create notification for the applicant
        Notification.objects.create(
            recipient=application.applicant,
            sender=request.user,
            notification_type='rejection',
            title=f"Application Status: {application.program.program_name}",
            message=f"Thank you for your interest in {application.program.program_name}. Unfortunately, your application was not approved at this time."
        )
        
        # Delete the application
        application.delete()
        
        messages.info(request, f"Application for {application.program.program_name} has been declined.")
        return redirect('Dashboard_admin')


@staff_member_required
@login_required
def mark_incomplete_fields(request):
    """Mark specific fields as incomplete/incorrect for an application"""
    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        marked_fields = request.POST.getlist('marked_fields')
        review_notes = request.POST.get('review_notes', '')
        
        try:
            application = get_object_or_404(ProgramApplication, id=application_id)
            
            # Convert list of field names to dictionary with True values
            marked_fields_dict = {field: True for field in marked_fields}
            
            # Update the application with marked fields
            application.marked_fields = marked_fields_dict
            application.is_under_review = True
            application.review_notes = review_notes
            application.reviewed_at = timezone.now()
            application.status = 'Pending'  # Keep as pending, not declined
            application.save()
            
            # Create notification for the applicant
            field_list = ', '.join([field.replace('_', ' ').title() for field in marked_fields])
            notification_message = f"Your application for {application.program.program_name} requires corrections. "
            notification_message += f"Please review and update the following fields: {field_list}."
            if review_notes:
                notification_message += f" Admin notes: {review_notes}"
            
            Notification.objects.create(
                recipient=application.applicant,
                sender=request.user,
                notification_type='application',
                title=f"Application Review: {application.program.program_name}",
                message=notification_message
            )
            
            messages.success(request, f"Application marked for review. {application.applicant.username} has been notified to correct the marked fields.")
            return redirect('Dashboard_admin')
            
        except Exception as e:
            messages.error(request, f"Error marking fields: {str(e)}")
            return redirect('Dashboard_admin')
    
    return redirect('Dashboard_admin')


@login_required
def update_marked_fields(request):
    """Allow users to update only the fields marked as incorrect"""
    if request.method == 'POST':
        try:
            # Get the user's learner profile
            profile = Learner_Profile.objects.get(user=request.user)
            
            # Get the application that's under review
            application = ProgramApplication.objects.filter(
                applicant=request.user,
                is_under_review=True
            ).first()
            
            if not application or not application.marked_fields:
                messages.error(request, "No fields are marked for correction.")
                return redirect('Dashboard')
            
            # Update only the marked fields
            marked_fields = application.marked_fields
            updated_fields = []
            
            for field_name in marked_fields.keys():
                if field_name in request.POST:
                    new_value = request.POST.get(field_name)
                    if hasattr(profile, field_name):
                        setattr(profile, field_name, new_value)
                        updated_fields.append(field_name.replace('_', ' ').title())
            
            profile.save()
            
            if updated_fields:
                messages.success(request, f"Successfully updated: {', '.join(updated_fields)}. Please click 'Resubmit for Review' when ready.")
            else:
                messages.info(request, "No changes were made.")
            
            return redirect('Dashboard')
            
        except Learner_Profile.DoesNotExist:
            messages.error(request, "Profile not found.")
            return redirect('Dashboard')
        except Exception as e:
            messages.error(request, f"Error updating fields: {str(e)}")
            return redirect('Dashboard')
    
    return redirect('Dashboard')


@login_required
def resubmit_for_review(request):
    """User resubmits corrected information for admin review"""
    if request.method == 'POST':
        try:
            # Get the application that's under review
            application = ProgramApplication.objects.filter(
                applicant=request.user,
                is_under_review=True
            ).first()
            
            if not application:
                return JsonResponse({
                    'success': False,
                    'message': 'No application is currently under review.'
                })
            
            # Check if marked_fields exists and is not empty
            if not application.marked_fields:
                return JsonResponse({
                    'success': False,
                    'message': 'No fields are marked for correction.'
                })
            
            # Clear the marked fields and review status
            marked_field_names = list(application.marked_fields.keys())
            field_list = ', '.join([f.replace('_', ' ').title() for f in marked_field_names])
            
            application.marked_fields = {}
            application.is_under_review = False
            application.review_notes = None
            application.save()
            
            # Notify all admin users
            admin_users = Applicant.objects.filter(is_staff=True, is_active=True)
            
            notification_count = 0
            for admin in admin_users:
                Notification.objects.create(
                    recipient=admin,
                    sender=request.user,
                    notification_type='application',
                    title=f"Resubmission: {application.program.program_name}",
                    message=f"{request.user.username} has resubmitted their corrected information for review. Previously marked fields: {field_list}. Please review their profile."
                )
                notification_count += 1
            
            # Create confirmation notification for user
            Notification.objects.create(
                recipient=request.user,
                sender=request.user,
                notification_type='application',
                title="Resubmission Successful",
                message=f"Your corrected information has been resubmitted for review. The admin will review your changes and get back to you soon."
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Your corrections have been successfully resubmitted! {notification_count} admin(s) have been notified.'
            })
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Resubmit error: {error_details}")  # Log to console
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def update_status(request):
    """Update applicant status and save to ApplicantPasser if finished"""
    if request.method == 'POST':
        applicant_id = request.POST.get('applicant_id')
        status = request.POST.get('status')
        
        try:
            # Get the approved applicant record
            approved_applicant = get_object_or_404(ApprovedApplicant, id=applicant_id)
            
            # Update the status
            approved_applicant.status = status
            approved_applicant.save()
            
            # If status is 'finished', create ApplicantPasser record
            if status == 'finished':
                from .models import ApplicantPasser
                
                # Get learner profile for proper name
                try:
                    learner_profile = approved_applicant.applicant.learner_profile.first()
                    trainee_name = f"{learner_profile.last_name}, {learner_profile.first_name}"
                except:
                    trainee_name = approved_applicant.applicant.username
                
                # Check if already exists to avoid duplicates
                passer, created = ApplicantPasser.objects.get_or_create(
                    applicant=approved_applicant.applicant,
                    program=approved_applicant.program,
                    defaults={
                        'trainee_name': trainee_name,
                        'program_name': approved_applicant.program.program_name,
                        'final_progress': getattr(approved_applicant, 'progress', 0),
                        'total_present': getattr(approved_applicant, 'total_present', 0),
                        'total_absent': getattr(approved_applicant, 'total_absent', 0),
                        'enrollment_date': approved_applicant.approved_at,
                    }
                )
                
                if created:
                    messages.success(request, f"{approved_applicant.applicant.username} has been successfully moved to Applicant Passer!")
                else:
                    messages.info(request, f"{approved_applicant.applicant.username} is already in Applicant Passer.")
            
            elif status == 'dropped':
                messages.info(request, f"{approved_applicant.applicant.username} has been marked as dropped.")
            
            return redirect('Dashboard_trainor')
            
        except ApprovedApplicant.DoesNotExist:
            messages.error(request, "Applicant not found.")
            return redirect('Dashboard_trainor')
        except Exception as e:
            messages.error(request, f"Error updating status: {str(e)}")
            return redirect('Dashboard_trainor')
    
    return redirect('Dashboard_trainor')


@staff_member_required
@login_required
def add_program(request):
    if request.method == 'POST':
        try:
            program_name = request.POST.get('program_name')
            program_detail = request.POST.get('program_detail')
            program_sched = request.POST.get('program_sched')
            program_trainor = request.POST.get('program_trainor')
            program_competencies_json = request.POST.get('program_competencies')
            program_image = request.FILES.get('program_image')
            
            # Validate required fields
            if not all([program_name, program_detail, program_sched]):
                messages.error(request, "Program name, description, and schedule are required.")
                return redirect('Dashboard_admin')
            
            # Parse skills/competencies from JSON
            program_competencies = []
            if program_competencies_json:
                try:
                    import json
                    program_competencies = json.loads(program_competencies_json)
                except json.JSONDecodeError:
                    # If JSON parsing fails, treat as empty list
                    program_competencies = []
            
            # Create the program
            program = Programs.objects.create(
                program_name=program_name,
                program_detail=program_detail,
                program_sched=program_sched,
                program_trainor=program_trainor or '',
                program_competencies=program_competencies
            )
            
            # Handle image upload if provided
            if program_image:
                ProgramImage.objects.create(
                    program=program,
                    image=program_image
                )
            
            messages.success(request, f"Program '{program_name}' has been successfully added!")
            return redirect('Dashboard_admin')
            
        except Exception as e:
            messages.error(request, f"Error adding program: {str(e)}")
            return redirect('Dashboard_admin')
    
    return redirect('Dashboard_admin')

@staff_member_required
@login_required
def edit_program(request, program_id):
    if request.method == 'POST':
        try:
            program = get_object_or_404(Programs, id=program_id)
            
            program_name = request.POST.get('program_name')
            program_detail = request.POST.get('program_detail')
            program_sched = request.POST.get('program_sched')
            program_trainor = request.POST.get('program_trainor')
            program_competencies_json = request.POST.get('program_competencies')
            program_image = request.FILES.get('program_image')
            
            # Validate required fields
            if not all([program_name, program_detail, program_sched]):
                messages.error(request, "Program name, description, and schedule are required.")
                return redirect('Dashboard_admin')
            
            # Parse skills/competencies from JSON
            program_competencies = []
            if program_competencies_json:
                try:
                    import json
                    program_competencies = json.loads(program_competencies_json)
                except json.JSONDecodeError:
                    program_competencies = []
            
            # Update program fields
            program.program_name = program_name
            program.program_detail = program_detail
            program.program_sched = program_sched
            program.program_trainor = program_trainor or ''
            program.program_competencies = program_competencies
            program.save()
            
            # Handle image upload if provided
            if program_image:
                # Delete old images
                ProgramImage.objects.filter(program=program).delete()
                # Create new image
                ProgramImage.objects.create(
                    program=program,
                    image=program_image
                )
            
            messages.success(request, f"Program '{program_name}' has been successfully updated!")
            return redirect('Dashboard_admin')
            
        except Exception as e:
            messages.error(request, f"Error updating program: {str(e)}")
            return redirect('Dashboard_admin')
    
    return redirect('Dashboard_admin')

@staff_member_required
@login_required
def delete_program(request, program_id):
    """Delete a program from the database"""
    if request.method == 'POST':
        try:
            program = get_object_or_404(Programs, id=program_id)
            program_name = program.program_name
            
            # Delete associated program images first
            ProgramImage.objects.filter(program=program).delete()
            
            # Delete the program
            program.delete()
            
            messages.success(request, f"Program '{program_name}' has been successfully deleted!")
            return redirect('Dashboard_admin')
            
        except Exception as e:
            messages.error(request, f"Error deleting program: {str(e)}")
            return redirect('Dashboard_admin')
    
    return redirect('Dashboard_admin')

@login_required
def approve_walkin(request, application_id):
    """Approve a walk-in application"""
    if request.method == 'POST':
        try:
            # Get the walk-in application
            walkin_app = get_object_or_404(WalkInApplication, id=application_id)
            
            # Update status to Approved
            walkin_app.status = 'Approved'
            walkin_app.processed_at = timezone.now()
            walkin_app.save()
            
            # Create ApprovedWalkIn record
            ApprovedWalkIn.objects.create(
                applicant=walkin_app.applicant,
                program=walkin_app.program,
                walkin_application=walkin_app
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Walk-in application for {walkin_app.applicant.get_full_name()} has been approved.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error approving walk-in application: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})




# Bulk Review and Approval Functions
@staff_member_required
@login_required
@csrf_exempt
def get_bulk_review_data(request):
    """Get all applications for bulk review"""
    if request.method == 'GET':
        try:
            # Get Program Applications
            program_applications = ProgramApplication.objects.filter(status='Pending').select_related('applicant', 'program')
            program_data = []
            
            for app in program_applications:
                # Check if learner profile exists and has required documents
                try:
                    learner_profile = Learner_Profile.objects.get(user=app.applicant)
                    has_id_picture = bool(learner_profile.id_picture)
                    has_signature = bool(learner_profile.applicant_signature)
                    has_learner_profile = True
                except Learner_Profile.DoesNotExist:
                    has_id_picture = False
                    has_signature = False
                    has_learner_profile = False
                
                # Check if DMS Review already exists
                dms_review, created = DMSReview.objects.get_or_create(
                    application_type='program',
                    application_id=app.id,
                    defaults={
                        'applicant': app.applicant,
                        'program': app.program,
                        'has_id_picture': has_id_picture,
                        'has_learner_profile': has_learner_profile,
                        'has_signature': has_signature,
                        'has_required_documents': has_id_picture and has_learner_profile and has_signature,
                    }
                )
                
                program_data.append({
                    'id': app.id,
                    'applicant_name': app.applicant.get_full_name() or app.applicant.username,
                    'program_name': app.program.program_name,
                    'applied_date': app.applied_at.strftime('%Y-%m-%d'),
                    'status': dms_review.get_status_display(),
                    'has_id_picture': dms_review.has_id_picture,
                    'has_learner_profile': dms_review.has_learner_profile,
                    'has_signature': dms_review.has_signature,
                    'has_required_documents': dms_review.has_required_documents,
                    'is_complete': dms_review.is_complete,
                    'dms_review_id': dms_review.id
                })
            
            # Get Walk-in Applications
            walkin_applications = WalkInApplication.objects.filter(status='Pending').select_related('applicant', 'program')
            walkin_data = []
            
            for app in walkin_applications:
                # Check if learner profile exists and has required documents
                try:
                    learner_profile = Learner_Profile.objects.get(user=app.applicant)
                    has_id_picture = bool(learner_profile.id_picture)
                    has_signature = bool(learner_profile.applicant_signature)
                    has_learner_profile = True
                except Learner_Profile.DoesNotExist:
                    has_id_picture = False
                    has_signature = False
                    has_learner_profile = False
                
                # Check if DMS Review already exists
                dms_review, created = DMSReview.objects.get_or_create(
                    application_type='walkin',
                    application_id=app.id,
                    defaults={
                        'applicant': app.applicant,
                        'program': app.program,
                        'has_id_picture': has_id_picture,
                        'has_learner_profile': has_learner_profile,
                        'has_signature': has_signature,
                        'has_required_documents': has_id_picture and has_learner_profile and has_signature,
                    }
                )
                
                walkin_data.append({
                    'id': app.id,
                    'applicant_name': app.applicant.get_full_name() or app.applicant.username,
                    'program_name': app.program.program_name,
                    'applied_date': app.applied_at.strftime('%Y-%m-%d'),
                    'status': dms_review.get_status_display(),
                    'has_id_picture': dms_review.has_id_picture,
                    'has_learner_profile': dms_review.has_learner_profile,
                    'has_signature': dms_review.has_signature,
                    'has_required_documents': dms_review.has_required_documents,
                    'is_complete': dms_review.is_complete,
                    'dms_review_id': dms_review.id
                })
            
            # Calculate statistics
            total_applications = len(program_data) + len(walkin_data)
            ready_for_approval = sum(1 for app in program_data + walkin_data if app['is_complete'])
            pending_review = total_applications - ready_for_approval
            
            return JsonResponse({
                'success': True,
                'program_applications': program_data,
                'walkin_applications': walkin_data,
                'statistics': {
                    'total_applications': total_applications,
                    'ready_for_approval': ready_for_approval,
                    'pending_review': pending_review
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})




@staff_member_required
@login_required
@csrf_exempt
def process_bulk_review(request):
    """Process selected applications for bulk review"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_reviews = data.get('selected_reviews', [])
            
            approved_count = 0
            incomplete_count = 0
            
            for review_id in selected_reviews:
                try:
                    dms_review = DMSReview.objects.get(id=review_id)
                    
                    # Update review status based on completeness
                    if dms_review.is_complete:
                        dms_review.status = 'ready_for_approval'
                        dms_review.reviewed_at = timezone.now()
                        dms_review.reviewed_by = request.user
                        dms_review.save()
                        
                        # Create DMSApproval entry for complete applications
                        DMSApproval.objects.get_or_create(
                            dms_review=dms_review,
                            defaults={
                                'applicant': dms_review.applicant,
                                'program': dms_review.program,
                                'application_type': dms_review.application_type,
                                'approved_by': request.user
                            }
                        )
                        approved_count += 1
                    else:
                        dms_review.status = 'incomplete'
                        dms_review.reviewed_at = timezone.now()
                        dms_review.reviewed_by = request.user
                        dms_review.save()
                        incomplete_count += 1
                        
                except DMSReview.DoesNotExist:
                    continue
            
            return JsonResponse({
                'success': True,
                'message': f'Review completed: {approved_count} applications ready for approval, {incomplete_count} applications marked as incomplete.',
                'approved_count': approved_count,
                'incomplete_count': incomplete_count
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})




@staff_member_required
@login_required
@csrf_exempt
def get_bulk_approval_data(request):
    """Get applications ready for bulk approval"""
    if request.method == 'GET':
        try:
            # Get all DMSApproval entries that are ready for final approval
            dms_approvals = DMSApproval.objects.filter(
                status='pending_final_approval'
            ).select_related('applicant', 'program', 'dms_review')
            
            approval_data = []
            for approval in dms_approvals:
                approval_data.append({
                    'id': approval.id,
                    'applicant_name': approval.applicant.get_full_name() or approval.applicant.username,
                    'program_name': approval.program.program_name,
                    'application_type': approval.get_application_type_display(),
                    'review_date': approval.dms_review.reviewed_at.strftime('%Y-%m-%d %H:%M') if approval.dms_review.reviewed_at else 'N/A',
                    'status': approval.get_status_display()
                })
            
            return JsonResponse({
                'success': True,
                'approval_applications': approval_data,
                'statistics': {
                    'ready_for_approval': len(approval_data)
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})




@staff_member_required
@login_required
@csrf_exempt
def process_bulk_approval(request):
    """Process selected applications for bulk approval"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_approvals = data.get('selected_approvals', [])
            
            approved_count = 0
            
            # Get the current batch cycle
            from datetime import datetime
            batch_cycle = BatchCycle.objects.filter(is_active=True).first()
            current_year = datetime.now().year
            
            # Create default batch cycle if none exists
            if not batch_cycle:
                batch_cycle = BatchCycle.objects.create(
                    current_batch='1',
                    cycle_state='waiting_enrollment',
                    is_active=True
                )
            
            
            # Get the current batch cycle
            from datetime import datetime
            batch_cycle = BatchCycle.objects.filter(is_active=True).first()
            current_year = datetime.now().year
            
            # Create default batch cycle if none exists
            if not batch_cycle:
                batch_cycle = BatchCycle.objects.create(
                    current_batch='1',
                    cycle_state='waiting_enrollment',
                    is_active=True
                )
            
            
            for approval_id in selected_approvals:
                try:
                    dms_approval = DMSApproval.objects.get(id=approval_id)
                    
                    # Get the original application
                    original_app = dms_approval.dms_review.get_original_application()
                    
                    if original_app:
                        if dms_approval.application_type == 'program':
                            # Use existing approve_application logic
                            ApprovedApplicant.objects.create(
                                applicant=original_app.applicant,
                                program=original_app.program,
                                batch_number=batch_cycle.current_batch,
                                enrollment_year=current_year
                            )
                            
                            # Create notification
                            Notification.objects.create(
                                recipient=original_app.applicant,
                                sender=request.user,
                                notification_type='approval',
                                title=f"Application Approved: {original_app.program.program_name}",
                                message=f"Congratulations! Your application for {original_app.program.program_name} has been approved. You are enrolled in Batch {batch_cycle.current_batch}, Year {current_year}."
                            )
                            
                            # Delete original application
                            original_app.delete()
                            
                        elif dms_approval.application_type == 'walkin':
                            # Create ApprovedWalkIn entry
                            ApprovedWalkIn.objects.create(
                                applicant=original_app.applicant,
                                program=original_app.program,
                                original_application=original_app,
                                approved_by=request.user,
                                batch_number=batch_cycle.current_batch,
                                enrollment_year=current_year
                            )
                            
                            # Create notification
                            Notification.objects.create(
                                recipient=original_app.applicant,
                                sender=request.user,
                                notification_type='approval',
                                title=f"Walk-in Application Approved: {original_app.program.program_name}",
                                message=f"Your walk-in application for {original_app.program.program_name} has been approved! You are enrolled in Batch {batch_cycle.current_batch}, Year {current_year}."
                            )
                            
                            # Update original application status
                            original_app.status = 'Approved'
                            original_app.processed_by = request.user
                            original_app.processed_at = timezone.now()
                            original_app.save()
                        
                        # Update DMS Approval status
                        dms_approval.status = 'approved'
                        dms_approval.final_approved_at = timezone.now()
                        dms_approval.final_approved_by = request.user
                        dms_approval.save()
                        
                        approved_count += 1
                        
                except DMSApproval.DoesNotExist:
                    continue
                except Exception as e:
                    print(f"Error processing approval {approval_id}: {str(e)}")
                    continue
            
            return JsonResponse({
                'success': True,
                'message': f'Bulk approval completed: {approved_count} applications approved successfully.',
                'approved_count': approved_count
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})



@login_required
def decline_walkin(request, application_id):
    """Decline a walk-in application"""
    if request.method == 'POST':
        try:
            # Get the walk-in application
            walkin_app = get_object_or_404(WalkInApplication, id=application_id)
            
            # Get decline reason from request
            decline_reason = request.POST.get('reason', 'No reason provided')
            
            # Update status to Declined
            walkin_app.status = 'Declined'
            walkin_app.decline_reason = decline_reason
            walkin_app.processed_at = timezone.now()
            walkin_app.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Walk-in application for {walkin_app.applicant.get_full_name()} has been declined.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error declining walk-in application: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})




# Bulk Review and Approval Functions
@staff_member_required
@login_required
@csrf_exempt
def get_bulk_review_data(request):
    """Get all applications for bulk review"""
    if request.method == 'GET':
        try:
            # Get Program Applications
            program_applications = ProgramApplication.objects.filter(status='Pending').select_related('applicant', 'program')
            program_data = []
            
            for app in program_applications:
                # Check if learner profile exists and has required documents
                try:
                    learner_profile = Learner_Profile.objects.get(user=app.applicant)
                    has_id_picture = bool(learner_profile.id_picture)
                    has_signature = bool(learner_profile.applicant_signature)
                    has_learner_profile = True
                except Learner_Profile.DoesNotExist:
                    has_id_picture = False
                    has_signature = False
                    has_learner_profile = False
                
                # Check if DMS Review already exists
                dms_review, created = DMSReview.objects.get_or_create(
                    application_type='program',
                    application_id=app.id,
                    defaults={
                        'applicant': app.applicant,
                        'program': app.program,
                        'has_id_picture': has_id_picture,
                        'has_learner_profile': has_learner_profile,
                        'has_signature': has_signature,
                        'has_required_documents': has_id_picture and has_learner_profile and has_signature,
                    }
                )
                
                program_data.append({
                    'id': app.id,
                    'applicant_name': app.applicant.get_full_name() or app.applicant.username,
                    'program_name': app.program.program_name,
                    'applied_date': app.applied_at.strftime('%Y-%m-%d'),
                    'status': dms_review.get_status_display(),
                    'has_id_picture': dms_review.has_id_picture,
                    'has_learner_profile': dms_review.has_learner_profile,
                    'has_signature': dms_review.has_signature,
                    'has_required_documents': dms_review.has_required_documents,
                    'is_complete': dms_review.is_complete,
                    'dms_review_id': dms_review.id
                })
            
            # Get Walk-in Applications
            walkin_applications = WalkInApplication.objects.filter(status='Pending').select_related('applicant', 'program')
            walkin_data = []
            
            for app in walkin_applications:
                # Check if learner profile exists and has required documents
                try:
                    learner_profile = Learner_Profile.objects.get(user=app.applicant)
                    has_id_picture = bool(learner_profile.id_picture)
                    has_signature = bool(learner_profile.applicant_signature)
                    has_learner_profile = True
                except Learner_Profile.DoesNotExist:
                    has_id_picture = False
                    has_signature = False
                    has_learner_profile = False
                
                # Check if DMS Review already exists
                dms_review, created = DMSReview.objects.get_or_create(
                    application_type='walkin',
                    application_id=app.id,
                    defaults={
                        'applicant': app.applicant,
                        'program': app.program,
                        'has_id_picture': has_id_picture,
                        'has_learner_profile': has_learner_profile,
                        'has_signature': has_signature,
                        'has_required_documents': has_id_picture and has_learner_profile and has_signature,
                    }
                )
                
                walkin_data.append({
                    'id': app.id,
                    'applicant_name': app.applicant.get_full_name() or app.applicant.username,
                    'program_name': app.program.program_name,
                    'applied_date': app.applied_at.strftime('%Y-%m-%d'),
                    'status': dms_review.get_status_display(),
                    'has_id_picture': dms_review.has_id_picture,
                    'has_learner_profile': dms_review.has_learner_profile,
                    'has_signature': dms_review.has_signature,
                    'has_required_documents': dms_review.has_required_documents,
                    'is_complete': dms_review.is_complete,
                    'dms_review_id': dms_review.id
                })
            
            # Calculate statistics
            total_applications = len(program_data) + len(walkin_data)
            ready_for_approval = sum(1 for app in program_data + walkin_data if app['is_complete'])
            pending_review = total_applications - ready_for_approval
            
            return JsonResponse({
                'success': True,
                'program_applications': program_data,
                'walkin_applications': walkin_data,
                'statistics': {
                    'total_applications': total_applications,
                    'ready_for_approval': ready_for_approval,
                    'pending_review': pending_review
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})




@staff_member_required
@login_required
@csrf_exempt
def process_bulk_review(request):
    """Process selected applications for bulk review"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_reviews = data.get('selected_reviews', [])
            
            approved_count = 0
            incomplete_count = 0
            
            for review_id in selected_reviews:
                try:
                    dms_review = DMSReview.objects.get(id=review_id)
                    
                    # Update review status based on completeness
                    if dms_review.is_complete:
                        dms_review.status = 'ready_for_approval'
                        dms_review.reviewed_at = timezone.now()
                        dms_review.reviewed_by = request.user
                        dms_review.save()
                        
                        # Create DMSApproval entry for complete applications
                        DMSApproval.objects.get_or_create(
                            dms_review=dms_review,
                            defaults={
                                'applicant': dms_review.applicant,
                                'program': dms_review.program,
                                'application_type': dms_review.application_type,
                                'approved_by': request.user
                            }
                        )
                        approved_count += 1
                    else:
                        dms_review.status = 'incomplete'
                        dms_review.reviewed_at = timezone.now()
                        dms_review.reviewed_by = request.user
                        dms_review.save()
                        incomplete_count += 1
                        
                except DMSReview.DoesNotExist:
                    continue
            
            return JsonResponse({
                'success': True,
                'message': f'Review completed: {approved_count} applications ready for approval, {incomplete_count} applications marked as incomplete.',
                'approved_count': approved_count,
                'incomplete_count': incomplete_count
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})




@staff_member_required
@login_required
@csrf_exempt
def get_bulk_approval_data(request):
    """Get applications ready for bulk approval"""
    if request.method == 'GET':
        try:
            # Get all DMSApproval entries that are ready for final approval
            dms_approvals = DMSApproval.objects.filter(
                status='pending_final_approval'
            ).select_related('applicant', 'program', 'dms_review')
            
            approval_data = []
            for approval in dms_approvals:
                approval_data.append({
                    'id': approval.id,
                    'applicant_name': approval.applicant.get_full_name() or approval.applicant.username,
                    'program_name': approval.program.program_name,
                    'application_type': approval.get_application_type_display(),
                    'review_date': approval.dms_review.reviewed_at.strftime('%Y-%m-%d %H:%M') if approval.dms_review.reviewed_at else 'N/A',
                    'status': approval.get_status_display()
                })
            
            return JsonResponse({
                'success': True,
                'approval_applications': approval_data,
                'statistics': {
                    'ready_for_approval': len(approval_data)
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})




@staff_member_required
@login_required
@csrf_exempt
def process_bulk_approval(request):
    """Process selected applications for bulk approval"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_approvals = data.get('selected_approvals', [])
            
            approved_count = 0
            
            # Get the current batch cycle
            from datetime import datetime
            batch_cycle = BatchCycle.objects.filter(is_active=True).first()
            current_year = datetime.now().year
            
            # Create default batch cycle if none exists
            if not batch_cycle:
                batch_cycle = BatchCycle.objects.create(
                    current_batch='1',
                    cycle_state='waiting_enrollment',
                    is_active=True
                )
            
            
            # Get the current batch cycle
            from datetime import datetime
            batch_cycle = BatchCycle.objects.filter(is_active=True).first()
            current_year = datetime.now().year
            
            # Create default batch cycle if none exists
            if not batch_cycle:
                batch_cycle = BatchCycle.objects.create(
                    current_batch='1',
                    cycle_state='waiting_enrollment',
                    is_active=True
                )
            
            
            for approval_id in selected_approvals:
                try:
                    dms_approval = DMSApproval.objects.get(id=approval_id)
                    
                    # Get the original application
                    original_app = dms_approval.dms_review.get_original_application()
                    
                    if original_app:
                        if dms_approval.application_type == 'program':
                            # Use existing approve_application logic
                            ApprovedApplicant.objects.create(
                                applicant=original_app.applicant,
                                program=original_app.program,
                                batch_number=batch_cycle.current_batch,
                                enrollment_year=current_year
                            )
                            
                            # Create notification
                            Notification.objects.create(
                                recipient=original_app.applicant,
                                sender=request.user,
                                notification_type='approval',
                                title=f"Application Approved: {original_app.program.program_name}",
                                message=f"Congratulations! Your application for {original_app.program.program_name} has been approved. You are enrolled in Batch {batch_cycle.current_batch}, Year {current_year}."
                            )
                            
                            # Delete original application
                            original_app.delete()
                            
                        elif dms_approval.application_type == 'walkin':
                            # Create ApprovedWalkIn entry
                            ApprovedWalkIn.objects.create(
                                applicant=original_app.applicant,
                                program=original_app.program,
                                original_application=original_app,
                                approved_by=request.user,
                                batch_number=batch_cycle.current_batch,
                                enrollment_year=current_year
                            )
                            
                            # Create notification
                            Notification.objects.create(
                                recipient=original_app.applicant,
                                sender=request.user,
                                notification_type='approval',
                                title=f"Walk-in Application Approved: {original_app.program.program_name}",
                                message=f"Your walk-in application for {original_app.program.program_name} has been approved! You are enrolled in Batch {batch_cycle.current_batch}, Year {current_year}."
                            )
                            
                            # Update original application status
                            original_app.status = 'Approved'
                            original_app.processed_by = request.user
                            original_app.processed_at = timezone.now()
                            original_app.save()
                        
                        # Update DMS Approval status
                        dms_approval.status = 'approved'
                        dms_approval.final_approved_at = timezone.now()
                        dms_approval.final_approved_by = request.user
                        dms_approval.save()
                        
                        approved_count += 1
                        
                except DMSApproval.DoesNotExist:
                    continue
                except Exception as e:
                    print(f"Error processing approval {approval_id}: {str(e)}")
                    continue
            
            return JsonResponse({
                'success': True,
                'message': f'Bulk approval completed: {approved_count} applications approved successfully.',
                'approved_count': approved_count
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})



@login_required
def decline_walkin(request, application_id):
    """Decline a walk-in application"""
    if request.method == 'POST':
        try:
            # Get the walk-in application
            walkin_app = get_object_or_404(WalkInApplication, id=application_id)
            
            # Get decline reason from request
            decline_reason = request.POST.get('reason', 'No reason provided')
            
            # Update status to Declined
            walkin_app.status = 'Declined'
            walkin_app.decline_reason = decline_reason
            walkin_app.processed_at = timezone.now()
            walkin_app.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Walk-in application for {walkin_app.applicant.get_full_name()} has been declined.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error declining walk-in application: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})




# Bulk Review and Approval Functions
@staff_member_required
@login_required
@csrf_exempt
def get_bulk_review_data(request):
    """Get all applications for bulk review"""
    if request.method == 'GET':
        try:
            # Get Program Applications
            program_applications = ProgramApplication.objects.filter(status='Pending').select_related('applicant', 'program')
            program_data = []
            
            for app in program_applications:
                # Check if learner profile exists and has required documents
                try:
                    learner_profile = Learner_Profile.objects.get(user=app.applicant)
                    has_id_picture = bool(learner_profile.id_picture)
                    has_signature = bool(learner_profile.applicant_signature)
                    has_learner_profile = True
                except Learner_Profile.DoesNotExist:
                    has_id_picture = False
                    has_signature = False
                    has_learner_profile = False
                
                # Check if DMS Review already exists
                dms_review, created = DMSReview.objects.get_or_create(
                    application_type='program',
                    application_id=app.id,
                    defaults={
                        'applicant': app.applicant,
                        'program': app.program,
                        'has_id_picture': has_id_picture,
                        'has_learner_profile': has_learner_profile,
                        'has_signature': has_signature,
                        'has_required_documents': has_id_picture and has_learner_profile and has_signature,
                    }
                )
                
                program_data.append({
                    'id': app.id,
                    'applicant_name': app.applicant.get_full_name() or app.applicant.username,
                    'program_name': app.program.program_name,
                    'applied_date': app.applied_at.strftime('%Y-%m-%d'),
                    'status': dms_review.get_status_display(),
                    'has_id_picture': dms_review.has_id_picture,
                    'has_learner_profile': dms_review.has_learner_profile,
                    'has_signature': dms_review.has_signature,
                    'has_required_documents': dms_review.has_required_documents,
                    'is_complete': dms_review.is_complete,
                    'dms_review_id': dms_review.id
                })
            
            # Get Walk-in Applications
            walkin_applications = WalkInApplication.objects.filter(status='Pending').select_related('applicant', 'program')
            walkin_data = []
            
            for app in walkin_applications:
                # Check if learner profile exists and has required documents
                try:
                    learner_profile = Learner_Profile.objects.get(user=app.applicant)
                    has_id_picture = bool(learner_profile.id_picture)
                    has_signature = bool(learner_profile.applicant_signature)
                    has_learner_profile = True
                except Learner_Profile.DoesNotExist:
                    has_id_picture = False
                    has_signature = False
                    has_learner_profile = False
                
                # Check if DMS Review already exists
                dms_review, created = DMSReview.objects.get_or_create(
                    application_type='walkin',
                    application_id=app.id,
                    defaults={
                        'applicant': app.applicant,
                        'program': app.program,
                        'has_id_picture': has_id_picture,
                        'has_learner_profile': has_learner_profile,
                        'has_signature': has_signature,
                        'has_required_documents': has_id_picture and has_learner_profile and has_signature,
                    }
                )
                
                walkin_data.append({
                    'id': app.id,
                    'applicant_name': app.applicant.get_full_name() or app.applicant.username,
                    'program_name': app.program.program_name,
                    'applied_date': app.applied_at.strftime('%Y-%m-%d'),
                    'status': dms_review.get_status_display(),
                    'has_id_picture': dms_review.has_id_picture,
                    'has_learner_profile': dms_review.has_learner_profile,
                    'has_signature': dms_review.has_signature,
                    'has_required_documents': dms_review.has_required_documents,
                    'is_complete': dms_review.is_complete,
                    'dms_review_id': dms_review.id
                })
            
            # Calculate statistics
            total_applications = len(program_data) + len(walkin_data)
            ready_for_approval = sum(1 for app in program_data + walkin_data if app['is_complete'])
            pending_review = total_applications - ready_for_approval
            
            return JsonResponse({
                'success': True,
                'program_applications': program_data,
                'walkin_applications': walkin_data,
                'statistics': {
                    'total_applications': total_applications,
                    'ready_for_approval': ready_for_approval,
                    'pending_review': pending_review
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})




@staff_member_required
@login_required
@csrf_exempt
def process_bulk_review(request):
    """Process selected applications for bulk review"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_reviews = data.get('selected_reviews', [])
            
            approved_count = 0
            incomplete_count = 0
            
            for review_id in selected_reviews:
                try:
                    dms_review = DMSReview.objects.get(id=review_id)
                    
                    # Update review status based on completeness
                    if dms_review.is_complete:
                        dms_review.status = 'ready_for_approval'
                        dms_review.reviewed_at = timezone.now()
                        dms_review.reviewed_by = request.user
                        dms_review.save()
                        
                        # Create DMSApproval entry for complete applications
                        DMSApproval.objects.get_or_create(
                            dms_review=dms_review,
                            defaults={
                                'applicant': dms_review.applicant,
                                'program': dms_review.program,
                                'application_type': dms_review.application_type,
                                'approved_by': request.user
                            }
                        )
                        approved_count += 1
                    else:
                        dms_review.status = 'incomplete'
                        dms_review.reviewed_at = timezone.now()
                        dms_review.reviewed_by = request.user
                        dms_review.save()
                        incomplete_count += 1
                        
                except DMSReview.DoesNotExist:
                    continue
            
            return JsonResponse({
                'success': True,
                'message': f'Review completed: {approved_count} applications ready for approval, {incomplete_count} applications marked as incomplete.',
                'approved_count': approved_count,
                'incomplete_count': incomplete_count
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})




@staff_member_required
@login_required
@csrf_exempt
def get_bulk_approval_data(request):
    """Get applications ready for bulk approval"""
    if request.method == 'GET':
        try:
            # Get all DMSApproval entries that are ready for final approval
            dms_approvals = DMSApproval.objects.filter(
                status='pending_final_approval'
            ).select_related('applicant', 'program', 'dms_review')
            
            approval_data = []
            for approval in dms_approvals:
                approval_data.append({
                    'id': approval.id,
                    'applicant_name': approval.applicant.get_full_name() or approval.applicant.username,
                    'program_name': approval.program.program_name,
                    'application_type': approval.get_application_type_display(),
                    'review_date': approval.dms_review.reviewed_at.strftime('%Y-%m-%d %H:%M') if approval.dms_review.reviewed_at else 'N/A',
                    'status': approval.get_status_display()
                })
            
            return JsonResponse({
                'success': True,
                'approval_applications': approval_data,
                'statistics': {
                    'ready_for_approval': len(approval_data)
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})




@staff_member_required
@login_required
@csrf_exempt
def process_bulk_approval(request):
    """Process selected applications for bulk approval"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_approvals = data.get('selected_approvals', [])
            
            approved_count = 0
            
            # Get the current batch cycle
            from datetime import datetime
            batch_cycle = BatchCycle.objects.filter(is_active=True).first()
            current_year = datetime.now().year
            
            # Create default batch cycle if none exists
            if not batch_cycle:
                batch_cycle = BatchCycle.objects.create(
                    current_batch='1',
                    cycle_state='waiting_enrollment',
                    is_active=True
                )
            
            
            # Get the current batch cycle
            from datetime import datetime
            batch_cycle = BatchCycle.objects.filter(is_active=True).first()
            current_year = datetime.now().year
            
            # Create default batch cycle if none exists
            if not batch_cycle:
                batch_cycle = BatchCycle.objects.create(
                    current_batch='1',
                    cycle_state='waiting_enrollment',
                    is_active=True
                )
            
            
            for approval_id in selected_approvals:
                try:
                    dms_approval = DMSApproval.objects.get(id=approval_id)
                    
                    # Get the original application
                    original_app = dms_approval.dms_review.get_original_application()
                    
                    if original_app:
                        if dms_approval.application_type == 'program':
                            # Use existing approve_application logic
                            ApprovedApplicant.objects.create(
                                applicant=original_app.applicant,
                                program=original_app.program,
                                batch_number=batch_cycle.current_batch,
                                enrollment_year=current_year
                            )
                            
                            # Create notification
                            Notification.objects.create(
                                recipient=original_app.applicant,
                                sender=request.user,
                                notification_type='approval',
                                title=f"Application Approved: {original_app.program.program_name}",
                                message=f"Congratulations! Your application for {original_app.program.program_name} has been approved. You are enrolled in Batch {batch_cycle.current_batch}, Year {current_year}."
                            )
                            
                            # Delete original application
                            original_app.delete()
                            
                        elif dms_approval.application_type == 'walkin':
                            # Create ApprovedWalkIn entry
                            ApprovedWalkIn.objects.create(
                                applicant=original_app.applicant,
                                program=original_app.program,
                                original_application=original_app,
                                approved_by=request.user,
                                batch_number=batch_cycle.current_batch,
                                enrollment_year=current_year
                            )
                            
                            # Create notification
                            Notification.objects.create(
                                recipient=original_app.applicant,
                                sender=request.user,
                                notification_type='approval',
                                title=f"Walk-in Application Approved: {original_app.program.program_name}",
                                message=f"Your walk-in application for {original_app.program.program_name} has been approved! You are enrolled in Batch {batch_cycle.current_batch}, Year {current_year}."
                            )
                            
                            # Update original application status
                            original_app.status = 'Approved'
                            original_app.processed_by = request.user
                            original_app.processed_at = timezone.now()
                            original_app.save()
                        
                        # Update DMS Approval status
                        dms_approval.status = 'approved'
                        dms_approval.final_approved_at = timezone.now()
                        dms_approval.final_approved_by = request.user
                        dms_approval.save()
                        
                        approved_count += 1
                        
                except DMSApproval.DoesNotExist:
                    continue
                except Exception as e:
                    print(f"Error processing approval {approval_id}: {str(e)}")
                    continue
            
            return JsonResponse({
                'success': True,
                'message': f'Bulk approval completed: {approved_count} applications approved successfully.',
                'approved_count': approved_count
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def archive_training(request):
    """Handle archived training requests - both GET (load archived) and POST (archive training)"""
    
    if request.method == 'GET':
        # Load archived training sessions
        try:
            archived_trainings = ArchivedTraining.objects.filter(
                trainer=request.user
            ).order_by('-archived_at')
            
            archived_data = []
            for archive in archived_trainings:
                archived_data.append({
                    'id': archive.id,
                    'original_training_id': archive.original_training_id,
                    'program_name': archive.program_name,
                    'start_date': archive.start_date.strftime('%Y-%m-%d'),
                    'end_date': archive.end_date.strftime('%Y-%m-%d') if archive.end_date else None,
                    'task_time': archive.task_time.strftime('%H:%M') if archive.task_time else None,
                    'end_time': archive.end_time.strftime('%H:%M') if archive.end_time else None,
                    'room_lab': archive.room_lab,
                    'trainer_name': archive.trainer.get_full_name() or archive.trainer.username,
                    'category': archive.category,
                    'description': archive.description,
                    'archived_at': archive.archived_at.isoformat(),
                    'archive_reason': archive.archive_reason,
                })
            
            return JsonResponse({
                'success': True,
                'archived_trainings': archived_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error loading archived trainings: {str(e)}'
            })
    
    elif request.method == 'POST':
        # Archive a training session
        try:
            data = json.loads(request.body)
            training_id = data.get('training_id')
            archive_reason = data.get('reason', '')
            
            if not training_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Training ID is required'
                })
            
            # Get the training to archive
            training = get_object_or_404(Training, id=training_id, trainer=request.user)
            
            # Create archived training record
            archived_training = ArchivedTraining.objects.create(
                original_training_id=training.id,
                program_name=training.program_name,
                start_date=training.start_date,
                end_date=training.end_date,
                task_time=training.task_time,
                end_time=training.end_time,
                room_lab=training.room_lab,
                trainer=training.trainer,
                category=training.category,
                description=training.description,
                archived_by=request.user,
                archive_reason=archive_reason,
                original_created_at=training.created_at,
                original_updated_at=training.updated_at,
            )
            
            # Delete the original training
            training.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Training session archived successfully'
            })
            
        except Training.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Training session not found or you do not have permission to archive it'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error archiving training: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })


# Support Ticket Views
@csrf_exempt
@require_POST
def create_ticket(request):
    """Create a new support ticket"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Authentication required'
        })
    
    try:
        data = json.loads(request.body)
        
        # Create the ticket
        ticket = SupportTicket.objects.create(
            subject=data.get('subject', ''),
            description=data.get('description', ''),
            category=data.get('category', 'other'),
            priority=data.get('priority', 'medium'),
            recipient=data.get('recipient', 'admin'),
            created_by=request.user
        )
        
        # Handle file attachment if present
        if 'attachment' in request.FILES:
            ticket.attachment = request.FILES['attachment']
            ticket.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Support ticket created successfully',
            'ticket_id': ticket.ticket_id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating ticket: {str(e)}'
        })


@csrf_exempt
def get_user_tickets(request):
    """Get tickets for the current user"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Authentication required'
        })
    
    try:
        tickets = SupportTicket.objects.filter(created_by=request.user).order_by('-created_at')
        
        tickets_data = []
        for ticket in tickets:
            tickets_data.append({
                'id': ticket.id,
                'ticket_id': ticket.ticket_id,
                'subject': ticket.subject,
                'category': ticket.get_category_display(),
                'priority': ticket.get_priority_display(),
                'status': ticket.get_status_display(),
                'created_at': ticket.created_at.strftime('%Y-%m-%d %H:%M'),
                'priority_class': ticket.get_priority_badge_class(),
                'status_class': ticket.get_status_badge_class(),
            })
        
        return JsonResponse({
            'success': True,
            'tickets': tickets_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching tickets: {str(e)}'
        })


@csrf_exempt
def get_ticket_details(request, ticket_id):
    """Get detailed information about a specific ticket"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Authentication required'
        })
    
    try:
        ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id, created_by=request.user)
        
        # Get responses for this ticket
        responses = TicketResponse.objects.filter(ticket=ticket).order_by('created_at')
        responses_data = []
        
        for response in responses:
            responses_data.append({
                'responder': response.responder.get_full_name() or response.responder.username,
                'responder_type': response.get_responder_type_display(),
                'message': response.message,
                'created_at': response.created_at.strftime('%Y-%m-%d %H:%M'),
                'attachment': response.attachment.url if response.attachment else None
            })
        
        ticket_data = {
            'ticket_id': ticket.ticket_id,
            'subject': ticket.subject,
            'description': ticket.description,
            'category': ticket.get_category_display(),
            'priority': ticket.get_priority_display(),
            'recipient': ticket.get_recipient_display(),
            'status': ticket.get_status_display(),
            'created_at': ticket.created_at.strftime('%Y-%m-%d %H:%M'),
            'attachment': ticket.attachment.url if ticket.attachment else None,
            'responses': responses_data,
            'admin_response': ticket.admin_response,
            'trainer_response': ticket.trainer_response,
        }
        
        return JsonResponse({
            'success': True,
            'ticket': ticket_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching ticket details: {str(e)}'
        })


@staff_member_required
@csrf_exempt
def get_all_tickets(request):
    """Get all tickets for admin/staff view"""
    try:
        tickets = SupportTicket.objects.all().order_by('-created_at')
        
        tickets_data = []
        for ticket in tickets:
            tickets_data.append({
                'id': ticket.id,
                'ticket_id': ticket.ticket_id,
                'subject': ticket.subject,
                'category': ticket.get_category_display(),
                'priority': ticket.get_priority_display(),
                'status': ticket.get_status_display(),
                'created_by': ticket.created_by.get_full_name() or ticket.created_by.username,
                'recipient': ticket.get_recipient_display(),
                'created_at': ticket.created_at.strftime('%Y-%m-%d %H:%M'),
                'priority_class': ticket.get_priority_badge_class(),
                'status_class': ticket.get_status_badge_class(),
            })
        
        return JsonResponse({
            'success': True,
            'tickets': tickets_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching tickets: {str(e)}'
        })


@staff_member_required
@csrf_exempt
@require_POST
def update_ticket_status(request):
    """Update ticket status and add response"""
    try:
        data = json.loads(request.body)
        ticket_id = data.get('ticket_id')
        new_status = data.get('status')
        response_message = data.get('response', '')
        
        ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)
        
        # Update ticket status
        if new_status:
            ticket.status = new_status
            if new_status == 'resolved':
                from django.utils import timezone
                ticket.resolved_at = timezone.now()
        
        # Add admin response
        if response_message:
            ticket.admin_response = response_message
            ticket.response_at = timezone.now()
            
            # Create a response record
            TicketResponse.objects.create(
                ticket=ticket,
                responder=request.user,
                responder_type='admin',
                message=response_message
            )
        
        ticket.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Ticket updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating ticket: {str(e)}'
        })
    return JsonResponse({'success': False, 'message': 'Invalid request method'})