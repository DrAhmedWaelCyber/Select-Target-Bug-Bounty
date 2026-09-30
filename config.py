"""
Select-Target Configuration Module
Developed by: Ahmed Wael
"""

import os
from pathlib import Path

# Tool Metadata
TOOL_NAME = "Select-Target"
DEVELOPER = "Ahmed Wael"
VERSION = "2.0.0 Pro"
DESCRIPTION = "Intelligent Bug Bounty Target Selector & Surface Engine"

# Base Directories
BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Data Sources (Real-time GitHub raw endpoints)
DATA_SOURCES = {
    "yeswehack": {
        "name": "YesWeHack",
        "url": "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/refs/heads/main/data/yeswehack_data.json",
        "cache_file": CACHE_DIR / "yeswehack_cache.json"
    },
    "bugcrowd": {
        "name": "Bugcrowd",
        "url": "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/refs/heads/main/data/bugcrowd_data.json",
        "cache_file": CACHE_DIR / "bugcrowd_cache.json"
    },
    "hackerone": {
        "name": "HackerOne",
        "url": "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/refs/heads/main/data/hackerone_data.json",
        "cache_file": CACHE_DIR / "hackerone_cache.json"
    }
}

# General history and selection persistence
HISTORY_FILE = CACHE_DIR / "hunted_history.json"
LAST_SYNC_FILE = CACHE_DIR / "last_sync.json"
ALL_CACHE_FILE = CACHE_DIR / "combined_targets.json"

# Network Settings
REQUEST_TIMEOUT = 30  # seconds per platform request
MAX_WORKERS = 3       # Parallel fetch workers

# High-yield / Juicy keywords for scoring
JUICY_KEYWORDS = [
    "api.", "dev.", "stg.", "staging.", "test.", "sandbox.",
    "corp.", "internal.", "admin.", "uat.", "demo.", "vpn.",
    "beta.", "graphql", "k8s", "aws", "ec2", "s3", "elastic",
    "cloud", "jira", "confluence", "auth", "sso", "login",
    "identity", "portal", "gateway", "service", "app.", "pay",
    "wallet", "checkout", "billing", "dashboard", "console"
]

# Saturated tech giants (heavy competition penalty)
SATURATED_GIANTS = [
    "google", "facebook", "meta", "microsoft", "apple", "paypal",
    "yahoo", "netflix", "amazon", "github", "uber", "twitter", "x.com"
]
