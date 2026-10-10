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
