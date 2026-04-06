import json
from typing import Dict, List, Any


def build_claude_prompt(jobs: List[Dict[str, Any]], profile: Dict[str, Any], max_jobs: int = 5) -> str:
    """
    Build a Claude prompt for job evaluation based on user profile and scraped jobs.
    OPTIMIZED for lower token usage with OpenRouter free tier.
    
    Args:
        jobs: List of job dictionaries with title, company, location, description, etc.
        profile: User profile containing role_key, target_level, location preferences, etc.
        max_jobs: Max jobs to include (default 5 to save tokens)
    
    Returns:
        Formatted prompt string for Claude API
    """
    role = profile.get("role_key", "Data Analyst").replace("_", " ").title()
    target_level = profile.get("target_level", "entry-level")
    
    # OPTIMIZED: Shorter, more concise prompt to fit token limits
    prompt = f"""Job Fit Analysis for {role} ({target_level})

For each job: Score (0-10), Why it fits, Missing skills, Top tip, Recommendation (APPLY_NOW/LATER/SKIP)

Jobs:
"""
    
    # Limit jobs to reduce token usage
    limited_jobs = jobs[:max_jobs] if len(jobs) > max_jobs else jobs
    
    for idx, job in enumerate(limited_jobs, 1):
        title = job.get("title", "N/A")
        company = job.get("company", "N/A")
        location = job.get("location", "N/A")
        desc = job.get("description", "")[:80]  # Short description only
        
        prompt += f"{idx}. {title} @ {company} ({location}): {desc}\n"
    
    prompt += f"\nAnalyze these {len(limited_jobs)} jobs. Output: Score, fit reason, gaps, tip, recommendation for each."
    
    if len(jobs) > max_jobs:
        prompt += f"\n\nNote: Showing top {max_jobs} of {len(jobs)} jobs to save token usage."
    
    return prompt


def build_interview_prep_prompt(job: Dict[str, Any], profile: Dict[str, Any]) -> str:
    """
    Build a Claude prompt for interview preparation - OPTIMIZED for token usage.
    """
    title = job.get("title", "N/A")
    company = job.get("company", "N/A")
    
    prompt = f"""Interview Prep: {title} @ {company}

Quick prep:
1. 5 key technical questions (with brief answers)
2. 3 behavioral questions (STAR format)
3. 3 smart questions to ask them
4. Top 3 tips to stand out

Be concise and actionable."""
    
    return prompt


def build_coding_interview_prompt(topic: str = "SQL") -> str:
    """
    Build a Claude prompt for coding interview prep - OPTIMIZED for tokens.
    """
    prompt = f"""{topic} Interview Prep

Give me 3 essential {topic} problems for entry-level interviews:
- Problem statement
- Example input/output  
- Key tip (don't solve it, just hint)

Then: Top 5 {topic} concepts to know.
Finally: 3 common mistakes.

Be brief and actionable."""
    
    return prompt


def build_recruiter_communication_prompt(context: str = "outreach") -> str:
    """
    Build a Claude prompt for recruiter communication - OPTIMIZED for tokens.
    """
    if context == "outreach":
        return """Cold Email Template - Data Analyst Role

Give me 3 templates (each 50-75 words):
1. LinkedIn connection message
2. Cold email to recruiter  
3. Job application follow-up

Make them personalized, professional, concise."""
        
    elif context == "followup":
        return """Follow-up Email - After Application

Give me 2 templates:
1. 1-week follow-up (no response)
2. 2-week follow-up (still waiting)

Each 40-60 words. Professional, not pushy."""
        
    elif context == "negotiation":
        return """Salary Negotiation Email

Give me 1 template to professionally counter-offer salary.
50-75 words. Also list 3 things negotiable besides salary."""
        
    elif context == "rejection_handling":
        return """Rejection Response Email

Give me 1 professional response template to rejection (50 words).
Then: How to ask for feedback + 1 follow-up template."""
    
    return "Unknown context"


def build_resume_optimization_prompt(profile: Dict[str, Any]) -> str:
    """
    Build a Claude prompt for resume optimization - OPTIMIZED for tokens.
    """
    role = profile.get("role_key", "Data Analyst")
    
    return f"""Resume Optimization for {role} Roles

Quick analysis of my resume:
1. Top 10 ATS keywords I should add
2. Rewrite 3 weak bullet points (strong, with metrics)
3. What skills section should list (5-7 skills)
4. Format tips for {role} resumes
5. One thing to fix immediately

Be specific, actionable, brief."""


def build_skill_development_prompt(profile: Dict[str, Any]) -> str:
    """
    Build a Claude prompt for skill development - OPTIMIZED for tokens.
    """
    return """3-Month Skill Development Plan

Create concise plan:
1. Priority skills (ranked by job demand) - top 5
2. Month 1: Focus on [X skill] + practice
3. Month 2: Learn [Y skill] + build project  
4. Month 3: Polish skills + interview prep
5. 1 portfolio project idea (beginner-friendly)
6. Top 5 daily habits (15-30 min commitment)

Be practical and achievable."""


def build_cover_letter_prompt(job: Dict[str, Any], profile: Dict[str, Any]) -> str:
    """
    Build a Claude prompt for personalized cover letters - OPTIMIZED for tokens.
    """
    company = job.get("company", "N/A")
    title = job.get("title", "N/A")
    
    return f"""Write Cover Letter: {title} @ {company}

200-word cover letter with:
1. Hook (why this role?)
2. Why I fit (2-3 skills match)
3. Unique value (what I bring)
4. Call to action

Professional tone, specific to company if possible."""


def build_talent_acquisition_strategy_prompt(profile: Dict[str, Any]) -> str:
    """
    Build a Claude prompt for overall strategy - OPTIMIZED for tokens.
    """
    return """90-Day Job Search Strategy - CONCISE VERSION

Quick 90-day plan:

Month 1:
- Optimize resume + portfolio (1 project)
- Apply to 30 jobs
- Connect with 20 recruiters

Month 2:
- Build 2nd project
- 40 job applications  
- 10 informational interviews
- 3 mock interviews

Month 3:
- Final polish
- 20 targeted applications
- Interview prep focus
- Negotiate offers

Daily: 15 min outreach, 30 min learning, 30 min applications.

Give me: Week-by-week breakdown, daily habits, success metrics."""


def format_jobs_for_claude(jobs: List[Dict[str, Any]]) -> str:
    """
    Format jobs data as JSON for Claude input/output tracking.
    
    Args:
        jobs: List of job dictionaries
    
    Returns:
        JSON string representation of jobs
    """
    return json.dumps(
        {
            "jobs": jobs,
            "count": len(jobs),
            "status": "ready"
        },
        indent=2,
        default=str
    )


def get_all_prompt_types() -> Dict[str, str]:
    """
    Get all available prompt types and descriptions.
    
    Returns:
        Dictionary of prompt types with descriptions
    """
    return {
        "job_matching": "Job evaluation and matching",
        "interview_prep": "Interview preparation and practice",
        "coding_interview": "Coding interview preparation",
        "recruiter_outreach": "Recruiter communication and outreach",
        "resume_optimization": "Resume improvement for ATS",
        "skill_development": "Learning roadmap and skill development",
        "cover_letter": "Personalized cover letter generation",
        "talent_acquisition": "Overall career/job search strategy"
    }
