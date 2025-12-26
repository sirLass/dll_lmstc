from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Programs, ApprovedApplicant, ApplicantPasser, Learner_Profile
import json


@csrf_exempt
def get_program_applicants(request, program_id):
    """Get approved, completed, dropped, or failed applicants for a specific program"""
    try:
        # Get the program
        program = Programs.objects.get(id=program_id)
        
        # Get status from query params (approved, complete, dropped, failed)
        status = request.GET.get('status', 'approved')
        
        applicants_data = []
        
        def build_address(profile):
            """Build full address from profile"""
            address_parts = []
            if profile.street:
                address_parts.append(profile.street)
            if profile.barangay_name:
                address_parts.append(profile.barangay_name)
            if profile.city_name:
                address_parts.append(profile.city_name)
            if profile.province_name:
                address_parts.append(profile.province_name)
            if profile.region_name:
                address_parts.append(profile.region_name)
            return ", ".join(address_parts) if address_parts else 'N/A'
        
        if status == 'approved':
            # Get approved applicants (active status)
            approved_applicants = ApprovedApplicant.objects.filter(
                program=program,
                status='active'
            ).select_related('applicant')
            
            for approved in approved_applicants:
                try:
                    profile = Learner_Profile.objects.get(user=approved.applicant)
                    applicants_data.append({
                        'name': f"{profile.first_name} {profile.middle_name or ''} {profile.last_name}".strip(),
                        'program': program.program_name,
                        'contact': profile.contact_number or 'N/A',
                        'address': build_address(profile),
                        'email': profile.email or approved.applicant.email or 'N/A',
                        'sex': profile.sex or 'N/A',
                        'status': 'Approved'
                    })
                except Learner_Profile.DoesNotExist:
                    applicants_data.append({
                        'name': approved.applicant.get_full_name() or approved.applicant.username,
                        'program': program.program_name,
                        'contact': 'N/A',
                        'address': 'N/A',
                        'email': approved.applicant.email or 'N/A',
                        'sex': 'N/A',
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
                        'name': passer.trainee_name or f"{profile.first_name} {profile.middle_name or ''} {profile.last_name}".strip(),
                        'program': passer.program_name or program.program_name,
                        'contact': profile.contact_number or 'N/A',
                        'address': build_address(profile),
                        'email': profile.email or passer.applicant.email or 'N/A',
                        'sex': profile.sex or 'N/A',
                        'status': 'Completed'
                    })
                except Learner_Profile.DoesNotExist:
                    applicants_data.append({
                        'name': passer.trainee_name or passer.applicant.username,
                        'program': passer.program_name or program.program_name,
                        'contact': 'N/A',
                        'address': 'N/A',
                        'email': passer.applicant.email or 'N/A',
                        'sex': 'N/A',
                        'status': 'Completed'
                    })
        
        elif status == 'dropped':
            # Get dropped applicants
            dropped_applicants = ApprovedApplicant.objects.filter(
                program=program,
                status='dropped'
            ).select_related('applicant')
            
            for dropped in dropped_applicants:
                try:
                    profile = Learner_Profile.objects.get(user=dropped.applicant)
                    applicants_data.append({
                        'name': f"{profile.first_name} {profile.middle_name or ''} {profile.last_name}".strip(),
                        'program': program.program_name,
                        'contact': profile.contact_number or 'N/A',
                        'address': build_address(profile),
                        'email': profile.email or dropped.applicant.email or 'N/A',
                        'sex': profile.sex or 'N/A',
                        'status': 'Dropped'
                    })
                except Learner_Profile.DoesNotExist:
                    applicants_data.append({
                        'name': dropped.applicant.get_full_name() or dropped.applicant.username,
                        'program': program.program_name,
                        'contact': 'N/A',
                        'address': 'N/A',
                        'email': dropped.applicant.email or 'N/A',
                        'sex': 'N/A',
                        'status': 'Dropped'
                    })
        
        elif status == 'failed':
            # Get failed applicants (finished status but not in passers - could be failed)
            # Note: You may need to add a 'failed' status field or use a different logic
            failed_applicants = ApprovedApplicant.objects.filter(
                program=program,
                status='finished'
            ).select_related('applicant')
            
            # Exclude those who are in passers (completed successfully)
            passer_ids = ApplicantPasser.objects.filter(program=program).values_list('applicant_id', flat=True)
            failed_applicants = failed_applicants.exclude(applicant_id__in=passer_ids)
            
            for failed in failed_applicants:
                try:
                    profile = Learner_Profile.objects.get(user=failed.applicant)
                    applicants_data.append({
                        'name': f"{profile.first_name} {profile.middle_name or ''} {profile.last_name}".strip(),
                        'program': program.program_name,
                        'contact': profile.contact_number or 'N/A',
                        'address': build_address(profile),
                        'email': profile.email or failed.applicant.email or 'N/A',
                        'sex': profile.sex or 'N/A',
                        'status': 'Failed'
                    })
                except Learner_Profile.DoesNotExist:
                    applicants_data.append({
                        'name': failed.applicant.get_full_name() or failed.applicant.username,
                        'program': program.program_name,
                        'contact': 'N/A',
                        'address': 'N/A',
                        'email': failed.applicant.email or 'N/A',
                        'sex': 'N/A',
                        'status': 'Failed'
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
