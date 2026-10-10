"""Turn one book page into a raw record (strings exactly as shown on the page)."""
from bs4 import BeautifulSoup

RATINGS = {"One", "Two", "Three", "Four", "Five"}


def extract_book(html: str, product_url: str, source_page: str, fetched_at: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    main = soup.select_one("article.product_page")  # aim at the product area, not the document
    if main is None:
        raise ValueError("no product area found")
    title = main.select_one(".product_main h1")
    price = main.select_one(".product_main p.price_color")
    avail = main.select_one(".product_main p.availability")
    rating = main.select_one(".product_main p.star-rating")
    desc = main.select_one("#product_description")
    desc_p = desc.find_next_sibling("p") if desc else None
    rating_text = next((c for c in (rating.get("class", []) if rating else []) if c in RATINGS), None)
    return {
        "title": title.get_text(strip=True) if title else None,
        "product_url": product_url,
        "price_text": price.get_text(strip=True) if price else None,
        "availability_text": " ".join(avail.get_text().split()) if avail else None,
        "rating_text": rating_text,
        "description": desc_p.get_text(strip=True) if desc_p else None,  # null, never invented
        "source_page": source_page,
        "fetched_at": fetched_at,
    }
