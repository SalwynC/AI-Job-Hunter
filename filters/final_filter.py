import re
import os
import pandas as pd


def filter_jobs(df, profile):
    if df.empty:
        return df

    df = df.copy()
    
    # Ensure required columns exist
    required_columns = ["description", "location"]
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""
    
    experience = profile.get("experience_range", {})
    min_years = experience.get("min_years")
    max_years = experience.get("max_years")

    def matches_experience(text):
        # Handle NaN, None, and non-string types safely
        if pd.isna(text) or text is None or not isinstance(text, str):
            return profile.get("experience_range", {}).get("accept_undefined", True)
        
        text = str(text).lower().strip()
        if not text:
            return profile.get("experience_range", {}).get("accept_undefined", True)
        
        match = re.search(r"(\d+)\+?\s*years?", text)
        if not match:
            return profile.get("experience_range", {}).get("accept_undefined", True)
        
        years = int(match.group(1))
        if min_years is not None and years < min_years:
            return False
        if max_years is not None and years > max_years:
            return False
        return True

    df["experience_match"] = df["description"].apply(matches_experience)
    df = df[df["experience_match"]]

    preferred_locations = profile.get("preferred_locations", [])
    if preferred_locations:
        lower_prefs = [str(loc).strip().lower() for loc in preferred_locations if loc]
        india_focus = "india" in lower_prefs
        excluded_global = [
            "usa", "united states", "united states of america", "canada", "uk",
            "united kingdom", "australia", "singapore", "germany", "france",
            "netherlands", "spain", "italy", "brazil", "mexico", "sweden",
            "switzerland", "uae",
        ]

        def matches_location(value):
            text = str(value or "").lower()
            if not text:
                return True
            if "remote" in text:
                return True
            if any(pref in text for pref in lower_prefs):
                return True
            if india_focus and not any(country in text for country in excluded_global):
                return True
            return False

        df["location_match"] = df["location"].apply(matches_location)
        df = df[df["location_match"]]

    # Enforce role relevance by requiring at least one target keyword in title/description/requirements.
    strict_role_match = os.getenv("STRICT_ROLE_MATCH", "1") == "1"
    target_keywords = [str(k).strip().lower() for k in profile.get("target_keywords", []) if str(k).strip()]

    if strict_role_match and target_keywords and not df.empty:
        def role_keyword_hits(row):
            text = " ".join([
                str(row.get("title", "")).lower(),
                str(row.get("description", "")).lower(),
                str(row.get("requirements", "")).lower(),
            ])
            return sum(1 for kw in target_keywords if kw in text)

        df["role_keyword_hits"] = df.apply(role_keyword_hits, axis=1)
        df = df[df["role_keyword_hits"] > 0]

    # Optional score floor for tighter matching in cloud runs.
    min_score = float(os.getenv("MIN_MATCH_SCORE", "1.0"))
    if "score" in df.columns and not df.empty:
        df = df[pd.to_numeric(df["score"], errors="coerce").fillna(0) >= min_score]

    if not df.empty:
        df = df.sort_values(by=["score"], ascending=False)

    return df
