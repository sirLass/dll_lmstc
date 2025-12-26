"""Test script for the updated PhilJobNet scraper"""
from Applicant.philjobnet_scraper import scrape_philjobnet_jobs

print("Testing PhilJobNet scraper with new URL...")
print("=" * 60)

jobs = scrape_philjobnet_jobs(10)

print(f"\nTotal jobs found: {len(jobs)}")
print("=" * 60)

if jobs:
    print("\nFirst 5 jobs:")
    for i, job in enumerate(jobs[:5], 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Salary: {job['salary']}")
        print(f"   URL: {job['url']}")
else:
    print("\nNo jobs found!")
