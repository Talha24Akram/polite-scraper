"""Run the whole pipeline: discover -> fetch -> extract -> validate -> store -> report.

    python src/main.py                # normal run
    python src/main.py --inject-bad   # add one made-up book URL to prove a bad page cannot kill the run
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError

from crawl import discover
from extract import extract_book
from fetcher import FetchError, fetch, fetched_at
from schema import reason, validate_record

OUT = Path(__file__).resolve().parent.parent / "output"
FAKE_URL = "https://books.toscrape.com/catalogue/not-a-real-book_0/index.html"


def run(inject_bad: bool = False) -> dict:
    t0, started = time.monotonic(), datetime.now(timezone.utc)
    OUT.mkdir(exist_ok=True)
    pages, urls, source_of, stats = discover()
    print(f"catalogue_pages={len(pages)} discovered={len(urls)} unique_urls={len(set(urls))}")
    if inject_bad:
        urls.append(FAKE_URL)
        source_of[FAKE_URL] = pages[-1]
    good, errors, failed = {}, [], []
    for url in urls:
        try:  # one page at a time: a broken page is logged and skipped
            html, how = fetch(url)
            stats[how] += 1
            raw = extract_book(html, url, source_of[url], fetched_at(url))
            good[url] = validate_record(raw).model_dump()  # keyed by canonical URL: no duplicates
        except FetchError as e:
            failed.append({"url": url, "error": str(e)})
            print(f"FAILED {e}")
        except ValidationError as e:
            errors.append({"product_url": url, "reason": reason(e), "raw": raw})
        except Exception as e:  # e.g. page layout changed
            failed.append({"url": url, "error": f"{type(e).__name__}: {e}"})
            print(f"FAILED {url}: {e}")
    (OUT / "books.json").write_text(json.dumps(list(good.values()), indent=2, ensure_ascii=False) + "\n")
    (OUT / "errors.json").write_text(json.dumps(errors, indent=2, ensure_ascii=False) + "\n")
    report = {
        "started_at": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "duration_seconds": round(time.monotonic() - t0, 2),
        "catalogue_pages": len(pages),
        "urls_discovered": len(urls),
        "pages_fetched": stats["FETCH"],
        "cache_hits": stats["CACHE HIT"],
        "valid_records": len(good),
        "invalid_records": len(errors),
        "failed_pages": len(failed),
        "failed": failed,
    }
    (OUT / "run-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "failed"}))
    return report


if __name__ == "__main__":
    run(inject_bad="--inject-bad" in sys.argv)
