"""Find the book links on the first catalogue pages by following the site's own 'next' link."""
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from fetcher import fetch

START = "https://books.toscrape.com/catalogue/page-1.html"
MAX_PAGES = 3


def parse_catalogue(html: str, page_url: str) -> tuple[list[str], str | None]:
    soup = BeautifulSoup(html, "html.parser")
    links = [urljoin(page_url, a["href"]) for a in soup.select("article.product_pod h3 a[href]")]
    nxt = soup.select_one("li.next a[href]")
    return links, (urljoin(page_url, nxt["href"]) if nxt else None)


def discover(start: str = START, max_pages: int = MAX_PAGES):
    """Return (pages, urls, source_of). urls are de-duplicated, order preserved."""
    pages, urls, source_of, stats = [], [], {}, {"FETCH": 0, "CACHE HIT": 0}
    page_url = start
    while page_url and len(pages) < max_pages:
        html, how = fetch(page_url)
        stats[how] += 1
        pages.append(page_url)
        links, page_url = parse_catalogue(html, pages[-1])
        for link in links:
            if link not in source_of:
                source_of[link] = pages[-1]
                urls.append(link)
    return pages, urls, source_of, stats
