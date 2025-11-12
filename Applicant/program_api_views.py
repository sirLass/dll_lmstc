from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Programs, ApprovedApplicant, ApplicantPasser, Learner_Profile
import json


@csrf_exempt
def get_program_applicants(request, program_id):
    """Get approved or completed applicants for a specific program"""
    try:
        # Get the program
        program = Programs.objects.get(id=program_id)
        
        # Get status from query params (approved or complete)
        status = request.GET.get('status', 'approved')
        
        applicants_data = []
        
        if status == 'approved':
            # Get approved applicants
            approved_applicants = ApprovedApplicant.objects.filter(
                program=program
            ).select_related('applicant')
            
            for approved in approved_applicants:
                try:
                    profile = Learner_Profile.objects.get(user=approved.applicant)
                    applicants_data.append({
                        'name': f"{profile.first_name} {profile.middle_name} {profile.last_name}".strip(),
                        'program': program.program_name,
                        'contact': profile.contact_number or 'N/A',
                        'address': f"{profile.barangay}, {profile.city_name or profile.city}" if profile.barangay else 'N/A',
                        'status': 'Approved'
                    })
                except Learner_Profile.DoesNotExist:
                    applicants_data.append({
                        'name': approved.applicant.username,
                        'program': program.program_name,
                        'contact': 'N/A',
                        'address': 'N/A',
                        'status': 'Approved'
                    })
        
        elif status == 'complete':
            # Get completed applicants (passers)
            passers = ApplicantPasser.objects.filter(
                program=program
            ).select_related('applicant')
            
            for passer in passers:
                try:
                    profile = Learner_Profile.objects.get(user=passer.applicant)
                    applicants_data.append({
                        'name': passer.trainee_name or f"{profile.first_name} {profile.middle_name} {profile.last_name}".strip(),
                        'program': passer.program_name or program.program_name,
                        'contact': profile.contact_number or 'N/A',
                        'address': f"{profile.barangay}, {profile.city_name or profile.city}" if profile.barangay else 'N/A',
                        'status': 'Completed'
                    })
                except Learner_Profile.DoesNotExist:
                    applicants_data.append({
                        'name': passer.trainee_name or passer.applicant.username,
                        'program': passer.program_name or program.program_name,
                        'contact': 'N/A',
                        'address': 'N/A',
                        'status': 'Completed'
                    })
        
        return JsonResponse({
            'success': True,
            'program_name': program.program_name,
            'applicants': applicants_data,
            'count': len(applicants_data)
        })
        
    except Programs.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Program not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
