import re
import os
from pathlib import Path


def clean_text(value):
    return str(value or "").lower()


def _extract_keywords(text):
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.\-]{2,}", clean_text(text))
    stop = {
        "with", "that", "from", "this", "have", "will", "your", "you", "our", "and", "the",
        "for", "are", "job", "role", "years", "year", "into", "about", "using", "required",
        "preferred", "experience", "skills", "skill", "must", "good", "ability", "work", "team",
    }
    return {w for w in words if w not in stop}


def _load_target_jd_keywords():
    jd_text = os.getenv("TARGET_JD_TEXT", "").strip()
    jd_file = os.getenv("TARGET_JD_FILE", "").strip()

    if not jd_text and jd_file:
        path = Path(jd_file)
        if path.exists() and path.is_file():
            try:
                jd_text = path.read_text(encoding="utf-8")
            except Exception:
                jd_text = ""

    return _extract_keywords(jd_text)


def score_job(job, profile):
    title = clean_text(job.get("title"))
    description = clean_text(job.get("description"))
    company = clean_text(job.get("company"))
    location = clean_text(job.get("location"))

    score = 0.0
    keywords = profile.get("target_keywords", [])
    boost_keywords = profile.get("boost_keywords", {})
    weights = profile.get("scoring_weights", {})

    if any(keyword.lower() in title for keyword in keywords):
        score += float(weights.get("title_match", 1.0)) * 2.0

    matches = sum(1 for keyword in keywords if keyword.lower() in description)
    score += min(matches * float(weights.get("keyword_match", 0.5)), 5.0)

    internship_markers = profile.get("internship_markers", {})
    internship_keywords = internship_markers.get("keywords", [])
    if any(marker.lower() in title or marker.lower() in description for marker in internship_keywords):
        score += float(weights.get("internship_tag", 0.5))

    if any(boost.lower() in title or boost.lower() in description for boost in boost_keywords.get("high", [])):
        score += 1.5
    if any(boost.lower() in title or boost.lower() in description for boost in boost_keywords.get("medium", [])):
        score += 0.8

    if profile.get("preferred_locations"):
        if any(loc.lower() in location for loc in profile["preferred_locations"]):
            score += 0.5

    if profile.get("preferred_industries"):
        industry_match = any(industry.lower() in description for industry in profile["preferred_industries"])
        if industry_match:
            score += 0.5

    jd_keywords = profile.get("_target_jd_keywords") or set()
    if jd_keywords:
        job_text = f"{title} {description} {clean_text(job.get('requirements'))}"
        jd_matches = sum(1 for kw in jd_keywords if kw in job_text)
        # Controlled boost to prioritize JD-relevant jobs without overpowering role scoring.
        score += min(jd_matches * 0.15, 2.0)

    return round(min(score, 10.0), 2)


def score_jobs(df, profile):
    if df.empty:
        return df

    df = df.copy()
    profile = dict(profile)
    profile["_target_jd_keywords"] = _load_target_jd_keywords()
    df["score"] = df.apply(lambda row: score_job(row.to_dict(), profile), axis=1)
    df["profile_role"] = profile["role_key"]
    return df
