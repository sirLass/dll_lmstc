"""
Job Matching API Views
Provides endpoints for skill-matched job recommendations
"""
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from .philjobnet_scraper import scrape_philjobnet_jobs
from .job_matching import match_jobs_for_user as match_jobs_heuristic
from .job_matching import save_high_match_jobs  # for sklearn path persistence
from .skill_matcher_sklearn import match_jobs_for_user as match_jobs_sklearn
from .models import ApplicantPasser
import logging
from datetime import datetime
from django.core.cache import cache

logger = logging.getLogger(__name__)


@require_GET
@login_required
def get_matched_jobs(request):
    """
    API endpoint to fetch PESO job posts matched with user's program competencies
    Batched approach: fetch 50 at a time; if no high matches (>=50%), fetch next batch.
    Returns only high matches sorted by score (and saves them via job_matching logic).
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

        # Parameters
        batch_size = int(request.GET.get('limit', 50))  # interpret 'limit' as batch size
        batch_size = min(max(batch_size, 1), 100)
        min_threshold = float(request.GET.get('min_threshold', 0.0))  # minimum score to appear in response
        search_query = request.GET.get('search') or None
        location_filter = request.GET.get('location') or None
        # Optional controls
        max_batches = int(request.GET.get('batches', 5))
        max_batches = max(1, min(max_batches, 10))
        pages_per_batch = int(request.GET.get('pages_per_batch', 1))
        pages_per_batch = max(1, min(pages_per_batch, 2))
        stop_after_count = int(request.GET.get('stop_after_count', 10))  # stop after N matched jobs
        stop_after_count = max(1, min(stop_after_count, 100))
        stop_after_high = int(request.GET.get('stop_after_high', 10))     # or stop after N high matches
        stop_after_high = max(1, min(stop_after_high, 100))

        algo = (request.GET.get('algo') or 'heuristic').strip().lower()
        if algo not in {"heuristic", "sklearn", "hybrid"}:
            algo = "heuristic"

        logger.info(
            "Batched matching: user=%s, algo=%s, batch_size=%s, max_batches=%s, pages_per_batch=%s, search=%s, location=%s",
            user.username, algo, batch_size, max_batches, pages_per_batch, search_query, location_filter
        )

        all_matches = []
        total_scraped = 0
        cache_key = f"job_matching_cancel:{user.id}"
        # Clear any previous cancel flag at the start of a new request
        cache.delete(cache_key)
        cancelled = False
        stopped_early = False
        stop_reason = None

        for batch_index in range(max_batches):
            # Check if a cancel request has been issued for this user
            if cache.get(cache_key):
                cancelled = True
                break
            start_page = 1 + (batch_index * pages_per_batch)
            peso_jobs = scrape_philjobnet_jobs(
                limit=batch_size,
                search_query=search_query,
                location_filter=location_filter,
                max_pages=pages_per_batch,
                start_page=start_page,
            )

            if not peso_jobs:
                # No more jobs available
                break

            total_scraped += len(peso_jobs)
            # Compute matches according to selected algorithm
            if algo == "heuristic":
                matched_jobs = match_jobs_heuristic(user, peso_jobs, min_threshold)
            elif algo == "sklearn":
                matched_jobs = match_jobs_sklearn(user, peso_jobs, min_threshold)
                # Persist high matches for sklearn path (mirror heuristic behavior)
                try:
                    for j in matched_jobs:
                        if j.get('match_percentage', 0) >= 50:
                            save_high_match_jobs(user, j, j.get('match_percentage', 0))
                except Exception:
                    logger.warning("Failed saving sklearn high matches for user=%s", user.username)
            else:  # hybrid -> compute both and take max per job id
                h_matches = match_jobs_heuristic(user, peso_jobs, 0.0)
                s_matches = match_jobs_sklearn(user, peso_jobs, 0.0)
                # Index by id for combination; fallback to title if id missing
                def _key(job):
                    return job.get('id') or job.get('url') or (job.get('title'), job.get('company'))
                s_map = { _key(j): j for j in s_matches }
                combined = []
                for hj in h_matches:
                    key = _key(hj)
                    sj = s_map.get(key)
                    h_score = hj.get('match_percentage', 0) or hj.get('matchScore', 0)
                    s_score = (sj.get('match_percentage', 0) if sj else 0)
                    best = max(h_score, s_score)
                    merged = hj.copy()
                    merged['match_percentage'] = round(float(best), 2)
                    combined.append(merged)
                # Persist high matches from hybrid
                try:
                    for j in combined:
                        if j.get('match_percentage', 0) >= 50:
                            save_high_match_jobs(user, j, j.get('match_percentage', 0))
                except Exception:
                    logger.warning("Failed saving hybrid high matches for user=%s", user.username)
                # Apply min_threshold
                matched_jobs = [j for j in combined if j.get('match_percentage', 0) >= min_threshold]
            all_matches.extend(matched_jobs)

            # Early stop once we have enough total matches
            if len(all_matches) >= stop_after_count:
                stopped_early = True
                stop_reason = 'count'
                break

            # Or early stop once we have enough high matches
            current_high = sum(1 for j in all_matches if j.get('match_percentage', 0) >= 50.0)
            if current_high >= stop_after_high:
                stopped_early = True
                stop_reason = 'high'
                break

        # Sort all matches descending by score
        all_matches.sort(key=lambda j: j.get('match_percentage', 0), reverse=True)

        # Backward-compatible fields expected by Dashboard.js
        matched_count = len(all_matches)
        high_match_count = sum(1 for j in all_matches if j.get('match_percentage', 0) >= 50.0)
        total_count = total_scraped

        return JsonResponse({
            'success': True,
            'jobs': all_matches,
            # New batched metadata
            'batched': True,
            'total_scraped': total_scraped,
            'returned_count': matched_count,
            'high_match_threshold': 50.0,
            'stop_after_count': stop_after_count,
            'stop_after_high': stop_after_high,
            'cancelled': cancelled,
            'stopped_early': stopped_early,
            'stop_reason': stop_reason,
            # Backward-compatible keys used by the dashboard
            'matched_count': matched_count,
            'high_match_count': high_match_count,
            'total_count': total_count,
            # Common fields
            'source': 'PhilJobNet',
            'scraped_at': str(datetime.now()),
            'search': search_query,
            'location': location_filter,
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


@require_POST
@login_required
def cancel_matched_jobs(request):
    """
    Signal the backend to cancel an in-progress job matching request for the current user.
    This sets a cache flag that is checked between batches in get_matched_jobs.
    """
    try:
        user = request.user
        cache_key = f"job_matching_cancel:{user.id}"
        # Set cancel flag with short TTL
        cache.set(cache_key, True, timeout=300)
        return JsonResponse({
            'success': True,
            'cancelled': True
        })
    except Exception as e:
        logger.error(f"Error setting cancel flag: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
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
