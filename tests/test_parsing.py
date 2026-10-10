import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from crawl import parse_catalogue  # noqa: E402
from extract import extract_book  # noqa: E402
from schema import parse_price, validate_record  # noqa: E402

FIX = Path(__file__).parent / "fixtures"
URL = "https://books.toscrape.com/catalogue/x_1/index.html"
PAGE = "https://books.toscrape.com/catalogue/page-1.html"


def raw(name):
    return extract_book((FIX / name).read_text(), URL, PAGE, "2026-01-01T00:00:00Z")


def test_price_normalization():
    assert parse_price("£51.77") == 51.77
    assert parse_price("£1,051.77") == 1051.77
    assert parse_price("free") is None


def test_relative_to_absolute_urls_and_next_link():
    links, nxt = parse_catalogue((FIX / "catalogue.html").read_text(), PAGE)
    assert links[0] == "https://books.toscrape.com/catalogue/a-book_1/index.html"
    assert links[2] == "https://books.toscrape.com/other_2/index.html"
    assert nxt == "https://books.toscrape.com/catalogue/page-2.html"


def test_missing_description_is_null_not_invented():
    r = raw("book_no_description.html")
    assert r["description"] is None
    assert validate_record(r).description is None


def test_whitespace_is_cleaned_and_only_product_price_is_used():
    r = raw("book_ok.html")
    assert r["title"] == "Test Book"
    assert r["price_text"] == "£1,051.77"  # not the stray £9.99 outside the product area
    assert r["availability_text"] == "In stock (3 available)"
    assert r["description"] == "A   description."
    assert set(r) == {"title", "product_url", "price_text", "availability_text",
                      "rating_text", "description", "source_page", "fetched_at"}


def test_duplicate_links_collapse_by_url():
    links, _ = parse_catalogue((FIX / "catalogue.html").read_text(), PAGE)
    assert len(links) == 3 and len(set(links)) == 2


def test_malformed_page_is_rejected_not_half_parsed():
    with pytest.raises(ValueError):
        raw("book_malformed.html")
