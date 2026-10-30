"""Google Fact Check Tools API & ClaimReview Knowledge Base Client.

Retrieves verified fact-check records from the Google Fact Check Tools API
and maps ClaimReview schema records to TruthLens-Omni Evidence objects.
Includes local fallback knowledge store for offline research and testing.
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import urllib.parse
import urllib.request
import json
import logging
from src.core.config import settings
from src.core.types import Evidence
from src.nlp.temporal_decay import calculate_temporal_decay

logger = logging.getLogger(__name__)

# Curated reference knowledge store for offline test execution and benchmark verification
OFFLINE_FACT_REGISTRY: List[Dict[str, Any]] = [
    {
        "keywords": ["who", "covid", "vaccine", "infertility", "microchip"],
        "title": "COVID-19 Vaccines Do Not Cause Infertility or Contain Microchips",
        "publisher": "World Health Organization & Reuters Fact Check",
        "url": "https://www.reuters.com/fact-check/covid-vaccines-safe",
        "publish_date": "2023-04-15T00:00:00Z",
        "rating": "False",
        "snippet": "Extensive peer-reviewed clinical studies across billions of administered doses confirm COVID-19 vaccines do not alter human reproductive organs or contain tracking microchips.",
    },
    {
        "keywords": ["isro", "chandrayaan", "alien", "moon"],
        "title": "ISRO Chandrayaan Mission Found Alien Structures on Moon: False Claim",
        "publisher": "CDAC Fact Check Unit & CDAC CDAC",
        "url": "https://factcheck.pib.gov.in/isro-chandrayaan-claims",
        "publish_date": "2023-09-02T00:00:00Z",
        "rating": "False",
        "snippet": "Official telemetry and photographic data from the Pragyan rover confirmed standard lunar regolith, sulfur, and mineral compositions with zero artificial structures.",
    },
    {
        "keywords": ["election", "voting", "machine", "tampered", "evm"],
        "title": "EVMs Hacked via Bluetooth: Viral Video is Manipulated",
        "publisher": "Election Commission of India / BoomLive",
        "url": "https://www.boomlive.in/fact-check/evm-tampering-debunk",
        "publish_date": "2024-02-10T00:00:00Z",
        "rating": "False",
        "snippet": "Electronic Voting Machines are standalone non-networked systems without Bluetooth, Wi-Fi, or internet transceivers, rendering remote electronic tampering physically impossible.",
    },
]

class FactCheckClient:
    """Client for retrieving verified claim reviews and evidence documents."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_FACT_CHECK_API_KEY
        self.endpoint = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

    def search_evidence(
        self,
        query: str,
        claim_time: Optional[datetime] = None,
        max_results: int = 5,
    ) -> List[Evidence]:
        """
        Search external evidence for a given claim query.
        
        Args:
            query: Claim assertion text.
            claim_time: Publication date of the claim to assess temporal decay.
            max_results: Maximum evidence sentences to return.
            
        Returns:
            List[Evidence]: Top evidence records with calculated temporal decay weights.
        """
        evidence_list: List[Evidence] = []

        if self.api_key:
            try:
                evidence_list = self._fetch_google_fact_check(query, claim_time, max_results)
            except Exception as e:
                logger.warning("Online Google Fact Check lookup failed (%s). Falling back to local store.", e)
                evidence_list = []

        # If online returned empty or no key provided, query local curated registry
        if not evidence_list:
            evidence_list = self._search_local_registry(query, claim_time, max_results)

        return evidence_list

    def _fetch_google_fact_check(
        self,
        query: str,
        claim_time: Optional[datetime],
        max_results: int,
    ) -> List[Evidence]:
        """Query Google Fact Check Tools API."""
        params = {
            "query": query,
            "key": self.api_key,
            "pageSize": max_results,
            "languageCode": "en",
        }
        url = f"{self.endpoint}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "TruthLens-Omni/1.0"})

        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        results: List[Evidence] = []
        for item in data.get("claims", []):
            for review in item.get("claimReview", []):
                pub_date = self._parse_iso_date(review.get("reviewDate"))
                temp_weight = calculate_temporal_decay(claim_time, pub_date)
                sim_score = 0.85  # Calibrated baseline for verified API matches

                evidence = Evidence(
                    source_title=review.get("title") or item.get("text", "Fact Check"),
                    publisher=review.get("publisher", {}).get("name", "Verified Fact-Checker"),
                    url=review.get("url"),
                    publish_date=pub_date,
                    snippet=f"Rating: {review.get('textualRating', 'Unverified')}. Claim: {item.get('text', '')}",
                    semantic_similarity=sim_score,
                    temporal_weight=temp_weight,
                    final_score=round(sim_score * temp_weight, 3),
                )
                results.append(evidence)
                if len(results) >= max_results:
                    break

        return results

    def _search_local_registry(
        self,
        query: str,
        claim_time: Optional[datetime],
        max_results: int,
    ) -> List[Evidence]:
        """Fallback keyword-weighted search over offline fact store."""
        query_words = set(query.lower().split())
        matched: List[Tuple[float, Dict[str, Any]]] = []

        for record in OFFLINE_FACT_REGISTRY:
            overlap = sum(1 for kw in record["keywords"] if kw in query_words or any(kw in word for word in query_words))
            if overlap > 0:
                score = min(0.95, 0.40 + 0.15 * overlap)
                matched.append((score, record))

        matched.sort(key=lambda x: x[0], reverse=True)
        results: List[Evidence] = []

        for score, rec in matched[:max_results]:
            pub_date = self._parse_iso_date(rec.get("publish_date"))
            temp_weight = calculate_temporal_decay(claim_time, pub_date)
            final = round(score * temp_weight, 3)

            results.append(
                Evidence(
                    source_title=rec["title"],
                    publisher=rec["publisher"],
                    url=rec["url"],
                    publish_date=pub_date,
                    snippet=f"Rating: {rec['rating']}. {rec['snippet']}",
                    semantic_similarity=round(score, 3),
                    temporal_weight=round(temp_weight, 3),
                    final_score=final,
                )
            )

        return results

    @staticmethod
    def _parse_iso_date(date_str: Optional[str]) -> Optional[datetime]:
        """Safely parse various ISO date strings."""
        if not date_str:
            return None
        try:
            cleaned = date_str.replace("Z", "+00:00")
            return datetime.fromisoformat(cleaned)
        except Exception:
            return None
