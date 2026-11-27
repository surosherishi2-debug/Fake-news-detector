"""Extended unit tests for URLScraper parsing and metadata extraction."""

from bs4 import BeautifulSoup

from src.retrieval.url_scraper import URLScraper


def test_url_scraper_initialization():
    scraper = URLScraper(timeout=8)
    assert scraper.timeout == 8
    assert "User-Agent" in scraper.headers
    assert "TruthLens" in scraper.headers["User-Agent"]


def test_url_scraper_parse_html_mock():
    html_doc = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CDC Reports Milestone In Public Health Initiative</title>
        <meta name="description" content="Official bulletin on health metrics.">
        <meta property="og:site_name" content="Centers for Disease Control">
        <meta property="article:published_time" content="2023-09-15T12:00:00Z">
    </head>
    <body>
        <nav><p>Navigation links to ignore</p></nav>
        <article>
            <h1>CDC Reports Milestone In Public Health Initiative</h1>
            <p>Comprehensive longitudinal health research demonstrates substantial reduction in communicable pathogens.</p>
            <p>Clinical researchers verified the findings across multi-hospital trials over two years.</p>
        </article>
        <footer><p>Footer copyright information</p></footer>
    </body>
    </html>
    """
    soup = BeautifulSoup(html_doc, "html.parser")

    # Check title extraction
    title = soup.title.string.strip() if soup.title else ""
    assert "CDC Reports Milestone" in title

    # Check article text extraction
    article = soup.find("article")
    assert article is not None
    paragraphs = article.find_all("p")
    text_content = " ".join(p.get_text().strip() for p in paragraphs)
    assert "longitudinal health research" in text_content
    assert "reduction in communicable pathogens" in text_content


def test_url_scraper_extract_publish_date():
    scraper = URLScraper()

    # Test ISO date parsing from meta
    html = '<meta property="article:published_time" content="2023-10-20T08:30:00Z">'
    soup = BeautifulSoup(html, "html.parser")
    date_val = scraper._extract_publish_date(soup)
    assert date_val is not None
    assert date_val.year == 2023
    assert date_val.month == 10
    assert date_val.day == 20


def test_url_scraper_extract_publish_date_missing():
    scraper = URLScraper()
    html = "<html><head><title>No date here</title></head><body><p>Text</p></body></html>"
    soup = BeautifulSoup(html, "html.parser")
    date_val = scraper._extract_publish_date(soup)
    assert date_val is None


def test_url_scraper_failed_network_graceful():
    scraper = URLScraper(timeout=1)
    # Non-routable private test URL should fail gracefully without unhandled exception
    req, meta = scraper.scrape_url("http://192.0.2.1/nonexistent-article-test")
    assert req is None
    assert meta["status"] == "failed"
    assert meta["word_count"] == 0
