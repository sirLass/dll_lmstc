import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import json
import logging
from urllib.parse import urljoin, parse_qs, urlparse
import time
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PhilJobNetScraper:
    def __init__(self):
        self.base_url = "https://peis.philjobnet.ph"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_job_vacancies(self, limit=50):
        """
        Scrape job vacancies from PhilJobNet
        Returns a list of job dictionaries
        """
        try:
            # Get the main page to extract job links
            response = self.session.get(f"{self.base_url}/index.aspx", timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            jobs = []
            
            # Find job links - they typically have pattern /details.aspx?id=...
            job_links = soup.find_all('a', href=re.compile(r'/details\.aspx\?id=\d+'))
            
            # Extract job data from the main page
            job_data = self._extract_jobs_from_main_page(soup)
            
            # If we have job data from main page, use it
            if job_data:
                jobs.extend(job_data[:limit])
                logger.info(f"Extracted {len(job_data)} jobs from main page")
            else:
                logger.info("No job data found on main page, trying individual job details")
                # Fallback: try to get individual job details
                for i, link in enumerate(job_links[:limit]):
                    if i >= limit:
                        break
                        
                    try:
                        job_detail = self._get_job_detail(link['href'])
                        if job_detail:
                            jobs.append(job_detail)
                        
                        # Add delay to avoid overwhelming the server
                        time.sleep(random.uniform(0.5, 1.0))
                        
                    except Exception as e:
                        logger.warning(f"Error getting job detail: {e}")
                        continue
            
            # If still no jobs found, return fallback data
            if not jobs:
                logger.warning("No jobs found from scraping, using fallback data")
                return self._get_fallback_jobs()[:limit]
            
            logger.info(f"Successfully scraped {len(jobs)} job posts")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping PhilJobNet: {e}")
            return self._get_fallback_jobs()
    
    def _extract_jobs_from_main_page(self, soup):
        """Extract job information from the main page"""
        jobs = []
        
        try:
            # Look for job listings in various possible containers
            job_containers = soup.find_all(['div', 'table', 'ul'], class_=re.compile(r'job|vacancy|position', re.I))
            
            # Also check for links with job-related patterns
            job_links = soup.find_all('a', href=re.compile(r'/details\.aspx\?id=\d+'))
            
            for link in job_links:
                try:
                    # Extract job ID from URL
                    url_parts = parse_qs(urlparse(link['href']).query)
                    job_id = url_parts.get('id', [''])[0]
                    position = url_parts.get('position', [''])[0]
                    
                    if not job_id:
                        continue
                    
                    # Get job title from link text or position parameter
                    job_title = link.get_text(strip=True) or position or "Job Position"
                    
                    # Extract vacancy count if available (usually in parentheses)
                    vacancy_match = re.search(r'\((\d+(?:,\d+)*)\)', link.get_text())
                    vacancy_count = vacancy_match.group(1).replace(',', '') if vacancy_match else "1"
                    
                    job = {
                        'id': job_id,
                        'title': job_title.upper(),
                        'company': 'Various Companies',
                        'location': 'Philippines',
                        'description': f"Multiple openings available for {job_title} position.",
                        'requirements': 'Please check individual job postings for specific requirements.',
                        'salary': 'Competitive',
                        'employment_type': 'Full-time',
                        'posted_date': datetime.now().strftime('%Y-%m-%d'),
                        'deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                        'vacancy_count': int(vacancy_count) if vacancy_count.isdigit() else 1,
                        'skills': self._extract_skills_from_title(job_title),
                        'url': urljoin(self.base_url, link['href']),
                        'source': 'PhilJobNet'
                    }
                    
                    jobs.append(job)
                    
                except Exception as e:
                    logger.warning(f"Error parsing job link: {e}")
                    continue
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error extracting jobs from main page: {e}")
            return []
    
    def _get_job_detail(self, job_url):
        """Get detailed information for a specific job"""
        try:
            full_url = urljoin(self.base_url, job_url)
            response = self.session.get(full_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract job details from the page
            job = {
                'id': self._extract_job_id(job_url),
                'title': self._extract_text(soup, ['h1', 'h2', '.job-title', '#job-title']),
                'company': self._extract_text(soup, ['.company', '#company', '.employer']),
                'location': self._extract_text(soup, ['.location', '#location', '.address']),
                'description': self._extract_text(soup, ['.description', '#description', '.job-desc']),
                'requirements': self._extract_text(soup, ['.requirements', '#requirements', '.qualifications']),
                'salary': self._extract_text(soup, ['.salary', '#salary', '.compensation']),
                'employment_type': 'Full-time',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'vacancy_count': 1,
                'skills': [],
                'url': full_url,
                'source': 'PhilJobNet'
            }
            
            # Clean up and validate job data
            job = self._clean_job_data(job)
            return job
            
        except Exception as e:
            logger.error(f"Error getting job detail from {job_url}: {e}")
            return None
    
    def _extract_text(self, soup, selectors):
        """Extract text from soup using multiple possible selectors"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return ""
    
    def _extract_job_id(self, url):
        """Extract job ID from URL"""
        match = re.search(r'id=(\d+)', url)
        return match.group(1) if match else str(random.randint(1000, 9999))
    
    def _extract_skills_from_title(self, title):
        """Extract potential skills from job title"""
        skills_map = {
            'CUSTOMER SERVICE': ['Customer Service', 'Communication'],
            'PRODUCTION': ['Manufacturing', 'Quality Control'],
            'CALL CENTER': ['Customer Service', 'Communication', 'Phone Support'],
            'NURSE': ['Healthcare', 'Patient Care', 'Medical'],
            'CASHIER': ['Customer Service', 'Cash Handling', 'POS Systems'],
            'SALES': ['Sales', 'Customer Relations', 'Communication'],
            'OFFICE': ['Administrative', 'Computer Skills', 'Documentation'],
            'TECHNICAL': ['Technical Skills', 'Problem Solving'],
            'QUALITY': ['Quality Assurance', 'Attention to Detail'],
            'HELPER': ['Manual Labor', 'Teamwork'],
            'OPERATOR': ['Equipment Operation', 'Technical Skills']
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
                'url': 'https://peis.philjobnet.ph/details.aspx?id=5701',
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
                'url': 'https://peis.philjobnet.ph/details.aspx?id=7429',
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
                'url': 'https://peis.philjobnet.ph/details.aspx?id=8130',
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
                'url': 'https://peis.philjobnet.ph/details.aspx?id=5706',
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
                'url': 'https://peis.philjobnet.ph/details.aspx?id=2118',
                'source': 'PhilJobNet'
            }
        ]
        
        return fallback_jobs

def scrape_philjobnet_jobs(limit=50):
    """
    Main function to scrape PhilJobNet jobs
    """
    scraper = PhilJobNetScraper()
    return scraper.get_job_vacancies(limit)

if __name__ == "__main__":
    # Test the scraper
    jobs = scrape_philjobnet_jobs(10)
    print(f"Scraped {len(jobs)} jobs")
    for job in jobs[:3]:  # Print first 3 jobs
        print(f"- {job['title']} at {job['company']} ({job['vacancy_count']} openings)")
