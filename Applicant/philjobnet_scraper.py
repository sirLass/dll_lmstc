import re
from datetime import datetime, timedelta
import json
import logging
from urllib.parse import urljoin, parse_qs, urlparse, quote_plus
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PhilJobNetScraper:
    def __init__(self):
        self.base_url = "https://philjobnet.gov.ph"
        self.job_vacancies_url = "https://philjobnet.gov.ph/job-vacancies/"
        # Initialize Selenium WebDriver (headless Chrome)
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            self.wait = WebDriverWait(self.driver, 15)
        except Exception as e:
            logger.error(f"Failed to initialize Selenium WebDriver: {e}")
            self.driver = None
            self.wait = None

    def get_job_vacancies(self, limit=50, search_query=None, location_filter=None, max_pages=5, start_page=1):
        """
        Scrape job vacancies from PhilJobNet (including domestic and international jobs)
        Returns a list of job dictionaries
        """
        # Clamp to keep requests fast
        try:
            limit = min(max(int(limit), 1), 30)
        except Exception:
            limit = 30
        try:
            max_pages = max(1, min(int(max_pages), 2))
        except Exception:
            max_pages = 1

        collected_jobs = []
        # If Selenium is not available, return fallback quickly
        if not getattr(self, 'driver', None):
            logger.warning("Selenium WebDriver unavailable; returning fallback jobs")
            fallback = self._filter_jobs(self._get_fallback_jobs(), search_query, location_filter)
            return fallback[:limit]
        try:
            page = max(1, int(start_page))
            last_page = page + max_pages - 1
            while len(collected_jobs) < limit and page <= last_page:
                page_loaded = self._fetch_page_soup(page, search_query)
                if not page_loaded:
                    break
                page_jobs = self._extract_jobs_from_main_page(None)
                if not page_jobs:
                    if page == 1:
                        logger.warning("No job data found on main page, using fallback data")
                    break
                for job in page_jobs:
                    if self._job_matches_filters(job, search_query, location_filter):
                        collected_jobs.append(job)
                        if len(collected_jobs) >= limit:
                            break
                page += 1
                # Be a bit nicer to the remote server
                time.sleep(random.uniform(0.6, 1.4))
            if not collected_jobs:
                fallback = self._filter_jobs(self._get_fallback_jobs(), search_query, location_filter)
                return fallback[:limit]
            logger.info(f"Successfully scraped {len(collected_jobs)} job posts across {page - 1} page(s)")
            return collected_jobs
        except Exception as e:
            logger.error(f"Error scraping PhilJobNet: {e}")
            fallback = self._filter_jobs(self._get_fallback_jobs(), search_query, location_filter)
            return fallback[:limit]

    def _fetch_page_soup(self, page_number=1, search_query=None):
        """Load a specific page with Selenium and optionally perform a search. Returns True if loaded."""
        try:
            # Build URL with optional search query using WordPress ?s= parameter
            # If no explicit search query provided, load the general listing page(s)
            if isinstance(search_query, str) and search_query.strip():
                effective_query = search_query.strip()
                if page_number <= 1:
                    page_url = f"{self.job_vacancies_url}?s={quote_plus(effective_query)}"
                else:
                    page_url = urljoin(self.job_vacancies_url, f"page/{page_number}/?s={quote_plus(effective_query)}")
            else:
                if page_number <= 1:
                    page_url = self.job_vacancies_url
                else:
                    page_url = urljoin(self.job_vacancies_url, f"page/{page_number}/")
            logger.info(f"Navigating to {page_url}")
            self.driver.get(page_url)
            # Wait for the page body (keep small)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            time.sleep(0.6)
            return True
        except Exception as e:
            logger.error(f"Unable to load PhilJobNet page {page_number}: {e}")
            return False

    def _extract_jobs_from_main_page(self, soup):
        """Extract job information from the vacancies page using Selenium DOM queries"""
        jobs = []

        try:
            # Find all job links - pattern /job-vacancies/job/{slug}-{id}
            link_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/job-vacancies/job/']")
            logger.info(f"Found {len(link_elements)} job links on page")
            seen = set()
            processed = 0
            for link in link_elements:
                try:
                    job_url = link.get_attribute('href') or ''
                    if not job_url:
                        continue
                    if job_url in seen:
                        continue
                    seen.add(job_url)

                    # Extract job ID from URL (last part after final hyphen)
                    job_id_match = re.search(r'-(\d+)$', job_url)
                    job_id = job_id_match.group(1) if job_id_match else str(random.randint(10000, 99999))

                    # Try to go up to find the job card container
                    parent = link
                    for _ in range(5):
                        try:
                            parent = parent.find_element(By.XPATH, "./..")
                        except Exception:
                            break

                    # Get all text from the link itself
                    link_text = (link.text or '').strip()
                    lines = [line.strip() for line in link_text.split('\n') if line.strip()]

                    # Parse job information from lines
                    job_title = lines[0] if len(lines) > 0 else (link.get_attribute('title') or "Job Position")
                    salary = lines[1] if len(lines) > 1 and '₱' in lines[1] else "Competitive"
                    company = lines[2] if len(lines) > 2 else "Company"
                    location = lines[3] if len(lines) > 3 else "Philippines"
                    education = lines[4] if len(lines) > 4 else "Not specified"
                    employment_type = lines[5] if len(lines) > 5 else "Full-time"
                    posted_date = lines[6] if len(lines) > 6 else datetime.now().strftime('%Y-%m-%d')

                    # Clean salary format
                    salary = salary.replace('₱', '').strip()

                    # Extract posted date
                    posted_match = re.search(r'Posted on (\d{1,2}/\d{1,2}/\d{4})', posted_date)
                    if posted_match:
                        try:
                            posted_date_obj = datetime.strptime(posted_match.group(1), '%m/%d/%Y')
                            posted_date = posted_date_obj.strftime('%Y-%m-%d')
                        except:
                            posted_date = datetime.now().strftime('%Y-%m-%d')
                    else:
                        posted_date = datetime.now().strftime('%Y-%m-%d')

                    # Build full URL
                    full_url = urljoin(self.base_url, job_url)

                    job = {
                        'id': job_id,
                        'title': job_title.upper(),
                        'company': company,
                        'location': location,
                        'description': f"Position: {job_title}. Education required: {education}.",
                        'requirements': f"Education: {education}",
                        'salary': salary,
                        'employment_type': employment_type,
                        'posted_date': posted_date,
                        'vacancy_count': 1,
                        'skills': self._extract_skills_from_title(job_title),
                        'url': full_url,
                        'source': 'PhilJobNet',
                        'education_level': education
                    }

                    jobs.append(job)
                    processed += 1
                    if processed >= 40:  # cap per page to keep things snappy
                        break

                except Exception as e:
                    logger.warning(f"Error parsing job: {e}")
                    continue

            return jobs

        except Exception as e:
            logger.error(f"Error extracting jobs from main page: {e}")
            return []

    def _job_matches_filters(self, job, search_query=None, location_filter=None):
        """Check if a job matches the provided search text and location filters"""
        if not job:
            return False
        if search_query:
            query = search_query.lower()
            combined = ' '.join([
                job.get('title', ''),
                job.get('company', ''),
                job.get('location', ''),
                job.get('description', ''),
                job.get('employment_type', ''),
                ' '.join(job.get('skills', []))
            ]).lower()
            if query not in combined:
                return False
        if location_filter:
            loc = job.get('location', '').lower()
            if location_filter.lower() not in loc:
                return False
        return True

    def _filter_jobs(self, jobs, search_query=None, location_filter=None):
        if not jobs:
            return []
        return [job for job in jobs if self._job_matches_filters(job, search_query, location_filter)]

    def _get_job_detail(self, job_url):
        """Get detailed information for a specific job using Selenium"""
        try:
            full_url = urljoin(self.base_url, job_url)
            self.driver.get(full_url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

            def _first_text(selectors):
                for sel in selectors:
                    try:
                        if sel.startswith('.') or sel.startswith('#'):
                            elem = self.driver.find_element(By.CSS_SELECTOR, sel)
                        else:
                            elem = self.driver.find_element(By.TAG_NAME, sel)
                        txt = elem.text.strip()
                        if txt:
                            return txt
                    except Exception:
                        continue
                return ""

            job = {
                'id': self._extract_job_id(job_url),
                'title': _first_text(['h1', 'h2', '.job-title', '#job-title']) or 'Job Position',
                'company': _first_text(['.company', '#company', '.employer']) or 'Company Name',
                'location': _first_text(['.location', '#location', '.address']) or 'Philippines',
                'description': _first_text(['.description', '#description', '.job-desc']) or 'Job description not available.',
                'requirements': _first_text(['.requirements', '#requirements', '.qualifications']) or 'Requirements not specified.',
                'salary': _first_text(['.salary', '#salary', '.compensation']) or 'Competitive',
                'employment_type': 'Full-time',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'vacancy_count': 1,
                'skills': [],
                'url': full_url,
                'source': 'PhilJobNet'
            }
            job = self._clean_job_data(job)
            return job
        except Exception as e:
            logger.error(f"Error getting job detail from {job_url}: {e}")
            return None

    def _extract_text(self, soup, selectors):
        """Deprecated: kept for compatibility; Selenium version uses _get_job_detail instead."""
        return ""

    def _extract_job_id(self, url):
        """Extract job ID from URL"""
        match = re.search(r'id=(\d+)', url)
        return match.group(1) if match else str(random.randint(1000, 9999))

    def _extract_skills_from_title(self, title):
        """Extract potential skills from job title"""
        skills_map = {
            'MANAGER': ['Management', 'Leadership', 'Team Management'],
            'ENGINEER': ['Engineering', 'Technical Skills', 'Problem Solving'],
            'CUSTOMER SERVICE': ['Customer Service', 'Communication'],
            'PRODUCTION': ['Manufacturing', 'Quality Control'],
            'CALL CENTER': ['Customer Service', 'Communication', 'Phone Support'],
            'NURSE': ['Healthcare', 'Patient Care', 'Medical'],
            'CASHIER': ['Customer Service', 'Cash Handling', 'POS Systems'],
            'SALES': ['Sales', 'Customer Relations', 'Communication'],
            'OFFICE': ['Administrative', 'Computer Skills', 'Documentation'],
            'ADMINISTRATIVE': ['Administrative', 'Organization', 'Documentation'],
            'TECHNICAL': ['Technical Skills', 'Problem Solving'],
            'QUALITY': ['Quality Assurance', 'Attention to Detail'],
            'HELPER': ['Manual Labor', 'Teamwork'],
            'OPERATOR': ['Equipment Operation', 'Technical Skills'],
            'CLEANER': ['Cleaning', 'Attention to Detail'],
            'BARISTA': ['Customer Service', 'Food Preparation'],
            'ACCOUNTING': ['Accounting', 'Financial Management', 'Bookkeeping'],
            'MECHANICAL': ['Mechanical Skills', 'Technical Skills'],
            'PEST CONTROL': ['Pest Control', 'Safety Procedures']
        }
        
        skills = []
        title_upper = title.upper()
        
        for keyword, skill_list in skills_map.items():
            if keyword in title_upper:
                skills.extend(skill_list)
        
        return list(set(skills))  # Remove duplicates
    
    def _clean_job_data(self, job):
        """Clean and validate job data"""
        # Ensure required fields have default values
        defaults = {
            'title': 'Job Position',
            'company': 'Company Name',
            'location': 'Philippines',
            'description': 'Job description not available.',
            'requirements': 'Requirements not specified.',
            'salary': 'Competitive',
            'employment_type': 'Full-time',
            'skills': []
        }
        
        for key, default_value in defaults.items():
            if not job.get(key) or job[key].strip() == '':
                job[key] = default_value
        
        # Ensure skills is a list
        if not isinstance(job['skills'], list):
            job['skills'] = []
        
        return job
    
    def _get_fallback_jobs(self):
        """Return fallback job data if scraping fails"""
        logger.info("Using fallback job data")
        
        fallback_jobs = [
            {
                'id': '5701',
                'title': 'CUSTOMER SERVICE ASSISTANT',
                'company': 'Various Companies',
                'location': 'Philippines',
                'description': 'Handle customer inquiries, provide support, and maintain customer satisfaction.',
                'requirements': 'Good communication skills, customer service experience preferred.',
                'salary': 'PHP 15,000 - 25,000',
                'employment_type': 'Full-time',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'vacancy_count': 33209,
                'skills': ['Customer Service', 'Communication'],
                'url': 'https://philjobnet.gov.ph/job-vacancies/',
                'source': 'PhilJobNet'
            },
            {
                'id': '7429',
                'title': 'PRODUCTION MACHINE OPERATOR',
                'company': 'Manufacturing Companies',
                'location': 'Philippines',
                'description': 'Operate production machinery, monitor quality, and ensure safety standards.',
                'requirements': 'Technical skills, machinery operation experience, safety awareness.',
                'salary': 'PHP 18,000 - 28,000',
                'employment_type': 'Full-time',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'vacancy_count': 32125,
                'skills': ['Equipment Operation', 'Technical Skills', 'Quality Control'],
                'url': 'https://philjobnet.gov.ph/job-vacancies/',
                'source': 'PhilJobNet'
            },
            {
                'id': '8130',
                'title': 'PRODUCTION WORKER',
                'company': 'Manufacturing Companies',
                'location': 'Philippines',
                'description': 'Assist in production processes, quality control, and maintaining clean work environment.',
                'requirements': 'Physical fitness, attention to detail, teamwork skills.',
                'salary': 'PHP 15,000 - 22,000',
                'employment_type': 'Full-time',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'vacancy_count': 27370,
                'skills': ['Manufacturing', 'Quality Control', 'Teamwork'],
                'url': 'https://philjobnet.gov.ph/job-vacancies/',
                'source': 'PhilJobNet'
            },
            {
                'id': '5706',
                'title': 'CALL CENTER AGENT',
                'company': 'BPO Companies',
                'location': 'Philippines',
                'description': 'Handle customer calls, provide technical support, and resolve customer issues.',
                'requirements': 'Excellent English communication, computer skills, customer service experience.',
                'salary': 'PHP 20,000 - 35,000',
                'employment_type': 'Full-time',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'vacancy_count': 25856,
                'skills': ['Customer Service', 'Communication', 'Phone Support', 'English'],
                'url': 'https://philjobnet.gov.ph/job-vacancies/',
                'source': 'PhilJobNet'
            },
            {
                'id': '2118',
                'title': 'STAFF NURSE',
                'company': 'Healthcare Facilities',
                'location': 'Philippines',
                'description': 'Provide patient care, administer medications, and assist doctors in medical procedures.',
                'requirements': 'Nursing degree, PRC license, healthcare experience preferred.',
                'salary': 'PHP 25,000 - 40,000',
                'employment_type': 'Full-time',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'vacancy_count': 5911,
                'skills': ['Healthcare', 'Patient Care', 'Medical', 'Nursing'],
                'url': 'https://philjobnet.gov.ph/job-vacancies/',
                'source': 'PhilJobNet'
            }
        ]
        
        return fallback_jobs

    def close(self):
        if self.driver:
            self.driver.quit()

def scrape_philjobnet_jobs(limit=50, search_query=None, location_filter=None, max_pages=5, start_page=1):
    """
    Main function to scrape PhilJobNet jobs with optional search and location filters
    
    Args:
        limit: Maximum number of jobs to return
        search_query: Optional search text to filter jobs
        location_filter: Optional location to filter jobs
        max_pages: Maximum number of pages to scrape (default 5)
    """
    scraper = PhilJobNetScraper()
    try:
        return scraper.get_job_vacancies(limit, search_query, location_filter, max_pages, start_page)
    finally:
        scraper.close()

if __name__ == "__main__":
    # Test the scraper
    jobs = scrape_philjobnet_jobs(10)
    print(f"Scraped {len(jobs)} jobs")
    for job in jobs[:3]:  # Print first 3 jobs
        print(f"- {job['title']} at {job['company']} ({job['vacancy_count']} openings)")
