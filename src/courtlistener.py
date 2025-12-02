"""CourtListener API client for citation validation."""

import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, TypeVar

import httpx
from lxml import html

from .models import Citation

T = TypeVar("T")


def retry_with_backoff(
    fn: Callable[[], T],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
) -> T:
    """Retry a function with exponential backoff.

    Args:
        fn: Function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries

    Returns:
        Result of the function

    Raises:
        The last exception if all retries fail
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return fn()
        except httpx.HTTPStatusError as e:
            last_exception = e
            if e.response.status_code == 429:
                # Rate limited - use longer delay
                delay = min(base_delay * (2**attempt) * 2, max_delay)
            elif e.response.status_code == 400:
                # CourtListener sometimes returns spurious 400s - retry
                delay = min(base_delay * (2**attempt), max_delay)
            elif e.response.status_code >= 500:
                # Server error - retry with backoff
                delay = min(base_delay * (2**attempt), max_delay)
            else:
                # Other client errors (4xx) - don't retry
                raise
        except (
            httpx.ConnectError,
            httpx.ReadTimeout,
            httpx.WriteTimeout,
            httpx.PoolTimeout,
            httpx.TimeoutException,
        ) as e:
            last_exception = e
            delay = min(base_delay * (2**attempt), max_delay)

        if attempt < max_retries:
            print(f"    Retry {attempt + 1}/{max_retries} after {delay:.1f}s...")
            time.sleep(delay)

    raise last_exception  # type: ignore[misc]


@dataclass
class CacheEntry:
    """A cached citation validation result."""

    citation_key: str
    is_valid: bool
    courtlistener_id: Optional[str]
    case_name: Optional[str]
    opinion_text: Optional[str]
    error: Optional[str]
    timestamp: float


class CitationCache:
    """Disk-based cache for citation validation results."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = cache_dir / "citation_cache.json"
        self._cache: dict[str, dict] = self._load_cache()

    def _load_cache(self) -> dict:
        """Load cache from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_cache(self) -> None:
        """Persist cache to disk."""
        with open(self.cache_file, "w") as f:
            json.dump(self._cache, f, indent=2)

    @staticmethod
    def make_key(raw_text: str) -> str:
        """Create a cache key from citation raw text."""
        return hashlib.md5(raw_text.lower().strip().encode()).hexdigest()

    def get(self, citation: Citation) -> Optional[CacheEntry]:
        """Look up a citation in the cache."""
        key = self.make_key(citation.raw_text)
        if key in self._cache:
            data = self._cache[key]
            return CacheEntry(
                citation_key=key,
                is_valid=data["is_valid"],
                courtlistener_id=data.get("courtlistener_id"),
                case_name=data.get("case_name"),
                opinion_text=data.get("opinion_text"),
                error=data.get("error"),
                timestamp=data["timestamp"],
            )
        return None

    def set(
        self,
        citation: Citation,
        is_valid: bool,
        courtlistener_id: Optional[str] = None,
        case_name: Optional[str] = None,
        opinion_text: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        """Store a citation validation result."""
        key = self.make_key(citation.raw_text)
        self._cache[key] = {
            "is_valid": is_valid,
            "courtlistener_id": courtlistener_id,
            "case_name": case_name,
            "opinion_text": opinion_text,
            "error": error,
            "timestamp": time.time(),
            "raw_text": citation.raw_text,
        }
        self._save_cache()


class CourtListenerClient:
    """Client for the CourtListener API using citation lookup endpoint."""

    BASE_URL = "https://www.courtlistener.com/api/rest/v4"

    def __init__(
        self,
        api_token: Optional[str] = None,
        cache_dir: Optional[Path] = None,
        rate_limit_delay: float = 0.5,  # seconds between requests
    ):
        self.api_token = api_token or os.environ.get("COURTLISTENER_API_TOKEN")
        if not self.api_token:
            raise ValueError(
                "CourtListener API token required. Set COURTLISTENER_API_TOKEN "
                "environment variable or pass api_token parameter."
            )

        self.cache = CitationCache(cache_dir or Path("data/cache"))
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0.0

        self._client = httpx.Client(
            headers={
                "Authorization": f"Token {self.api_token}",
            },
            timeout=httpx.Timeout(60.0, read=120.0),  # 60s default, 120s for reads
        )

    def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    def _extract_opinion_text(self, cluster: dict) -> Optional[str]:
        """Extract the best available opinion text from a cluster.

        Prefers html_with_citations, falls back to plain_text.
        """
        sub_opinions = cluster.get("sub_opinions", [])
        if sub_opinions:
            opinion_url = sub_opinions[0]

            def fetch_opinion():
                self._rate_limit()
                response = self._client.get(opinion_url)
                response.raise_for_status()
                return response.json()

            opinion_data = retry_with_backoff(fetch_opinion)

            if "html_with_citations" in opinion_data:
                return html.fromstring(
                    opinion_data["html_with_citations"].encode("utf-8")
                ).text_content()

            return opinion_data.get("plain_text")

        if "html_with_citations" in cluster:
            return html.fromstring(
                cluster["html_with_citations"].encode("utf-8")
            ).text_content()

        return cluster.get("plain_text")

    def lookup_citation(self, raw_text: str) -> Optional[dict]:
        """Look up a citation using the citation-lookup endpoint.

        Args:
            raw_text: The citation text as it appears (e.g., "576 U.S. 644")

        Returns:
            The first matching cluster or None if not found.
        """

        def do_lookup():
            self._rate_limit()
            response = self._client.post(
                f"{self.BASE_URL}/citation-lookup/",
                data={"text": raw_text},
            )
            response.raise_for_status()
            return response.json()

        results = retry_with_backoff(do_lookup)

        # Results is a list of citation matches
        if results and len(results) > 0:
            first_result = results[0]
            # Status 200 means found
            if first_result.get("status") == 200:
                clusters = first_result.get("clusters", [])
                if clusters:
                    return clusters[0]
        return None

    def validate_citation(self, citation: Citation) -> Citation:
        """Validate a citation against CourtListener.

        Uses the citation-lookup endpoint which handles normalization.
        Updates the citation object with validation results and returns it.
        """
        # Check cache first
        cached = self.cache.get(citation)
        if cached is not None:
            citation.is_valid = cached.is_valid
            citation.courtlistener_id = cached.courtlistener_id
            citation.opinion_text = cached.opinion_text
            if cached.case_name:
                citation.case_name = cached.case_name
            if cached.error:
                citation.validation_error = cached.error
            return citation

        cluster = self.lookup_citation(citation.raw_text)

        if cluster:
            citation.is_valid = True
            citation.courtlistener_id = str(cluster.get("id", ""))

            # Extract case name if available
            if not citation.case_name and cluster.get("case_name"):
                citation.case_name = cluster["case_name"]

            # Extract and store opinion text for holding validation
            opinion_text = self._extract_opinion_text(cluster)
            citation.opinion_text = opinion_text

            self.cache.set(
                citation,
                is_valid=True,
                courtlistener_id=citation.courtlistener_id,
                case_name=citation.case_name,
                opinion_text=opinion_text,
            )
        else:
            citation.is_valid = False
            citation.validation_error = "Citation not found in CourtListener"
            self.cache.set(citation, is_valid=False, error="Not found")

        return citation

    def validate_citations(self, citations: list[Citation]) -> list[Citation]:
        """Validate multiple citations.

        Returns the list with validation results populated.
        """
        for citation in citations:
            # Skip statutes and already-validated citations
            if citation.court == "STATUTE" or citation.is_valid is not None:
                continue
            self.validate_citation(citation)
        return citations

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
