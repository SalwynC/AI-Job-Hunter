import os
import json
import logging
from google import genai
from typing import Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)

# Configure Gemini with zero-cost API Key structure
# We expect GEMINI_API_KEY to be set in the .env-analyst file
API_KEY = os.getenv("GEMINI_API_KEY", "")

def score_job_with_gemini(job: Dict[str, Any], profile: Dict[str, Any]) -> float:
    """
    Zero-Cost AI scoring: Leverages Gemini 1.5 Flash to calculate ATS scores
    instead of poor static regexes. Fast and 100% Free tier (1500 limit/day).
    """
    if not API_KEY:
        # Fallback to base score if no API Key provided yet
        logger.warning("No GEMINI_API_KEY provided. Falling back to 5.0 score.")
        return 5.0

    try:
        client = genai.Client(api_key=API_KEY)
        
        prompt = f"""
        Act as a strict tech recruiter evaluating roles for a 2026 CSE Graduate/Fresher from India.
        
        Role Profile: {profile.get('role_key', 'Analyst')}
        Target Skills: {', '.join(profile.get('target_keywords', []))}
        
        Job Title: {job.get('title', '')}
        Job Description: {str(job.get('description', ''))[:1200]}
        
        CRITICAL EVALUATION RULES:
        1. EXPERIENCE DEDUCTION: If the job strictly requires 2+ years of experience or is explicitly "Senior", output a very low score (0.0 to 3.0 maximum).
        2. FRESHER / 2026 BOOST: If the job mentions "Fresher", "0-1 years", "2026 batch", "Intern", or "Entry level", dramatically boost the score to (8.0 to 10.0).
        3. SKILL MATCH: Verify if the job requires the Target Skills (e.g., MERN, Data Analysis, SQL).
        
        Analyze the job strictly against these rules.
        Reply with a single float number between 0.0 to 10.0 representing the ATS match score.
        Example reply: 8.5
        """
        
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        text = response.text.strip().replace("Score:", "").replace("score:", "").strip()
        
        # Try to extract the first valid float
        import re
        match = re.search(r'\d+(\.\d+)?', text)
        if match:
            score = float(match.group())
            return min(10.0, max(0.0, score))
        return 5.0 # fallback
        
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        return 5.0

def score_jobs(df: pd.DataFrame, profile: Dict[str, Any]) -> pd.DataFrame:
    """
    Applies Gemini AI scoring to the entire batch of jobs.
    """
    if df.empty:
        return df

    df = df.copy()
    logger.info(f"🧠 Scoring {len(df)} jobs using Gemini 1.5 Flash (100% Free Tier)")
    
    # We apply scoring only on non-empty rows
    df["score"] = df.apply(lambda row: score_job_with_gemini(row.to_dict(), profile), axis=1)
    df["profile_role"] = profile.get("role_key", "unknown")
    
    return df
