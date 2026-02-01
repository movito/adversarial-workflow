"""
Citation verification utilities for checking URLs in documents.

This module provides:
- URL extraction from markdown documents
- Async parallel URL checking with caching
- Inline marking of URL status
- Blocked URL task file generation

Status categories:
- available: 200 OK, content accessible
- blocked: Paywall/auth/bot-blocked (401, 403, or bot detection)
- broken: 404, 500, timeout, DNS failure
- redirect: 301/302 with final destination noted
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

# Module logger for debugging URL check failures
logger = logging.getLogger(__name__)


class URLStatus(Enum):
    """URL verification status categories."""

    AVAILABLE = "available"
    BLOCKED = "blocked"
    BROKEN = "broken"
    REDIRECT = "redirect"


@dataclass
class URLResult:
    """Result of checking a single URL."""

    url: str
    status: URLStatus
    status_code: Optional[int] = None
    final_url: Optional[str] = None
    error: Optional[str] = None
    checked_at: Optional[float] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "url": self.url,
            "status": self.status.value,
            "status_code": self.status_code,
            "final_url": self.final_url,
            "error": self.error,
            "checked_at": self.checked_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "URLResult":
        """Create from dictionary."""
        return cls(
            url=data["url"],
            status=URLStatus(data["status"]),
            status_code=data.get("status_code"),
            final_url=data.get("final_url"),
            error=data.get("error"),
            checked_at=data.get("checked_at"),
        )


@dataclass
class ExtractedURL:
    """A URL extracted from a document with context."""

    url: str
    position: int
    context: str
    line_number: int


# URL extraction pattern - matches http/https URLs
URL_PATTERN = re.compile(r"https?://[^\s\)\]\>\"\'\`]+")

# Bot detection patterns in response
BOT_DETECTION_PATTERNS = [
    "captcha",
    "cloudflare",
    "access denied",
    "forbidden",
    "bot detected",
    "please verify",
    "human verification",
]

# Default configuration
DEFAULT_CONFIG = {
    "max_urls": 100,
    "concurrency": 10,
    "timeout_per_url": 10,
    "cache_ttl": 86400,  # 24 hours
}


def extract_urls(document: str, max_urls: int = 100) -> list[ExtractedURL]:
    """
    Extract URLs from a document with surrounding context.

    Args:
        document: The document text to extract URLs from
        max_urls: Maximum number of URLs to extract (default: 100)

    Returns:
        List of ExtractedURL objects with position and context
    """
    urls = []
    lines = document.split("\n")
    line_starts = [0]
    for line in lines:
        line_starts.append(line_starts[-1] + len(line) + 1)

    for match in URL_PATTERN.finditer(document):
        url = match.group().rstrip(".,;:!?")  # Clean trailing punctuation
        position = match.start()

        # Find line number
        line_number = 1
        for i, start in enumerate(line_starts):
            if start > position:
                line_number = i
                break

        # Get context (50 chars before and after)
        start = max(0, position - 50)
        end = min(len(document), match.end() + 50)
        context = document[start:end]

        urls.append(
            ExtractedURL(
                url=url,
                position=position,
                context=context,
                line_number=line_number,
            )
        )

        if len(urls) >= max_urls:
            break

    return urls


def get_cache_path(cache_dir: Optional[Path] = None) -> Path:
    """Get the path to the URL cache file."""
    if cache_dir is None:
        cache_dir = Path.cwd() / ".adversarial"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "url_cache.json"


def load_cache(cache_path: Path) -> dict[str, dict]:
    """Load URL cache from disk."""
    if not cache_path.exists():
        return {}
    try:
        with open(cache_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_cache(cache_path: Path, cache: dict[str, dict]) -> None:
    """Save URL cache to disk."""
    with open(cache_path, "w") as f:
        json.dump(cache, f, indent=2)


def get_cache_key(url: str) -> str:
    """Generate a cache key for a URL."""
    return hashlib.md5(url.encode()).hexdigest()


def classify_response(status_code: int, _headers: dict, content: Optional[str] = None) -> URLStatus:
    """
    Classify HTTP response into a URL status.

    Args:
        status_code: HTTP status code
        _headers: Response headers (reserved for future use)
        content: Optional response body content (for bot detection)

    Returns:
        URLStatus enum value
    """
    if status_code == 200:
        # Check for bot blocking in content
        if content:
            content_lower = content.lower()
            for pattern in BOT_DETECTION_PATTERNS:
                if pattern in content_lower:
                    return URLStatus.BLOCKED
        return URLStatus.AVAILABLE
    elif status_code in (301, 302, 307, 308):
        return URLStatus.REDIRECT
    elif status_code in (401, 403):
        return URLStatus.BLOCKED
    elif status_code == 429:
        return URLStatus.BLOCKED  # Rate limited
    else:
        return URLStatus.BROKEN


async def check_url_async(
    url: str,
    timeout: int = 10,
    session=None,
) -> URLResult:
    """
    Check a single URL asynchronously.

    Args:
        url: URL to check
        timeout: Request timeout in seconds
        session: Optional aiohttp session to reuse

    Returns:
        URLResult with status information
    """
    try:
        import aiohttp
    except ImportError:
        return URLResult(
            url=url,
            status=URLStatus.BROKEN,
            error="aiohttp not installed - run: pip install aiohttp",
            checked_at=time.time(),
        )

    close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True

    try:
        async with session.head(
            url,
            timeout=aiohttp.ClientTimeout(total=timeout),
            allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; CitationVerifier/1.0)"},
        ) as response:
            final_url = str(response.url) if str(response.url) != url else None
            status = classify_response(response.status, dict(response.headers))

            # If redirect to an available page, mark as redirect (informational)
            # Keep broken/blocked status if redirect leads to error page
            if final_url and response.history and status == URLStatus.AVAILABLE:
                status = URLStatus.REDIRECT

            return URLResult(
                url=url,
                status=status,
                status_code=response.status,
                final_url=final_url,
                checked_at=time.time(),
            )
    except asyncio.TimeoutError:
        return URLResult(
            url=url,
            status=URLStatus.BROKEN,
            error="Timeout",
            checked_at=time.time(),
        )
    except Exception as e:
        error_name = type(e).__name__
        # Log full exception for debugging while returning truncated message
        logger.debug("URL check failed for %s: %s", url, e, exc_info=True)
        return URLResult(
            url=url,
            status=URLStatus.BROKEN,
            error=f"{error_name}: {str(e)[:50]}",
            checked_at=time.time(),
        )
    finally:
        if close_session:
            await session.close()


async def check_urls_parallel(
    urls: list[str],
    concurrency: int = 10,
    timeout: int = 10,
    cache: Optional[dict] = None,
    cache_ttl: int = 86400,
) -> list[URLResult]:
    """
    Check multiple URLs in parallel with optional caching.

    Args:
        urls: List of URLs to check
        concurrency: Maximum concurrent requests (must be >= 1)
        timeout: Timeout per request in seconds (must be >= 1)
        cache: Optional cache dictionary
        cache_ttl: Cache TTL in seconds (default: 24 hours)

    Returns:
        List of URLResult objects

    Raises:
        ValueError: If concurrency or timeout is less than 1
    """
    # Validate parameters to prevent deadlocks
    if concurrency < 1:
        raise ValueError(f"concurrency must be >= 1, got {concurrency}")
    if timeout < 1:
        raise ValueError(f"timeout must be >= 1, got {timeout}")

    try:
        import aiohttp
    except ImportError:
        return [
            URLResult(
                url=url,
                status=URLStatus.BROKEN,
                error="aiohttp not installed",
                checked_at=time.time(),
            )
            for url in urls
        ]

    url_to_result: dict[str, URLResult] = {}
    urls_to_check = []
    current_time = time.time()

    # Check cache first
    if cache is not None:
        for url in urls:
            cache_key = get_cache_key(url)
            if cache_key in cache:
                cached = cache[cache_key]
                if cached.get("expires", 0) > current_time:
                    url_to_result[url] = URLResult.from_dict(cached["result"])
                    continue
            urls_to_check.append(url)
    else:
        urls_to_check = list(urls)

    if urls_to_check:
        # Create semaphore for concurrency limiting
        semaphore = asyncio.Semaphore(concurrency)

        async def check_with_semaphore(session, url):
            async with semaphore:
                return await check_url_async(url, timeout, session)

        # Check remaining URLs
        connector = aiohttp.TCPConnector(limit=concurrency, limit_per_host=5)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [check_with_semaphore(session, url) for url in urls_to_check]
            checked_results = await asyncio.gather(*tasks)

        # Update cache and store results
        for result in checked_results:
            if cache is not None:
                cache_key = get_cache_key(result.url)
                cache[cache_key] = {
                    "result": result.to_dict(),
                    "expires": current_time + cache_ttl,
                }
            url_to_result[result.url] = result

    # Return results in original URL order
    return [url_to_result[url] for url in urls]


def check_urls(
    urls: list[str],
    concurrency: int = 10,
    timeout: int = 10,
    cache_dir: Optional[Path] = None,
    cache_ttl: int = 86400,
) -> list[URLResult]:
    """
    Check multiple URLs synchronously (wrapper around async version).

    Args:
        urls: List of URLs to check
        concurrency: Maximum concurrent requests
        timeout: Timeout per request in seconds
        cache_dir: Optional cache directory
        cache_ttl: Cache TTL in seconds

    Returns:
        List of URLResult objects

    Raises:
        RuntimeError: If called from within an async context (event loop running).
            Use check_urls_parallel() directly from async code.
    """
    # Guard against calling from async context
    try:
        asyncio.get_running_loop()
        raise RuntimeError(
            "check_urls() cannot be called from within an async context. "
            "Use check_urls_parallel() directly instead."
        )
    except RuntimeError as e:
        # No running loop - this is expected, proceed
        if "no running event loop" not in str(e).lower():
            raise

    # Load cache
    cache_path = get_cache_path(cache_dir)
    cache = load_cache(cache_path)

    # Run async check
    results = asyncio.run(
        check_urls_parallel(
            urls,
            concurrency=concurrency,
            timeout=timeout,
            cache=cache,
            cache_ttl=cache_ttl,
        )
    )

    # Save cache
    save_cache(cache_path, cache)

    return results


def get_status_badge(result: URLResult) -> str:
    """
    Generate an inline status badge for a URL result.

    Args:
        result: URLResult to generate badge for

    Returns:
        Markdown-formatted status badge
    """
    if result.status == URLStatus.AVAILABLE:
        return f"[✅ Verified | {result.status_code} OK]"
    elif result.status == URLStatus.BLOCKED:
        if result.status_code:
            return f"[⚠️ Blocked | {result.status_code}]"
        return "[⚠️ Blocked | Access Denied]"
    elif result.status == URLStatus.BROKEN:
        if result.error:
            return f"[❌ Broken | {result.error}]"
        if result.status_code:
            return f"[❌ Broken | {result.status_code}]"
        return "[❌ Broken | Unreachable]"
    elif result.status == URLStatus.REDIRECT:
        dest = (
            result.final_url[:30] + "..."
            if result.final_url and len(result.final_url) > 30
            else result.final_url
        )
        return f"[🔄 Redirect | → {dest}]"
    return "[❓ Unknown]"


def mark_urls_inline(document: str, results: list[URLResult]) -> str:
    """
    Mark URLs in a document with their status badges.

    Args:
        document: Original document text
        results: List of URL check results

    Returns:
        Document with inline status badges added after URLs
    """
    # Create URL to result mapping
    url_results = {r.url: r for r in results}

    # Find all URLs and their positions
    marked = document
    offset = 0  # Track offset as we insert badges

    for match in URL_PATTERN.finditer(document):
        url = match.group().rstrip(".,;:!?")  # Same stripping as extract_urls
        if url in url_results:
            result = url_results[url]
            badge = get_status_badge(result)

            # Check if badge already exists after this URL
            end_pos = match.end() + offset
            remaining = marked[end_pos:]
            if remaining.startswith((" [✅", " [⚠️", " [❌", " [🔄")):
                continue  # Already marked

            # Insert badge after URL
            insert_pos = end_pos
            marked = marked[:insert_pos] + " " + badge + marked[insert_pos:]
            offset += len(badge) + 1

    return marked


def generate_blocked_tasks(
    results: list[URLResult],
    document_path: str,
    output_path: Optional[Path] = None,
) -> str:
    """
    Generate a task file for blocked URLs requiring manual verification.

    Args:
        results: List of URL check results
        document_path: Path to the source document
        output_path: Optional path to write task file

    Returns:
        Task file content as string
    """
    blocked = [r for r in results if r.status in (URLStatus.BLOCKED, URLStatus.BROKEN)]

    if not blocked:
        return ""

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    content = f"""# Blocked Citation Verification Tasks

**Source**: {document_path}
**Generated**: {timestamp}
**Total blocked URLs**: {len(blocked)}

## URLs Requiring Manual Verification

"""

    for i, result in enumerate(blocked, 1):
        status_label = "⚠️ Blocked" if result.status == URLStatus.BLOCKED else "❌ Broken"
        reason = result.error or (f"HTTP {result.status_code}" if result.status_code else "Unknown")

        content += f"""### {i}. {status_label}

- **URL**: {result.url}
- **Reason**: {reason}
- [ ] Verify URL manually
- [ ] Update document if URL is permanently unavailable

"""

    content += """---

## Instructions

1. Open each URL in a browser
2. Verify if content is accessible
3. If blocked by paywall/auth, note the access method needed
4. If broken, find replacement URL or remove citation
5. Update the source document accordingly
"""

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

    return content


def verify_document(
    document_path: Path,
    output_tasks_path: Optional[Path] = None,
    mark_inline: bool = True,
    concurrency: int = 10,
    timeout: int = 10,
    cache_dir: Optional[Path] = None,
) -> tuple[str, list[URLResult], str]:
    """
    Verify all citations in a document.

    Args:
        document_path: Path to the document to verify
        output_tasks_path: Optional path for blocked URL task file
        mark_inline: Whether to mark URLs inline in the document
        concurrency: Maximum concurrent requests
        timeout: Timeout per request
        cache_dir: Optional cache directory

    Returns:
        Tuple of (marked_document, results, blocked_tasks)
    """
    with open(document_path, encoding="utf-8") as f:
        document = f.read()

    # Extract URLs
    extracted = extract_urls(document)
    urls = [e.url for e in extracted]

    if not urls:
        return document, [], ""

    # Check URLs
    results = check_urls(
        urls,
        concurrency=concurrency,
        timeout=timeout,
        cache_dir=cache_dir,
    )

    # Mark document if requested
    marked_document = document
    if mark_inline:
        marked_document = mark_urls_inline(document, results)

    # Generate blocked tasks
    blocked_tasks = generate_blocked_tasks(
        results,
        str(document_path),
        output_tasks_path,
    )

    return marked_document, results, blocked_tasks


def print_verification_summary(results: list[URLResult]) -> None:
    """Print a summary of verification results to stdout."""
    available = sum(1 for r in results if r.status == URLStatus.AVAILABLE)
    blocked = sum(1 for r in results if r.status == URLStatus.BLOCKED)
    broken = sum(1 for r in results if r.status == URLStatus.BROKEN)
    redirect = sum(1 for r in results if r.status == URLStatus.REDIRECT)

    total = len(results)
    print("\n📋 Citation Verification Summary")
    print(f"   Total URLs checked: {total}")
    print(f"   ✅ Available: {available}")
    print(f"   🔄 Redirect: {redirect}")
    print(f"   ⚠️  Blocked: {blocked}")
    print(f"   ❌ Broken: {broken}")

    if blocked + broken > 0:
        print(f"\n   ⚠️  {blocked + broken} URLs need manual verification")
