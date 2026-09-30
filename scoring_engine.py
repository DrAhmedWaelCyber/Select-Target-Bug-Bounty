"""
Intelligent Scoring Engine for Select-Target
Evaluates bug bounty programs and targets to identify the absolute best opportunities.
Developed by: Ahmed Wael
"""

from typing import Dict, List, Set
import random
from config import JUICY_KEYWORDS, SATURATED_GIANTS

def calculate_program_score(program: dict, platform: str) -> float:
    """
    Computes a base score for a bug bounty program based on payout,
    responsiveness, triage quality, and competition factors.
    """
    score = 0.0
    name = str(program.get("name") or program.get("handle") or "").lower()
    
    # 1. Saturation Penalty (Avoid hardened hyper-saturated targets)
    if any(giant in name for giant in SATURATED_GIANTS):
        score -= 150.0
        
    # 2. Managed Program Boost (Managed programs triage and pay faster)
    is_managed = (
        program.get("managed_program") is True or
        program.get("managed_by_bugcrowd") is True or
        platform == "yeswehack"  # YesWeHack natively provides managed triage
    )
    if is_managed:
        score += 35.0

    # 3. Payout Potential
    max_payout = 0
    if platform == "bugcrowd":
        max_payout = program.get("max_payout", 0) or 0
    elif platform == "yeswehack":
        max_payout = program.get("max_bounty", 0) or 0
    elif platform == "hackerone":
        if program.get("offers_bounties"):
            score += 60.0

    if isinstance(max_payout, (int, float)) and max_payout > 0:
        score += 50.0  # Cash bounty offered
        if 500 <= max_payout <= 3500:
            score += 45.0  # The sweet spot: lucrative yet accessible
        elif max_payout > 3500:
            score += 30.0

    # 4. Responsiveness Metrics (HackerOne specific)
    try:
        efficiency = float(program.get("response_efficiency_percentage") or 0)
        if efficiency >= 90:
            score += 40.0
        elif efficiency >= 75:
            score += 20.0
    except (ValueError, TypeError):
        pass

    # 5. Attack Surface Balance
    targets_data = program.get("targets", {})
    in_scope = targets_data.get("in_scope", [])
    out_of_scope = targets_data.get("out_of_scope", [])
    
    in_count = len(in_scope)
    out_count = len(out_of_scope)
    
    if in_count > 0:
        ratio = in_count / max(1, out_count)
        if ratio >= 5:
            score += 25.0
        elif ratio < 0.3:
            score -= 20.0

    return score

def calculate_target_juiciness(target_identifier: str, category: str) -> tuple[float, List[str]]:
    """
    Computes juiciness score for a specific domain/wildcard based on
    sensitive environment keywords, depth, and attack surface.
    Returns: (score, list_of_matching_tags)
    """
    score = 0.0
    identifier = str(target_identifier).lower()
    matched_tags = []

    # Wildcards have vastly larger attack surfaces than single fixed endpoints
    if category == "wildcard":
        score += 80.0
        matched_tags.append("WILDCARD")

    # Keyword analysis
    keyword_weights = {
        "staging.": (140, "STAGING"),
        "stg.": (140, "STAGING"),
        "uat.": (130, "UAT"),
        "sandbox.": (120, "SANDBOX"),
        "dev.": (130, "DEV"),
        "beta.": (110, "BETA"),
        "demo.": (100, "DEMO"),
        "api.": (130, "API"),
        "graphql": (120, "GRAPHQL"),
        "auth.": (130, "AUTH"),
        "sso.": (130, "SSO"),
        "login.": (120, "LOGIN"),
        "identity.": (120, "IDENTITY"),
        "admin.": (125, "ADMIN"),
        "portal.": (110, "PORTAL"),
        "console.": (110, "CONSOLE"),
        "dashboard.": (105, "DASHBOARD"),
        "vpn.": (125, "VPN"),
        "internal.": (130, "INTERNAL"),
        "corp.": (115, "CORP"),
        "pay": (125, "PAYMENTS"),
        "wallet": (125, "FINTECH"),
        "billing": (120, "BILLING"),
        "checkout": (120, "CHECKOUT"),
        "k8s": (100, "K8S"),
        "aws": (100, "AWS"),
        "cloud": (95, "CLOUD")
    }

    for kw, (weight, tag) in keyword_weights.items():
        if kw in identifier:
            score += weight
            if tag not in matched_tags:
                matched_tags.append(tag)

    # Subdomain depth: deeper targets are less examined by mass scanners
    clean_id = identifier.replace("*.", "")
    dot_count = clean_id.count('.')
    if dot_count >= 2:
        score += min(60.0, (dot_count - 1) * 20.0)
        matched_tags.append(f"DEPTH-{dot_count}")

    # Root domain penalty if single domain with www
    if identifier.startswith("www."):
        score -= 30.0

    return score, matched_tags

def score_and_rank_targets(targets: List[dict], previous_known_ids: Set[str] = None) -> List[dict]:
    """
    Ranks targets using program health, target juiciness, and freshness boost.
    """
    if previous_known_ids is None:
        previous_known_ids = set()

    ranked_targets = []
    
    for t in targets:
        prog = t.get("raw_program", {})
        platform = t.get("platform", "")
        identifier = t.get("identifier", "")
        category = t.get("category", "")

        prog_score = calculate_program_score(prog, platform)
        juicy_score, tags = calculate_target_juiciness(identifier, category)

        total_score = prog_score + juicy_score
        is_brand_new = bool(previous_known_ids and identifier not in previous_known_ids)

        if is_brand_new:
            total_score += 1000.0  # Massive priority boost for fresh targets
            tags.insert(0, "🔥 NEW TARGET")

        # Add a random jitter to shuffle targets with similar scores each run
        jitter = random.uniform(0.0, 15.0)
        total_score += jitter

        t_copy = dict(t)
        t_copy["score"] = round(total_score, 1)
        t_copy["program_score"] = round(prog_score, 1)
        t_copy["juicy_score"] = round(juicy_score, 1)
        t_copy["tags"] = tags
        t_copy["is_new"] = is_brand_new
        ranked_targets.append(t_copy)

    # Sort descending by final score
    ranked_targets.sort(key=lambda x: x["score"], reverse=True)
    return ranked_targets
