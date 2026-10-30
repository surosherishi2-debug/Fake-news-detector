"""Unit tests for URL Scraper (Feature 10)."""

from src.retrieval.url_scraper import URLScraper

def test_url_scraper_domain_parsing():
    scraper = URLScraper()
    # Test on an invalid/nonexistent URL: must gracefully return None with error metadata
    v_req, meta = scraper.scrape_url("http://invalid-nonexistent-domain-xyz992.com/article")
    assert v_req is None
    assert meta["domain"] == "invalid-nonexistent-domain-xyz992.com"
    assert meta["status"] == "failed"
    assert "error" in meta
