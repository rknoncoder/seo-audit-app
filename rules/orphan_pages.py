def find_orphan_pages(sitemap_urls, internal_links):
    """
    sitemap_urls: list of URLs from sitemap crawl
    internal_links: set of all internal links found
    """
    sitemap_set = set(url.rstrip("/") for url in sitemap_urls)

    orphans = sitemap_set - internal_links

    return sorted(list(orphans))
