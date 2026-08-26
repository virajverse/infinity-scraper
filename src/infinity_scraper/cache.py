"""
High-performance Caching Layer for InfinityScrape.
Supports SQLite persistent caching with TTL to eliminate redundant network hits.
"""

import hashlib
import json
import os
import sqlite3
import time
from typing import Any, Dict, Optional

CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
DB_PATH = os.path.join(CACHE_DIR, "scrape_cache.db")


class ScrapeCache:
    def __init__(self, db_path: str = DB_PATH, default_ttl_seconds: int = 3600):
        self.db_path = db_path
        self.default_ttl = default_ttl_seconds
        self._init_db()

    def _init_db(self):
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS page_cache (
                        key TEXT PRIMARY KEY,
                        url TEXT,
                        content_json TEXT,
                        created_at REAL,
                        ttl REAL
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON page_cache (created_at)")
        except Exception:
            pass

    def _hash_key(self, url: str, extra: str = "") -> str:
        raw = f"{url.strip()}::{extra}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, url: str, extra: str = "") -> Optional[Dict[str, Any]]:
        try:
            key = self._hash_key(url, extra)
            now = time.time()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT content_json, created_at, ttl FROM page_cache WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row:
                    content_json, created_at, ttl = row
                    if (now - created_at) < ttl:
                        return json.loads(content_json)
                    else:
                        cursor.execute("DELETE FROM page_cache WHERE key = ?", (key,))
                        conn.commit()
        except Exception:
            pass
        return None

    def set(self, url: str, data: Dict[str, Any], extra: str = "", ttl_seconds: Optional[int] = None):
        try:
            key = self._hash_key(url, extra)
            now = time.time()
            ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
            payload = json.dumps(data, ensure_ascii=False)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO page_cache (key, url, content_json, created_at, ttl) VALUES (?, ?, ?, ?, ?)",
                    (key, url, payload, now, ttl),
                )
        except Exception:
            pass

    def clear(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM page_cache")
        except Exception:
            pass


cache = ScrapeCache()
