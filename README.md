# Polite scraper (Python lane)

A small, polite scraping pipeline for the FlyRank Backend track (A9).

## Target classification
- **Site:** https://books.toscrape.com (Books to Scrape).
- **Why:** toscrape.com describes itself as a "Web Scraping Sandbox" — "a fictional bookstore that desperately wants to be scraped. It's a safe place for beginners learning web scraping". The site exists for exactly this practice, so automating it is permitted.
- **How much:** the first 3 catalogue pages only, which link to 60 book pages (63 pages in total).
- **What I collect:** public product data per book: title, product URL, price, availability, star rating, description.
- **robots.txt result:** `GET https://books.toscrape.com/robots.txt` returned **404 Not Found** — no robots file found. A missing file is not permission by itself; the permission here comes from the site's own sandbox statement.
- **Appropriate because:** it is a practice sandbox built for scrapers, I stay inside 63 requests, send an honest user-agent, and wait between requests.

I will not reuse this code on another site without checking its rules and terms first.

## Run it (about 5 minutes the first time)
Lane: **Python 3.10+** with `requests`, `beautifulsoup4`, `pydantic`.
```bash
git clone https://github.com/Talha24Akram/polite-scraper && cd polite-scraper
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python src/main.py                # first run: ~65 s (63 polite requests); reruns read the cache
.venv/bin/python src/main.py --inject-bad   # adds one made-up book URL to prove a bad page cannot kill the run
.venv/bin/python -m pytest -q tests         # 6 offline parser tests, no network
```
Outputs land in `output/`: `books.json` (valid records), `errors.json` (invalid ones with a reason),
`run-report.json` (what happened). Downloaded HTML goes to `cache/` (git-ignored).

## Pipeline
`fetch → extract → normalize → validate → store → report`

| Step | Code |
|---|---|
| Fetch + cache | `src/fetcher.py` |
| Find the 3 pages and 60 URLs | `src/crawl.py` (follows the site's own `next` link, `urljoin` for relative links, de-duplicates) |
| Extract raw record | `src/extract.py` (selectors scoped to `article.product_page`) |
| Normalize + validate | `src/schema.py` (Pydantic `Book`) |
| Orchestrate + report | `src/main.py` |

## Record schema
| Field | Type | Notes |
|---|---|---|
| `title` | str, required | |
| `product_url` | str, required, `https://` | canonical URL = identity, so a book is stored once |
| `price_text` | str, required | raw, e.g. `£51.77` |
| `price_gbp` | float ≥ 0, required | normalized from `price_text`; raw value is kept beside it |
| `availability_text` | str, required | e.g. `In stock (22 available)` |
| `rating_text` | str, required | `One` … `Five` |
| `description` | str or `null` | `null` when the page has none; never invented |
| `source_page` | str, required | provenance: catalogue page the link came from |
| `fetched_at` | str, required | provenance: when the HTML was downloaded (UTC) |

A record that fails the schema goes to `output/errors.json` with the reason and never into `books.json`.
Writing `books.json` is keyed by `product_url`, so a rerun produces the same 60 records, not 120 (idempotent).

## Politeness rules
- **User-agent:** `FlyRankInternship-A9/1.0 (+https://github.com/Talha24Akram/polite-scraper)` on every request.
- **Delay:** at least 0.6 s between real requests (cache hits need none).
- **Timeout:** 10 s on every request.
- **Status check:** only `200` is parsed. A timeout or `5xx` is retried once after 2 s; `404` and `403` are never retried.
- **Cache:** development reads the saved HTML in `cache/`, so the site is asked once per page.
- **Scope:** only the first 3 catalogue pages and the 60 books they link to.

## Proof: a real run report
Two runs on a warm cache (the first, cold run took about 72 s and fetched 63 pages). This is
`docs/run-report-with-bad-url.json`, the run with one made-up URL added on purpose:
```json
{
  "started_at": "2026-10-10T18:35:56Z",
  "duration_seconds": 0.97,
  "catalogue_pages": 3,
  "urls_discovered": 61,
  "pages_fetched": 0,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1,
  "failed": [
    {
      "url": "https://books.toscrape.com/catalogue/not-a-real-book_0/index.html",
      "error": "HTTP 404 for https://books.toscrape.com/catalogue/not-a-real-book_0/index.html"
    }
  ]
}
```
The run finished, `books.json` still has the 60 good records, and `failed_pages` is 1.
`output/run-report.json` in the repo is the last clean rerun (`failed_pages: 0`).

**Why no browser:** the data is already in the HTML the server sends, so a browser would only add cost.

## Ethics note
I only scraped a site whose owners say it exists to be scraped, introduced myself with an honest user-agent,
kept the request count and speed low, and cached everything so the site never sees me twice for the same page.
A real site needs its terms, robots.txt and any official API checked first. A missing robots.txt, as here, is not
permission by itself.

## Honest limitation
Selectors are tied to this site's current HTML. If the layout changes, the extractor raises for that page, which is
logged under `failed` in the run report instead of storing guesses. The retry is deliberately simple (one retry, no
backoff or `Retry-After` handling), and the cache never expires, so delete `cache/` to refresh.
