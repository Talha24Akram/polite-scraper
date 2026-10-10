import json
from pathlib import Path

from pydantic import ValidationError

from crawl import discover
from extract import extract_book
from fetcher import fetch, fetched_at
from schema import reason, validate_record

OUT = Path(__file__).resolve().parent.parent / "output"

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    pages, urls, source_of, stats = discover()
    print(f"catalogue_pages={len(pages)} discovered={len(urls)} unique_urls={len(set(urls))}")
    good, errors = {}, []
    for url in urls:
        html, how = fetch(url)
        stats[how] += 1
        raw = extract_book(html, url, source_of[url], fetched_at(url))
        try:
            good[url] = validate_record(raw).model_dump()  # keyed by canonical URL: no duplicates
        except ValidationError as e:
            errors.append({"product_url": url, "reason": reason(e), "raw": raw})
    (OUT / "books.json").write_text(json.dumps(list(good.values()), indent=2, ensure_ascii=False) + "\n")
    (OUT / "errors.json").write_text(json.dumps(errors, indent=2, ensure_ascii=False) + "\n")
    print(f"valid={len(good)} invalid={len(errors)} fetched={stats['FETCH']} cache_hits={stats['CACHE HIT']}")
