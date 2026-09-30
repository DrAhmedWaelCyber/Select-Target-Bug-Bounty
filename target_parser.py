"""
Target Parser Module for Select-Target
Cleans, normalizes, and filters targets into Wildcards and Domains.
Developed by: Ahmed Wael
"""

import re
from urllib.parse import urlparse

# Regex patterns for accurate identification
WILDCARD_PATTERN = re.compile(r'(\*\.[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)+)')
DOMAIN_PATTERN = re.compile(r'^([a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$')

# Excluded keywords in asset types or identifiers
EXCLUDED_TYPES = {
    "ANDROID", "IOS", "GOOGLE_PLAY_APP_ID", "APPLE_STORE_APP_ID",
    "SOURCE_CODE", "EXECUTABLE", "BINARY", "SMART_CONTRACT",
    "HARDWARE", "CIDR", "IP_ADDRESS", "IP-ADDRESS", "OTHER"
}

NON_DOMAIN_INDICATORS = [
    " ", "/", "\\", "@", ":", ";", "<", ">", "{", "}", "[", "]",
    "github.com", "gitlab.com", "bitbucket.org", "play.google.com",
    "apps.apple.com"
]

def clean_target_string(raw_target: str) -> str:
    """
    Strips protocols, trailing slashes, paths, and extraneous text.
    """
    if not raw_target:
        return ""
    
    target = str(raw_target).strip()
    
    # Check if there is an embedded wildcard first (e.g. "*.example.com (some notes)")
    wildcard_match = WILDCARD_PATTERN.search(target)
    if wildcard_match:
        return wildcard_match.group(1).lower()
    
    # Remove protocol if present
    if target.startswith(("http://", "https://")):
        try:
            parsed = urlparse(target)
            target = parsed.netloc or parsed.path
        except Exception:
            target = re.sub(r'^https?://', '', target)
            
    # Remove port numbers (e.g., example.com:8443)
    target = re.sub(r':\d+$', '', target)
    
    # Remove paths and query params
    target = target.split('/')[0].split('?')[0].split('#')[0].strip()
    
    # Clean surrounding quotes or brackets
    target = target.strip("'\"`()[]{}.,* \t\n\r")
    
    return target.lower()

def classify_target(raw_identifier: str, asset_type: str = "") -> dict:
    """
    Analyzes an asset identifier and type, returning classification:
    - category: 'wildcard' | 'domain' | 'invalid'
    - clean_target: standardized hostname or wildcard string
    """
    raw_str = str(raw_identifier or "").strip()
    type_str = str(asset_type or "").upper().strip()
    
    # Quick filter on known non-web asset types
    for ex in EXCLUDED_TYPES:
        if ex in type_str:
            return {"category": "invalid", "target": ""}
            
    # Check for wildcard pattern anywhere in the string
    wildcard_match = WILDCARD_PATTERN.search(raw_str)
    if wildcard_match:
        cleaned = wildcard_match.group(1).lower()
        return {"category": "wildcard", "target": cleaned}
        
    # Check if raw target starts with *.
    if raw_str.startswith("*."):
        cleaned = clean_target_string(raw_str)
        if cleaned:
            return {"category": "wildcard", "target": f"*.{cleaned}"}
            
    # Clean single domain
    cleaned = clean_target_string(raw_str)
    if not cleaned:
        return {"category": "invalid", "target": ""}
        
    # Validate if it is a legitimate domain name
    if DOMAIN_PATTERN.match(cleaned):
        # Discard false positives (IPs, numbers only, etc.)
        parts = cleaned.split('.')
        if len(parts) >= 2 and not all(p.isdigit() for p in parts):
            return {"category": "domain", "target": cleaned}
            
    return {"category": "invalid", "target": ""}

def parse_program_targets(program: dict, platform: str) -> list:
    """
    Extracts all valid in-scope targets for a given program.
    """
    results = []
    in_scope = program.get("targets", {}).get("in_scope", [])
    
    # Extract Program metadata
    prog_name = program.get("name") or program.get("handle") or "Unknown"
    prog_url = program.get("url") or ""
    
    # Cash bounty verification
    offers_bounty = False
    max_payout = 0
    
    if platform == "hackerone":
        offers_bounty = bool(program.get("offers_bounties", False))
        prog_url = prog_url or f"https://hackerone.com/{program.get('handle', '')}"
    elif platform == "bugcrowd":
        payout = program.get("max_payout", 0)
        if isinstance(payout, (int, float)) and payout > 0:
            offers_bounty = True
            max_payout = payout
        prog_url = prog_url or program.get("url", "")
    elif platform == "yeswehack":
        max_b = program.get("max_bounty", 0)
        if isinstance(max_b, (int, float)) and max_b > 0:
            offers_bounty = True
            max_payout = max_b
        prog_url = prog_url or f"https://yeswehack.com/programs/{program.get('id', '')}"
        
    for item in in_scope:
        # Check bounty eligibility if specifically marked on the asset
        if "eligible_for_bounty" in item and item["eligible_for_bounty"] is False:
            continue
            
        identifier = item.get("asset_identifier") or item.get("target") or item.get("uri") or ""
        asset_type = item.get("asset_type") or item.get("type") or item.get("category") or ""
        
        classification = classify_target(identifier, asset_type)
        if classification["category"] in ("wildcard", "domain"):
            results.append({
                "identifier": classification["target"],
                "category": classification["category"],
                "raw_identifier": identifier,
                "asset_type": asset_type,
                "program": prog_name,
                "platform": platform,
                "program_url": prog_url,
                "offers_bounty": offers_bounty,
                "max_payout": max_payout,
                "raw_program": program
            })
            
    return results
