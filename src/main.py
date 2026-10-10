import json

from crawl import discover
from extract import extract_book
from fetcher import fetch, fetched_at

if __name__ == "__main__":
    pages, urls, source_of, stats = discover()
    print(f"catalogue_pages={len(pages)} discovered={len(urls)} unique_urls={len(set(urls))}")
    raw = []
    for url in urls:
        html, how = fetch(url)
        stats[how] += 1
        raw.append(extract_book(html, url, source_of[url], fetched_at(url)))
    print(json.dumps(raw[0], indent=2, ensure_ascii=False))
    print(f"detail_pages={len(raw)} null_descriptions={sum(r['description'] is None for r in raw)} "
          f"fetched={stats['FETCH']} cache_hits={stats['CACHE HIT']}")
