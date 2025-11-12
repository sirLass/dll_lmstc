"""
Job Matching API Views
Provides endpoints for skill-matched job recommendations
"""
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from .philjobnet_scraper import scrape_philjobnet_jobs
from .skill_matcher import match_jobs_for_user
from .models import ApplicantPasser
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@require_GET
@login_required
def get_matched_jobs(request):
    """
    API endpoint to fetch PESO job posts matched with user's program competencies
    Only returns jobs that match user's completed program competencies
    """
    try:
        user = request.user
        
        # Check if user is a passer (has completed at least one program)
        is_passer = ApplicantPasser.objects.filter(applicant=user).exists()
        
        if not is_passer:
            return JsonResponse({
                'success': False,
                'error': 'User has not completed any programs',
                'message': 'Job recommendations are only available after completing a program.',
                'jobs': []
            })
        
        # Get parameters
        limit = int(request.GET.get('limit', 50))
        limit = min(limit, 100)  # Cap at 100
        min_threshold = float(request.GET.get('min_threshold', 10.0))  # Minimum match percentage
        
        # Scrape jobs from PhilJobNet
        logger.info(f"Fetching {limit} jobs from PhilJobNet for user {user.username}")
        peso_jobs = scrape_philjobnet_jobs(limit)
        
        if not peso_jobs:
            return JsonResponse({
                'success': False,
                'error': 'No jobs available from PhilJobNet',
                'message': 'Failed to fetch jobs. Please try again later.',
                'jobs': []
            })
        
        # Match jobs with user's competencies
        logger.info(f"Matching {len(peso_jobs)} jobs with user competencies (threshold: {min_threshold}%)")
        matched_jobs = match_jobs_for_user(user, peso_jobs, min_threshold)
        
        # Log results
        logger.info(f"Found {len(matched_jobs)} matching jobs for user {user.username}")
        
        # If no matches found, notify user
        if not matched_jobs:
            return JsonResponse({
                'success': True,
                'jobs': [],
                'total_count': 0,
                'matched_count': 0,
                'source': 'PhilJobNet',
                'scraped_at': str(datetime.now()),
                'message': 'No job skills match your program competencies. Try adjusting the match threshold.',
                'no_match': True
            })
        
        return JsonResponse({
            'success': True,
            'jobs': matched_jobs,
            'total_count': len(peso_jobs),
            'matched_count': len(matched_jobs),
            'source': 'PhilJobNet',
            'scraped_at': str(datetime.now()),
            'min_threshold': min_threshold
        })
        
    except ValueError as e:
        logger.error(f"Invalid parameter: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Invalid request parameters'
        }, status=400)
        
    except Exception as e:
        logger.error(f"Error fetching matched jobs: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to fetch and match jobs from PhilJobNet'
        }, status=500)


@require_GET
@login_required
def get_user_competencies_summary(request):
    """
    API endpoint to get user's competencies summary
    Useful for displaying what skills the user has
    """
    try:
        user = request.user
        
        # Get all programs the user has passed
        passed_programs = ApplicantPasser.objects.filter(applicant=user).select_related('program')
        
        if not passed_programs.exists():
            return JsonResponse({
                'success': False,
                'message': 'No completed programs found'
            })
        
        # Collect competencies from all passed programs
        all_competencies = {
            'basic': [],
            'common': [],
            'core': [],
            'job_opportunities': []
        }
        
        programs_info = []
        
        for passer in passed_programs:
            program = passer.program
            programs_info.append({
                'program_name': program.program_name,
                'completion_date': passer.completion_date.strftime('%Y-%m-%d') if passer.completion_date else None
            })
            
            if program.program_competencies:
                comp = program.program_competencies
                
                # Basic competencies
                if comp.get('basic'):
                    all_competencies['basic'].extend(comp['basic'])
                
                # Common competencies
                if comp.get('common'):
                    all_competencies['common'].extend(comp['common'])
                
                # Core competencies
                if comp.get('core'):
                    all_competencies['core'].extend(comp['core'])
                
                # Job opportunities
                if comp.get('job_opportunities'):
                    all_competencies['job_opportunities'].extend(comp['job_opportunities'])
        
        return JsonResponse({
            'success': True,
            'programs': programs_info,
            'competencies': all_competencies,
            'total_programs_completed': len(programs_info)
        })
        
    except Exception as e:
        logger.error(f"Error fetching user competencies: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to fetch user competencies'
        }, status=500)


@require_GET
@login_required
def test_skill_match(request):
    """
    Test endpoint to verify skill matching is working
    """
    try:
        user = request.user
        
        # Test with a sample job
        test_job = {
            'id': 'test_001',
            'title': 'Software Developer',
            'company': 'Test Company',
            'skills': ['Programming', 'Python', 'JavaScript', 'Web Development'],
            'description': 'Develop web applications using modern frameworks'
        }
        
        matched_jobs = match_jobs_for_user(user, [test_job], min_threshold=5.0)
        
        return JsonResponse({
            'success': True,
            'test_job': test_job,
            'matched_jobs': matched_jobs,
            'match_found': len(matched_jobs) > 0,
            'match_percentage': matched_jobs[0]['match_percentage'] if matched_jobs else 0
        })
        
    except Exception as e:
        logger.error(f"Error in test skill match: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
