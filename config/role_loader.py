import os
from pathlib import Path

import yaml


def load_role_profiles():
    role_file = Path(__file__).resolve().parents[1] / "roles" / "role_profiles.yaml"
    if not role_file.exists():
        raise FileNotFoundError(f"Role profiles file not found: {role_file}")

    with role_file.open("r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream)

    roles = config.get("roles", {})
    default_role = config.get("default_role", "data_analyst")
    return roles, default_role


def validate_profile(profile, role_name):
    """Validate that a profile has all required fields."""
    required_fields = [
        "role_key",
        "target_keywords",
        "boost_keywords",
        "scoring_weights",
        "experience_range",
        "preferred_locations",
    ]
    
    missing_fields = [field for field in required_fields if field not in profile]
    
    if missing_fields:
        raise ValueError(
            f"Role profile '{role_name}' is missing required fields: {', '.join(missing_fields)}. "
            f"Please check roles/role_profiles.yaml"
        )


def load_role_profile(role_name=None):
    roles, default_role = load_role_profiles()
    target_role = role_name or os.getenv("TARGET_ROLE") or default_role
    profile = roles.get(target_role)
    if profile is None:
        raise ValueError(
            f"Role profile '{target_role}' not found. Available roles: {', '.join(sorted(roles.keys()))}"
        )

    profile = dict(profile)
    profile["role_key"] = target_role
    profile["default_role"] = default_role
    
    # Validate profile has all required fields
    validate_profile(profile, target_role)
    
    return profile
