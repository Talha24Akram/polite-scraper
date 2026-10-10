from fetcher import fetch, cache_path

START = "https://books.toscrape.com/catalogue/page-1.html"

if __name__ == "__main__":
    html, source = fetch(START)
    print(f"{source} {START} -> {cache_path(START).name} ({len(html)} chars)")
