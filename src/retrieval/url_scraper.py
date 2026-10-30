"""Live URL Scraper and Web Article Extractor.

Extracts article body, metadata, author, publish date, and domain reputation
from live web links for real-time TruthLens verification.
"""

from typing import Optional, Dict, Any, Tuple
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import re
import logging
from src.core.types import VerificationRequest

logger = logging.getLogger(__name__)

class URLScraper:
    """Extracts clean article text and publisher metadata from raw URLs."""

    def __init__(self, timeout: int = 6):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 TruthLens/1.0"
        }

    def scrape_url(self, url: str) -> Tuple[Optional[VerificationRequest], Dict[str, Any]]:
        """
        Scrape and parse article content from a live URL.
        
        Args:
            url: Target web page URL.
            
        Returns:
            Tuple[VerificationRequest, Dict[str, Any]]: Structured request payload and metadata.
        """
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]

        metadata: Dict[str, Any] = {
            "url": url,
            "domain": domain,
            "title": "",
            "publish_date": None,
            "word_count": 0,
            "status": "failed",
        }

        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                html = resp.read().decode("utf-8", errors="ignore")

            soup = BeautifulSoup(html, "html.parser")

            # Extract title
            title = ""
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                title = og_title["content"].strip()
            elif soup.title and soup.title.string:
                title = soup.title.string.strip()

            # Extract paragraphs
            paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 30]
            body_text = " ".join(paragraphs)

            # Fallback if few paragraphs found
            if not body_text and title:
                og_desc = soup.find("meta", property="og:description")
                if og_desc and og_desc.get("content"):
                    body_text = f"{title}. {og_desc['content'].strip()}"
                else:
                    body_text = title

            # Extract publish date
            pub_date = None
            date_meta = soup.find("meta", property=re.compile(r"(published_time|date|pubdate)", re.I))
            if date_meta and date_meta.get("content"):
                try:
                    pub_date = datetime.fromisoformat(date_meta["content"].replace("Z", "+00:00"))
                except Exception:
                    pub_date = None

            metadata["title"] = title
            metadata["word_count"] = len(body_text.split())
            metadata["publish_date"] = pub_date.isoformat() if pub_date else None
            metadata["status"] = "success"

            combined_text = f"{title}. {body_text}" if title and title not in body_text else body_text

            v_req = VerificationRequest(
                text=combined_text[:4000],  # Bound to 4000 chars for prompt & model safety
                publisher=domain,
                publication_date=pub_date or datetime.now(timezone.utc),
            )
            return v_req, metadata

        except Exception as e:
            logger.warning("Failed to scrape URL %s: %s", url, e)
            metadata["error"] = str(e)
            return None, metadata
