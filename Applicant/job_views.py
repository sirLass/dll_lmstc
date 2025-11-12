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
        # Get limit parameter from request, default to 50
        limit = int(request.GET.get('limit', 50))
        limit = min(limit, 100)  # Cap at 100 to prevent overload
        
        # Scrape jobs from PhilJobNet
        jobs = scrape_philjobnet_jobs(limit)
        
        # Log the scraping result
        logger.info(f"Successfully scraped {len(jobs)} jobs from PhilJobNet")
        
        return JsonResponse({
            'success': True,
            'jobs': jobs,
            'total_count': len(jobs),
            'source': 'PhilJobNet',
            'scraped_at': str(datetime.now())
        })
        
    except Exception as e:
        logger.error(f"Error scraping PhilJobNet jobs: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to fetch jobs from PhilJobNet'
        }, status=500)
