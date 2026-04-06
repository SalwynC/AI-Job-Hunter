"""
Job Posting Analyzer - Deep Parsing Extractor
Parses raw job descriptions to extract structured fields:
- Required qualifications (degrees, certifications)
- Technical skills (programming languages, frameworks)
- Responsibilities/duties
- Experience level (years)
- Employment type (internship, full-time, contract)
- Fresherness (passout year, 2024/2025/2026)
- Location details
- Salary range
"""

import re
from typing import Dict, Any, List, Optional


DEGREE_PATTERNS = [
    (r'\b(?:B\.?Tech|B\.?E\.?|BE|BTech)\b', 'B.Tech/B.E.'),
    (r'\b(?:B\.?Sc\.?\s*(?:CS|IT|Computer Science|Computers))\b', 'B.Sc CS'),
    (r'\bBCA\b', 'BCA'),
    (r'\bB\.?Com\b', 'B.Com'),
    (r'\bM\.?Tech\b', 'M.Tech'),
    (r'\bM\.?CA\b', 'MCA'),
    (r'\bM\.?Sc\b', 'M.Sc'),
    (r'\bM\.?B\.?A\b', 'MBA'),
    (r'\bB\.?A\.?\b', 'B.A.'),
    (r'\b10\+2\b', '10+2 / PUC'),
    (r'\bany\b.*\b(?:degree|bachelor)\b', 'Any Bachelor\'s'),
    (r'\bgraduate\b', 'Graduate'),
    (r'\b(?:postgraduate|PG)\b', 'Postgraduate'),
]

SKILL_PATTERNS = [
    (r'\bPython\b', 'Python'),
    (r'\bJava\b(?!script)', 'Java'),
    (r'\bJavaScript\b|\bJS\b', 'JavaScript'),
    (r'\bTypeScript\b|\bTS\b', 'TypeScript'),
    (r'\bReact\b|\bReact\.js\b|\bReactJS\b', 'React'),
    (r'\bNode\.js\b|\bNodeJS\b|\bNode\b', 'Node.js'),
    (r'\bDjango\b', 'Django'),
    (r'\bFlask\b', 'Flask'),
    (r'\bFastAPI\b', 'FastAPI'),
    (r'\bSQL\b', 'SQL'),
    (r'\bMySQL\b', 'MySQL'),
    (r'\bPostgreSQL\b', 'PostgreSQL'),
    (r'\bMongoDB\b', 'MongoDB'),
    (r'\bPostgreSQL\b', 'PostgreSQL'),
    (r'\bSQLite\b', 'SQLite'),
    (r'\bHTML\b', 'HTML'),
    (r'\bCSS\b', 'CSS'),
    (r'\bGit\b', 'Git'),
    (r'\bDocker\b', 'Docker'),
    (r'\bKubernetes\b', 'Kubernetes'),
    (r'\bAWS\b', 'AWS'),
    (r'\bAzure\b', 'Azure'),
    (r'\bGCP\b', 'Google Cloud'),
    (r'\bLinux\b', 'Linux'),
    (r'\bDSA\b', 'Data Structures & Algorithms'),
    (r'\bOOPs?\b', 'OOP'),
    (r'\bREST\b.*\bAPI\b', 'REST API'),
    (r'\bGraphQL\b', 'GraphQL'),
    (r'\bMachine Learning\b|\bML\b', 'Machine Learning'),
    (r'\bDeep Learning\b', 'Deep Learning'),
    (r'\bNLP\b', 'NLP'),
    (r'\bTableau\b', 'Tableau'),
    (r'\bPower BI\b', 'Power BI'),
    (r'\bExcel\b', 'Excel'),
    (r'\bPandas\b', 'Pandas'),
    (r'\bNumPy\b', 'NumPy'),
    (r'\bScikit\b', 'Scikit-learn'),
    (r'\bTensorFlow\b', 'TensorFlow'),
    (r'\bPyTorch\b', 'PyTorch'),
    (r'\bC\+\+\b', 'C++'),
    (r'\bC#', 'C#'),
    (r'\bSwift\b', 'Swift'),
    (r'\bKotlin\b', 'Kotlin'),
    (r'\bGo\b', 'Go'),
    (r'\bRust\b', 'Rust'),
    (r'\bPHP\b', 'PHP'),
    (r'\bRuby\b', 'Ruby'),
    (r'\bRuby on Rails\b', 'Ruby on Rails'),
    (r'\bSpring Boot\b', 'Spring Boot'),
    (r'\bHibernate\b', 'Hibernate'),
    (r'\bAndroid\b', 'Android'),
    (r'\biOS\b', 'iOS'),
    (r'\bFlutter\b', 'Flutter'),
    (r'\bAndroid\b', 'Android'),
    (r'\biOS\b', 'iOS'),
    (r'\bFirebase\b', 'Firebase'),
    (r'\bRedis\b', 'Redis'),
    (r'\bKafka\b', 'Apache Kafka'),
    (r'\bElasticsearch\b', 'Elasticsearch'),
    (r'\bJira\b', 'Jira'),
]

RESPONSIBILITY_PATTERNS = [
    r'design\b(?:\s+and)?\s+(?:|develop\b)',
    r'develop\b(?:\s+and)?\s+(?:|test\b)',
    r'build\b(?:\s+and)?\s+(?:|maintain\b)',
    r'te(?:?:st|esting)',
    r'monitor\b',
    r'implement(?:ed|ing|s)',
    r'manage\b',
    r'create\b',
    r'maintain\b',
    r'analyze\b',
    r'optimize\b',
    r'debug\b',
    r'troubleshoot\b',
]

def extract_degree(text: str) -> str:
    """Extract required degree from job text."""
    for pattern, label in DEGREE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return label
    return "Not specified"

def extract_skills(text: str) -> List[str]:
    """Extract all technical skills mentioned."""
    skills = []
    for pattern, label in SKILL_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            if label not in skills:
                skills.append(label)
    return skills

def extract_experience_years(text: str) -> Dict[str, Optional[int]]:
    """Extract experience range from text like '2-4 years' or 'fresher'."""
    for marker in ["fresher", "fresher", "recent graduate", "recent grad"]:
        if marker in text.lower():
            return {"min": 0, "max": 0, "label": "Fresher (0 years)"}

    match = re.search(r'(\d+)\s*[-–]\s*(\d+)\s*(?:years?|yrs)', text.lower())
    if match:
        return {
            "min": int(match.group(1)),
            "max": int(match.group(2)),
            "label": f"{match.group(1)}-{match.group(2)} years"
        }

    match = re.search(r'(\d+)\s*(?:years?|yrs)', text.lower())
    if match:
        return {"min": 0, "max": int(match.group(1)), "label": f"0-{match.group(1)} years"}

    return {"min": None, "max": None, "label": "Not specified"}

def extract_employment_type(text: str) -> str:
    """Determine if it's internship, full-time, contract, etc."""
    text_lower = text.lower()
    if any(kw in text_lower for kw in ["intern", "trainee", "apprentice"]):
        return "Internship"
    if "contract" in text_lower:
        return "Contract"
    if "part-time" in text_lower or "part time" in text_lower:
        return "Part-Time"
    return "Full-Time"

def extract_fresherness(text: str) -> str:
    """Detect if job is for freshers and target passout year."""
    text_lower = text.lower()
    if "fresher" in text_lower or "freshers" in text_lower:
        # Look for passout year
        year_match = re.search(r'(202[456])', text_lower)
        if year_match:
            return f"Fresher (20{year_match.group(1)} Passout)"
        return "Fresher (Any Year)"
    year_match = re.search(r'(202[456])\s*(?:passout|batch|graduate)', text_lower)
    if year_match:
        return f"20{year_match.group(1)} Passout"
    return "Experienced / Not Fresher"

def extract_responsibilities(text: str) -> List[str]:
    """Extract key responsibilities/duties from job description."""
    duties = []
    for pattern in RESPONSIBILITY_PATTERNS:
        if re.search(pattern, text.lower()):
            duties.append(pattern.split(r'\b')[0].replace(r'\b', ''))

    # Clean up
    cleaned = []
    for duty in duties:
        duty = duty.strip()
        if duty and len(duty) < 25:
            cleaned.append(duty)
    return cleaned if cleaned else ["Not specified"]

def extract_salary_range(text: str) -> Dict[str, Optional[float]]:
    """Extract salary range from text like '4-8 LPA' or '₹8,00,000'."""
    # Standard LPA format
    match = re.search(r'(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*(?:L|LPA|lpa)', text, re.IGNORECASE)
    if match:
        return {"min_lakh": float(match.group(1)), "max_lakh": float(match.group(2))}

    match = re.search(r'UP\s*TO\s+(\d+(?:\.\d+)?)\s*(?:L|LPA)', text, re.IGNORECASE)
    if match:
        return {"min_lakh": 0.0, "max_lakh": float(match.group(1))}

    # Rupee format like '₹4-8 LPA'
    match = re.search(r'₹?\s*(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*(?:L|LPA)', text)
    if match:
        return {"min_lakh": float(match.group(1)), "max_lakh": float(match.group(2))}

    # Single number like '8 LPA'
    match = re.search(r'(\d+(?:\.\d+)?)\s*(?:L|LPA|lpa)', text.lower())
    if match:
        return {"min_lakh": float(match.group(1)), "max_lakh": float(match.group(1))}

    return {"min_lakh": None, "max_lakh": None}


def analyze_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """Deep-parses and enriches a single job posting with structured fields."""
    # Combine all text fields for parsing
    all_text = f"{job.get('title', '')} {job.get('description', '')} {job.get('requirements', '')}"

    enriched = {
        **job,
        # New fields
        "qualification_required": extract_degree(all_text),
        "skills": extract_skills(all_text),
        "experience": extract_experience_years(all_text),
        "employment_type": extract_employment_type(all_text),
        "fresherness": extract_fresherness(all_text),
        "responsibilities": extract_responsibilities(all_text),
        "salary_parsed": extract_salary_range(all_text),
    }

    return enriched


def analyze_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze and enrich all jobs in a list."""
    parsed = []
    for job in jobs:
        parsed.append(analyze_job(job))
    return parsed