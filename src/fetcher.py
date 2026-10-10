"""Polite HTTP fetching with an on-disk HTML cache."""
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/Talha24Akram/polite-scraper)"
TIMEOUT = 10  # seconds
RETRY_WAIT = 2  # seconds before the single retry
MIN_DELAY = 0.6  # seconds between real requests (brief asks for >= 0.5)
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"

_last_request = 0.0


def cache_path(url: str) -> Path:
    name = re.sub(r"^https?://[^/]+/", "", url)
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_") or "index"
    return CACHE_DIR / name


def fetched_at(url: str) -> str:
    """When the cached copy was downloaded (file mtime), as ISO-8601 UTC."""
    mtime = cache_path(url).stat().st_mtime
    return datetime.fromtimestamp(mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _wait_turn() -> None:
    global _last_request
    gap = time.monotonic() - _last_request
    if gap < MIN_DELAY:
        time.sleep(MIN_DELAY - gap)
    _last_request = time.monotonic()


class FetchError(Exception):
    """A page could not be fetched; the run logs it and moves on."""


def _get(url: str) -> requests.Response:
    """One real request. Timeouts and 5xx get one more try; 404/403 never do."""
    for attempt in (1, 2):
        _wait_turn()
        try:
            resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        except (requests.Timeout, requests.ConnectionError) as e:
            if attempt == 2:
                raise FetchError(f"{type(e).__name__} for {url}") from e
            time.sleep(RETRY_WAIT)
            continue
        if resp.status_code >= 500 and attempt == 1:
            time.sleep(RETRY_WAIT)
            continue
        return resp
    raise AssertionError("unreachable")


def fetch(url: str) -> tuple[str, str]:
    """Return (html, source) where source is 'CACHE HIT' or 'FETCH'."""
    path = cache_path(url)
    if path.exists():
        return path.read_text(encoding="utf-8"), "CACHE HIT"
    resp = _get(url)
    if resp.status_code != 200:
        raise FetchError(f"HTTP {resp.status_code} for {url}")
    html = resp.content.decode("utf-8")  # the site sends no charset; do not trust requests' guess
    CACHE_DIR.mkdir(exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return html, "FETCH"
