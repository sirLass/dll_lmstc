from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .philjobnet_scraper import scrape_philjobnet_jobs
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

@require_GET
def get_philjobnet_jobs(request):
    """
    API endpoint to fetch job posts from PhilJobNet
    """
    try:
        # Get pagination and filter parameters
        limit = int(request.GET.get('limit', 50))
        limit = min(max(limit, 1), 100)  # Cap at 100 to prevent overload
        search_query = request.GET.get('search') or None
        location_filter = request.GET.get('location') or None
        max_pages = int(request.GET.get('pages', 5))
        max_pages = max(1, min(max_pages, 10))
        
        # Scrape jobs from PhilJobNet with optional filters
        jobs = scrape_philjobnet_jobs(
            limit=limit,
            search_query=search_query,
            location_filter=location_filter,
            max_pages=max_pages
        )
        
        # Log the scraping result
        logger.info(
            f"Successfully scraped {len(jobs)} jobs from PhilJobNet "
            f"(search={search_query}, location={location_filter}, pages={max_pages})"
        )
        
        return JsonResponse({
            'success': True,
            'jobs': jobs,
            'total_count': len(jobs),
            'source': 'PhilJobNet',
            'scraped_at': str(datetime.now()),
            'search': search_query,
            'location': location_filter
        })
        
    except Exception as e:
        logger.error(f"Error scraping PhilJobNet jobs: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to fetch jobs from PhilJobNet'
        }, status=500)
