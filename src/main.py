from crawl import discover

if __name__ == "__main__":
    pages, urls, source_of, stats = discover()
    print(f"catalogue_pages={len(pages)} discovered={len(urls)} unique_urls={len(set(urls))} "
          f"fetched={stats['FETCH']} cache_hits={stats['CACHE HIT']}")
