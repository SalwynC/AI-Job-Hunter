#!/usr/bin/env python3
import yaml
from pathlib import Path

yaml_file = Path("roles/role_profiles.yaml")
with open(yaml_file, 'r') as f:
    data = yaml.safe_load(f)

# Fix all boost_keywords that are lists
for role_name, role_config in data['roles'].items():
    boost_keywords = role_config.get('boost_keywords', [])
    
    # If it's already a dict, skip
    if isinstance(boost_keywords, dict):
        continue
    
    # If it's a list, convert to dict
    if isinstance(boost_keywords, list):
        if len(boost_keywords) >= 2:
            new_boost = {
                'high': boost_keywords[:len(boost_keywords)//2],
                'medium': boost_keywords[len(boost_keywords)//2:]
            }
        else:
            new_boost = {'high': boost_keywords, 'medium': []}
        
        role_config['boost_keywords'] = new_boost

# Write back
with open(yaml_file, 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)

print("✅ All boost_keywords fixed!")
