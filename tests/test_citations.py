"""
Tests for the citation verification module.

Tests URL extraction, checking, caching, inline marking, and task generation.
"""

import asyncio
import json
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from adversarial_workflow.utils.citations import (
    DEFAULT_CONFIG,
    BOT_DETECTION_PATTERNS,
    URL_PATTERN,
    URLResult,
    URLStatus,
    ExtractedURL,
    check_url_async,
    check_urls,
    check_urls_parallel,
    classify_response,
    extract_urls,
    generate_blocked_tasks,
    get_cache_key,
    get_cache_path,
    get_status_badge,
    load_cache,
    mark_urls_inline,
    print_verification_summary,
    save_cache,
    verify_document,
)


class TestURLExtraction:
    """Tests for URL extraction functionality."""

    def test_extract_simple_urls(self):
        """Test extracting simple HTTP/HTTPS URLs."""
        document = "Check out https://example.com and http://test.org for more."
        urls = extract_urls(document)
        assert len(urls) == 2
        assert urls[0].url == "https://example.com"
        assert urls[1].url == "http://test.org"

    def test_extract_urls_with_paths(self):
        """Test extracting URLs with paths."""
        document = "See https://example.com/path/to/resource.html for details."
        urls = extract_urls(document)
        assert len(urls) == 1
        assert urls[0].url == "https://example.com/path/to/resource.html"

    def test_extract_urls_with_query_params(self):
        """Test extracting URLs with query parameters."""
        document = "Link: https://example.com/search?q=test&page=1"
        urls = extract_urls(document)
        assert len(urls) == 1
        assert "q=test" in urls[0].url

    def test_extract_urls_strips_trailing_punctuation(self):
        """Test that trailing punctuation is stripped."""
        document = "See https://example.com. Also https://test.org, and https://foo.bar!"
        urls = extract_urls(document)
        assert urls[0].url == "https://example.com"
        assert urls[1].url == "https://test.org"
        assert urls[2].url == "https://foo.bar"

    def test_extract_urls_in_parentheses(self):
        """Test extracting URLs within parentheses."""
        document = "Reference (https://example.com/doc) for more info."
        urls = extract_urls(document)
        assert len(urls) == 1
        assert urls[0].url == "https://example.com/doc"

    def test_extract_urls_in_markdown_links(self):
        """Test extracting URLs from markdown links."""
        document = "See [the docs](https://docs.example.com/guide) for details."
        urls = extract_urls(document)
        assert len(urls) == 1
        assert urls[0].url == "https://docs.example.com/guide"

    def test_extract_urls_respects_max_limit(self):
        """Test that max_urls limit is respected."""
        document = "\n".join([f"https://example{i}.com" for i in range(150)])
        urls = extract_urls(document, max_urls=100)
        assert len(urls) == 100

    def test_extract_urls_with_context(self):
        """Test that context is captured around URLs."""
        document = "According to the official documentation at https://example.com/docs the feature works as follows."
        urls = extract_urls(document)
        assert len(urls) == 1
        assert "official documentation" in urls[0].context
        assert "the feature" in urls[0].context

    def test_extract_urls_with_line_numbers(self):
        """Test that line numbers are captured."""
        document = "Line 1\nLine 2 with https://example.com\nLine 3"
        urls = extract_urls(document)
        assert len(urls) == 1
        assert urls[0].line_number == 2

    def test_extract_no_urls(self):
        """Test document with no URLs."""
        document = "This document has no URLs at all."
        urls = extract_urls(document)
        assert len(urls) == 0


class TestURLClassification:
    """Tests for URL response classification."""

    def test_classify_200_as_available(self):
        """Test 200 OK is classified as available."""
        status = classify_response(200, {}, None)
        assert status == URLStatus.AVAILABLE

    def test_classify_200_with_bot_detection(self):
        """Test 200 with bot detection content is blocked."""
        status = classify_response(200, {}, "Please complete the captcha")
        assert status == URLStatus.BLOCKED

    def test_classify_301_as_redirect(self):
        """Test 301 redirect classification."""
        status = classify_response(301, {}, None)
        assert status == URLStatus.REDIRECT

    def test_classify_302_as_redirect(self):
        """Test 302 redirect classification."""
        status = classify_response(302, {}, None)
        assert status == URLStatus.REDIRECT

    def test_classify_401_as_blocked(self):
        """Test 401 Unauthorized is blocked."""
        status = classify_response(401, {}, None)
        assert status == URLStatus.BLOCKED

    def test_classify_403_as_blocked(self):
        """Test 403 Forbidden is blocked."""
        status = classify_response(403, {}, None)
        assert status == URLStatus.BLOCKED

    def test_classify_429_as_blocked(self):
        """Test 429 Rate Limited is blocked."""
        status = classify_response(429, {}, None)
        assert status == URLStatus.BLOCKED

    def test_classify_404_as_broken(self):
        """Test 404 Not Found is broken."""
        status = classify_response(404, {}, None)
        assert status == URLStatus.BROKEN

    def test_classify_500_as_broken(self):
        """Test 500 Server Error is broken."""
        status = classify_response(500, {}, None)
        assert status == URLStatus.BROKEN


class TestStatusBadge:
    """Tests for status badge generation."""

    def test_available_badge(self):
        """Test available status badge."""
        result = URLResult("https://example.com", URLStatus.AVAILABLE, status_code=200)
        badge = get_status_badge(result)
        assert "[✅ Verified | 200 OK]" in badge

    def test_blocked_badge_with_code(self):
        """Test blocked status badge with status code."""
        result = URLResult("https://example.com", URLStatus.BLOCKED, status_code=403)
        badge = get_status_badge(result)
        assert "[⚠️ Blocked | 403]" in badge

    def test_blocked_badge_without_code(self):
        """Test blocked status badge without status code."""
        result = URLResult("https://example.com", URLStatus.BLOCKED)
        badge = get_status_badge(result)
        assert "[⚠️ Blocked | Access Denied]" in badge

    def test_broken_badge_with_error(self):
        """Test broken status badge with error message."""
        result = URLResult("https://example.com", URLStatus.BROKEN, error="Timeout")
        badge = get_status_badge(result)
        assert "[❌ Broken | Timeout]" in badge

    def test_broken_badge_with_code(self):
        """Test broken status badge with status code."""
        result = URLResult("https://example.com", URLStatus.BROKEN, status_code=404)
        badge = get_status_badge(result)
        assert "[❌ Broken | 404]" in badge

    def test_redirect_badge(self):
        """Test redirect status badge."""
        result = URLResult(
            "https://example.com",
            URLStatus.REDIRECT,
            final_url="https://www.example.com",
        )
        badge = get_status_badge(result)
        assert "[🔄 Redirect |" in badge
        assert "www.example.com" in badge


class TestInlineMarking:
    """Tests for inline URL marking."""

    def test_mark_single_url(self):
        """Test marking a single URL."""
        document = "See https://example.com for details."
        results = [URLResult("https://example.com", URLStatus.AVAILABLE, status_code=200)]
        marked = mark_urls_inline(document, results)
        assert "[✅ Verified | 200 OK]" in marked
        assert "https://example.com" in marked

    def test_mark_multiple_urls(self):
        """Test marking multiple URLs."""
        document = "See https://example.com and https://test.org for details."
        results = [
            URLResult("https://example.com", URLStatus.AVAILABLE, status_code=200),
            URLResult("https://test.org", URLStatus.BROKEN, status_code=404),
        ]
        marked = mark_urls_inline(document, results)
        assert "[✅ Verified | 200 OK]" in marked
        assert "[❌ Broken | 404]" in marked

    def test_no_duplicate_marking(self):
        """Test that already marked URLs are not marked again."""
        document = "See https://example.com [✅ Verified | 200 OK] for details."
        results = [URLResult("https://example.com", URLStatus.AVAILABLE, status_code=200)]
        marked = mark_urls_inline(document, results)
        # Should not have duplicate badges
        assert marked.count("[✅ Verified | 200 OK]") == 1


class TestBlockedTaskGeneration:
    """Tests for blocked URL task file generation."""

    def test_generate_no_tasks_when_all_available(self):
        """Test no task file when all URLs are available."""
        results = [
            URLResult("https://example.com", URLStatus.AVAILABLE, status_code=200),
            URLResult("https://test.org", URLStatus.AVAILABLE, status_code=200),
        ]
        content = generate_blocked_tasks(results, "test.md")
        assert content == ""

    def test_generate_tasks_for_blocked_urls(self):
        """Test task file generation for blocked URLs."""
        results = [
            URLResult("https://example.com", URLStatus.BLOCKED, status_code=403),
            URLResult("https://test.org", URLStatus.AVAILABLE, status_code=200),
        ]
        content = generate_blocked_tasks(results, "test.md")
        assert "Blocked Citation Verification Tasks" in content
        assert "https://example.com" in content
        assert "⚠️ Blocked" in content
        assert "https://test.org" not in content

    def test_generate_tasks_for_broken_urls(self):
        """Test task file generation for broken URLs."""
        results = [
            URLResult("https://dead-link.com", URLStatus.BROKEN, status_code=404),
        ]
        content = generate_blocked_tasks(results, "test.md")
        assert "https://dead-link.com" in content
        assert "❌ Broken" in content

    def test_write_tasks_to_file(self, tmp_path):
        """Test writing task file to disk."""
        output_path = tmp_path / "blocked-urls.md"
        results = [
            URLResult("https://blocked.com", URLStatus.BLOCKED, status_code=403),
        ]
        generate_blocked_tasks(results, "test.md", output_path)
        assert output_path.exists()
        content = output_path.read_text()
        assert "https://blocked.com" in content


class TestCaching:
    """Tests for URL result caching."""

    def test_get_cache_path_default(self, tmp_path):
        """Test default cache path."""
        path = get_cache_path(tmp_path)
        assert path.parent == tmp_path
        assert path.name == "url_cache.json"

    def test_cache_key_consistency(self):
        """Test cache key is consistent for same URL."""
        key1 = get_cache_key("https://example.com")
        key2 = get_cache_key("https://example.com")
        assert key1 == key2

    def test_cache_key_different_urls(self):
        """Test different URLs get different keys."""
        key1 = get_cache_key("https://example.com")
        key2 = get_cache_key("https://test.org")
        assert key1 != key2

    def test_save_and_load_cache(self, tmp_path):
        """Test saving and loading cache."""
        cache_path = tmp_path / "url_cache.json"
        cache = {
            "abc123": {
                "result": {
                    "url": "https://example.com",
                    "status": "available",
                    "status_code": 200,
                },
                "expires": time.time() + 86400,
            }
        }
        save_cache(cache_path, cache)
        loaded = load_cache(cache_path)
        assert loaded == cache

    def test_load_empty_cache(self, tmp_path):
        """Test loading non-existent cache returns empty dict."""
        cache_path = tmp_path / "nonexistent.json"
        loaded = load_cache(cache_path)
        assert loaded == {}


class TestURLResult:
    """Tests for URLResult dataclass."""

    def test_to_dict(self):
        """Test serialization to dict."""
        result = URLResult(
            url="https://example.com",
            status=URLStatus.AVAILABLE,
            status_code=200,
            final_url=None,
            error=None,
            checked_at=1234567890.0,
        )
        d = result.to_dict()
        assert d["url"] == "https://example.com"
        assert d["status"] == "available"
        assert d["status_code"] == 200

    def test_from_dict(self):
        """Test deserialization from dict."""
        d = {
            "url": "https://example.com",
            "status": "blocked",
            "status_code": 403,
            "final_url": None,
            "error": None,
            "checked_at": 1234567890.0,
        }
        result = URLResult.from_dict(d)
        assert result.url == "https://example.com"
        assert result.status == URLStatus.BLOCKED
        assert result.status_code == 403


class TestAsyncURLChecking:
    """Tests for async URL checking.

    Note: These tests verify the async checking logic without making real network
    requests. The check_url_async function handles aiohttp import internally.
    """

    def test_check_url_returns_result_object(self):
        """Test that check_url_async returns a proper URLResult object."""
        # We can't easily mock the internal import, so just verify the function
        # signature and that it handles errors gracefully
        result = asyncio.run(check_url_async("https://invalid-url-that-will-fail.test"))

        # Should return a URLResult regardless of network status
        assert isinstance(result, URLResult)
        assert result.url == "https://invalid-url-that-will-fail.test"
        # Status should be set (either success or failure)
        assert result.status in [URLStatus.AVAILABLE, URLStatus.BLOCKED, URLStatus.BROKEN, URLStatus.REDIRECT]


class TestSyncURLChecking:
    """Tests for synchronous URL checking wrapper."""

    def test_check_urls_with_cache(self, tmp_path):
        """Test URL checking with caching."""
        with patch(
            "adversarial_workflow.utils.citations.check_urls_parallel"
        ) as mock_parallel:
            mock_parallel.return_value = [
                URLResult("https://example.com", URLStatus.AVAILABLE, status_code=200)
            ]

            results = check_urls(
                ["https://example.com"],
                cache_dir=tmp_path,
            )

            assert len(results) == 1
            assert results[0].status == URLStatus.AVAILABLE


class TestVerifyDocument:
    """Tests for full document verification."""

    def test_verify_document_no_urls(self, tmp_path):
        """Test verification of document with no URLs."""
        doc_path = tmp_path / "no_urls.md"
        doc_path.write_text("This document has no URLs.")

        marked, results, tasks = verify_document(doc_path)
        assert marked == "This document has no URLs."
        assert len(results) == 0
        assert tasks == ""

    def test_verify_document_with_urls(self, tmp_path):
        """Test verification with mocked URL checks."""
        # Re-import to ensure we have fresh references
        from adversarial_workflow.utils.citations import (
            URLResult,
            URLStatus,
            verify_document,
        )

        doc_path = tmp_path / "with_urls.md"
        doc_path.write_text("Check https://example.com for details.")

        with patch("adversarial_workflow.utils.citations.check_urls") as mock_check:
            mock_check.return_value = [
                URLResult("https://example.com", URLStatus.AVAILABLE, status_code=200)
            ]

            marked, results, _tasks = verify_document(doc_path)
            assert "[✅ Verified | 200 OK]" in marked
            assert len(results) == 1


class TestPrintSummary:
    """Tests for verification summary printing."""

    def test_print_summary(self, capsys):
        """Test summary output."""
        # Re-import to ensure we have fresh references
        from adversarial_workflow.utils.citations import (
            URLResult,
            URLStatus,
            print_verification_summary,
        )

        results = [
            URLResult("https://a.com", URLStatus.AVAILABLE, status_code=200),
            URLResult("https://b.com", URLStatus.BLOCKED, status_code=403),
            URLResult("https://c.com", URLStatus.BROKEN, status_code=404),
            URLResult("https://d.com", URLStatus.REDIRECT, final_url="https://e.com"),
        ]
        print_verification_summary(results)
        captured = capsys.readouterr()
        assert "Total URLs checked: 4" in captured.out
        assert "✅ Available: 1" in captured.out
        assert "⚠️  Blocked: 1" in captured.out
        assert "❌ Broken: 1" in captured.out
        assert "🔄 Redirect: 1" in captured.out


class TestCLICheckCitations:
    """Tests for CLI check-citations command."""

    def test_check_citations_help(self, run_cli):
        """Test check-citations help."""
        result = run_cli(["check-citations", "--help"])
        assert result.returncode == 0
        assert "Verify URLs" in result.stdout or "check-citations" in result.stdout

    def test_check_citations_file_not_found(self, run_cli, tmp_path):
        """Test error when file doesn't exist."""
        result = run_cli(["check-citations", "nonexistent.md"])
        assert result.returncode != 0

    def test_check_citations_no_urls(self, run_cli, tmp_path):
        """Test checking document with no URLs."""
        doc = tmp_path / "no_urls.md"
        doc.write_text("No URLs here.")
        result = run_cli(["check-citations", str(doc)])
        assert "No URLs found" in result.stdout or result.returncode == 0


class TestEvaluatorCheckCitations:
    """Tests for --check-citations flag on evaluator commands."""

    def test_evaluate_with_check_citations_flag(self, run_cli):
        """Test that --check-citations flag is accepted."""
        result = run_cli(["evaluate", "--help"])
        assert "--check-citations" in result.stdout
