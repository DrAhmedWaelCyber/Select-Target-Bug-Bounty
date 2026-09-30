"""
Data Manager Module for Select-Target
Handles live synchronization with GitHub endpoints, intelligent caching,
differential freshness analysis, and target catalog querying.
Developed by: Ahmed Wael
"""

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter

from config import (
    DATA_SOURCES,
    CACHE_DIR,
    HISTORY_FILE,
    LAST_SYNC_FILE,
    REQUEST_TIMEOUT,
    MAX_WORKERS
)
from target_parser import parse_program_targets
from scoring_engine import score_and_rank_targets

class TargetDataManager:
    def __init__(self):
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        self.history = self._load_json(HISTORY_FILE, default=[])
        self.sync_meta = self._load_json(LAST_SYNC_FILE, default={})

    def _load_json(self, path: Path, default=None):
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return default if default is not None else {}
        return default if default is not None else {}

    def _save_json(self, path: Path, data):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def check_github_update(self, platform_key: str) -> Tuple[bool, Optional[str]]:
        """
        Performs a fast HEAD request to check if the file on GitHub has changed via ETag.
        Returns: (needs_download: bool, remote_etag: str)
        """
        source = DATA_SOURCES.get(platform_key)
        if not source:
            return False, None

        cache_file = source["cache_file"]
        if not cache_file.exists():
            return True, None

        saved_etag = self.sync_meta.get(platform_key, {}).get("etag")
        try:
            head_resp = self.session.head(source["url"], timeout=10)
            remote_etag = head_resp.headers.get("ETag")
            if not saved_etag or remote_etag != saved_etag:
                return True, remote_etag
            return False, saved_etag
        except Exception:
            # Network failure on HEAD -> rely on cache if available
            return False, saved_etag

    def fetch_single_platform(self, platform_key: str, force_refresh: bool = False, progress_callback=None) -> Tuple[str, List[dict], bool]:
        """
        Fetches or loads platform data. Returns: (platform_key, raw_programs, is_updated)
        """
        source = DATA_SOURCES.get(platform_key)
        if not source:
            return platform_key, [], False

        cache_file = source["cache_file"]
        needs_download = force_refresh or not cache_file.exists()
        new_etag = None

        if not needs_download:
            needs_download, new_etag = self.check_github_update(platform_key)

        is_updated = False
        raw_programs = []

        if needs_download:
            if progress_callback:
                progress_callback(f"[bold cyan]Syncing {source['name']} with GitHub...[/bold cyan]")
            try:
                resp = self.session.get(source["url"], timeout=REQUEST_TIMEOUT)
                resp.raise_for_status()
                raw_programs = resp.json()
                
                # Save data to local cache
                self._save_json(cache_file, raw_programs)
                
                # Update ETag metadata
                etag = resp.headers.get("ETag") or new_etag or str(time.time())
                self.sync_meta[platform_key] = {
                    "etag": etag,
                    "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "count": len(raw_programs)
                }
                self._save_json(LAST_SYNC_FILE, self.sync_meta)
                is_updated = True
            except Exception as e:
                # If network fails, attempt fallback to cache
                if cache_file.exists():
                    raw_programs = self._load_json(cache_file, default=[])
                else:
                    raw_programs = []
        else:
            raw_programs = self._load_json(cache_file, default=[])

        return platform_key, raw_programs, is_updated

    def fetch_all_platforms(self, platform_keys: Optional[List[str]] = None, force_refresh: bool = False, status_callback=None) -> Dict[str, List[dict]]:
        """
        Fetches target data across specified platforms in parallel.
        """
        if not platform_keys:
            platform_keys = list(DATA_SOURCES.keys())

        results = {}
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_platform = {
                executor.submit(self.fetch_single_platform, key, force_refresh, status_callback): key
                for key in platform_keys
            }
            for future in as_completed(future_to_platform):
                key = future_to_platform[future]
                try:
                    p_key, raw_data, updated = future.result()
                    results[p_key] = raw_data
                except Exception:
                    results[key] = []
        return results

    def get_processed_targets(
        self,
        platform_choice: str = "all",
        category_filter: str = "all",
        force_refresh: bool = False,
        status_callback=None
    ) -> List[dict]:
        """
        Orchestrates fetching, parsing, scope filtering, and AI scoring.
        - platform_choice: 'yeswehack', 'bugcrowd', 'hackerone', or 'all'
        - category_filter: 'wildcard', 'domain', or 'all'
        """
        if platform_choice == "all":
            platforms_to_fetch = list(DATA_SOURCES.keys())
        else:
            platforms_to_fetch = [platform_choice]

        raw_platform_data = self.fetch_all_platforms(
            platforms_to_fetch,
            force_refresh=force_refresh,
            status_callback=status_callback
        )

        all_parsed_targets = []
        for p_key, programs in raw_platform_data.items():
            for prog in programs:
                parsed = parse_program_targets(prog, p_key)
                all_parsed_targets.extend(parsed)

        # Apply category filter (Wildcard vs Single Domain vs All)
        if category_filter in ("wildcard", "domain"):
            filtered_targets = [
                t for t in all_parsed_targets if t["category"] == category_filter
            ]
        else:
            filtered_targets = all_parsed_targets

        # Known previous targets set for Freshness calculation
        known_target_ids = set(self.history)
        
        # Filter out anything already seen/hunted completely
        filtered_targets = [t for t in filtered_targets if t["identifier"] not in known_target_ids]

        # Score and rank targets
        ranked_targets = score_and_rank_targets(filtered_targets, known_target_ids)

        return ranked_targets

    def record_hunted_target(self, target_identifier: str):
        """
        Stores an identifier in history.
        """
        if target_identifier not in self.history:
            self.history.append(target_identifier)
            self._save_json(HISTORY_FILE, self.history)

    def get_known_history_count(self) -> int:
        return len(self.history)

    def get_last_sync_info(self) -> Dict[str, dict]:
        return self.sync_meta
