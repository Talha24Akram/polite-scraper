"""Polite HTTP fetching with an on-disk HTML cache."""
import re
import time
from pathlib import Path

import requests

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/Talha24Akram/polite-scraper)"
TIMEOUT = 10  # seconds
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"


def cache_path(url: str) -> Path:
    name = re.sub(r"^https?://[^/]+/", "", url)
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_") or "index"
    return CACHE_DIR / name


def fetch(url: str) -> tuple[str, str]:
    """Return (html, source) where source is 'CACHE HIT' or 'FETCH'."""
    path = cache_path(url)
    if path.exists():
        return path.read_text(encoding="utf-8"), "CACHE HIT"
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code} for {url}")
    html = resp.content.decode("utf-8")  # the site sends no charset; do not trust requests' guess
    CACHE_DIR.mkdir(exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return html, "FETCH"
