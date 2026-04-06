"""Common scraper orchestration for AI Job Hunter."""

import asyncio
import logging
import os
import random
import time
from urllib.parse import urlparse
from typing import Any, Dict, List

from scrapers.internshala_scraper import scrape_internshala_jobs
from scrapers.naukri_scraper import scrape_naukri_jobs
from scrapers.shine_scraper import ShineScraper
from scrapers.timesjobs_scraper import TimesJobsScraper
from scrapers.unstop_scraper import scrape_unstop_jobs
from scrapers.free_portals_scraper import scrape_free_job_portals
from scrapers.job4freshers_scraper import scrape_job4freshers_jobs
from scrapers.linkedin_scraper import scrape_linkedin_jobs
from scrapers.foundit_scraper import scrape_foundit_jobs
from scrapers.talentd_scraper import scrape_talentd_jobs
from scrapers.wellfound_scraper import scrape_wellfound_jobs
from scrapers.placementdrive_scraper import scrape_placementdrive_jobs
from scrapers.jobfound_scraper import scrape_jobfound_jobs

logger = logging.getLogger(__name__)


def is_valid_apply_link(link: str) -> bool:
    """Return True for usable external apply links; reject placeholders."""
    if not link:
        return False

    link = str(link).strip()
    if not link.startswith(("http://", "https://")):
        return False

    try:
        parsed = urlparse(link)
    except Exception:
        return False

    host = (parsed.netloc or "").lower()
    if not host:
        return False

    blocked_hosts = {
        "example.com",
        "www.example.com",
        "localhost",
        "127.0.0.1",
    }
    if host in blocked_hosts:
        return False

    return True


def normalize_job(job: Dict[str, Any], source_name: str) -> Dict[str, Any]:
    """Normalize job dictionaries across sources to a consistent schema."""
    title = job.get("title") or job.get("job_title") or job.get("position") or "Job Opportunity"
    link = job.get("link") or job.get("url") or job.get("apply_link") or ""
    normalized = {
        "title": title,
        "job_title": title,
        "company": job.get("company") or job.get("organization") or "Unknown",
        "location": job.get("location") or job.get("city") or "India",
        "description": job.get("description") or job.get("summary") or "",
        "requirements": job.get("requirements") or job.get("eligibility") or "",
        "experience": job.get("experience") or job.get("experience_range") or "0-1 years",
        "salary_min": job.get("salary_min") or job.get("salary_from") or 0,
        "salary_max": job.get("salary_max") or job.get("salary_to") or 0,
        "salary_text": job.get("salary_text") or job.get("salary") or "",
        "job_type": job.get("job_type") or job.get("category") or "Job",
        "link": link,
        "apply_link": link,
        "source": job.get("source") or source_name.title(),
        "platform": job.get("platform") or source_name.title(),
        "posted_date": job.get("posted_date", ""),
        "keywords_matched": job.get("keywords_matched", []),
        "ats_score": job.get("ats_score", 0),
    }
    return normalized



def generate_realistic_jobs(query_list: List[str], profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate realistic fallback jobs when direct scraping is unavailable."""
    jobs: List[Dict[str, Any]] = []
    locations = profile.get("preferred_locations", ["India", "Remote"])
    locations = [loc for loc in locations if loc]
    if not locations:
        locations = ["India", "Remote"]

    selected_locations = locations[:3]
    random.shuffle(selected_locations)

    for idx, query in enumerate(query_list[:3], start=1):
        for location in selected_locations:
            title = query.title()
            jobs.append(
                {
                    "title": f"{title} - Intern / Entry Role",
                    "company": f"{query.title().split()[0]} Labs Pvt Ltd",
                    "location": location,
                    "description": (
                        f"Hiring for {query}. This role is suitable for CSE students and freshers interested in "
                        "hands-on development, data analytics, or research."
                    ),
                    "requirements": "SQL, Python, Linux, communication, teamwork.",
                    "experience": "0-1 years",
                    "link": f"https://example.com/jobs/{query.replace(' ', '-').lower()}/{idx}",
                    "source": "Fallback",
                    "platform": "Synthetic",
                }
            )

    return jobs


def scrape_shine_jobs(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    return ShineScraper.scrape(profile)


def scrape_timesjobs_jobs(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    return TimesJobsScraper.scrape(profile)


def scrape_jobs_for_profile(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Scrape jobs for the given role profile from non-LinkedIn sources."""
    queries = profile.get("queries", {})
    all_jobs: List[Dict[str, Any]] = []

    source_handlers = {
        "naukri": scrape_naukri_jobs,
        "internshala": scrape_internshala_jobs,
        "shine": scrape_shine_jobs,
        "timesjobs": scrape_timesjobs_jobs,
        "unstop": scrape_unstop_jobs,
        "free_portals": scrape_free_job_portals,
        "job4freshers": scrape_job4freshers_jobs,
        "linkedin": scrape_linkedin_jobs,
        "foundit": scrape_foundit_jobs,
        "talentd": scrape_talentd_jobs,
        "wellfound": scrape_wellfound_jobs,
        "placementdrive": scrape_placementdrive_jobs,
        "jobfound": scrape_jobfound_jobs,
    }

    allow_fallback_jobs = os.getenv("ALLOW_FALLBACK_JOBS", "0") == "1"

    for source, query_list in queries.items():
        if not query_list:
            continue

        try:
            if source in source_handlers:
                source_jobs = source_handlers[source](profile)
            else:
                source_jobs = generate_realistic_jobs(query_list, profile)

            source_jobs = [normalize_job(job, source) for job in source_jobs]

            if source_jobs:
                logger.info(f"✅ Collected {len(source_jobs)} jobs from {source}")
            else:
                if allow_fallback_jobs:
                    logger.warning(f"⚠️ No jobs returned from {source}; using fallback generation")
                    source_jobs = [normalize_job(job, source) for job in generate_realistic_jobs(query_list, profile)]
                else:
                    logger.warning(f"⚠️ No jobs returned from {source}; fallback generation disabled")

            all_jobs.extend(source_jobs)

        except Exception as exc:
            logger.warning(f"Error collecting jobs from {source}: {exc}")
            if allow_fallback_jobs:
                all_jobs.extend([normalize_job(job, source) for job in generate_realistic_jobs(query_list, profile)])

        time.sleep(random.uniform(0.5, 1.5))

    # Keep only entries with usable apply links.
    valid_jobs = [job for job in all_jobs if is_valid_apply_link(job.get("apply_link") or job.get("link"))]
    dropped = len(all_jobs) - len(valid_jobs)
    if dropped > 0:
        logger.info(f"🔗 Dropped {dropped} jobs without valid apply links")

    if not valid_jobs and allow_fallback_jobs:
        logger.warning("No jobs were collected from configured sources. Generating fallback jobs...")
        fallback_queries = [q for query_list in queries.values() for q in query_list]
        valid_jobs = [normalize_job(job, "fallback") for job in generate_realistic_jobs(fallback_queries, profile)]
        valid_jobs = [job for job in valid_jobs if is_valid_apply_link(job.get("apply_link") or job.get("link"))]

    return valid_jobs
