"""Unit tests for the library client module."""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from adversarial_workflow.library.cache import CacheManager
from adversarial_workflow.library.client import (
    LibraryClient,
    LibraryClientError,
    NetworkError,
    ParseError,
)
from adversarial_workflow.library.models import (
    EvaluatorEntry,
    IndexData,
    InstalledEvaluatorMeta,
    UpdateInfo,
)

# Sample test data
SAMPLE_INDEX = {
    "version": "1.2.0",
    "evaluators": [
        {
            "name": "gemini-flash",
            "provider": "google",
            "path": "evaluators/google/gemini-flash",
            "model": "gemini/gemini-2.5-flash",
            "category": "quick-check",
            "description": "Fast evaluation using Gemini 2.5 Flash",
        },
        {
            "name": "fast-check",
            "provider": "openai",
            "path": "evaluators/openai/fast-check",
            "model": "gpt-4o-mini",
            "category": "quick-check",
            "description": "GPT-4o-mini quick review",
        },
        {
            "name": "claude-adversarial",
            "provider": "anthropic",
            "path": "evaluators/anthropic/claude-adversarial",
            "model": "claude-4-opus",
            "category": "adversarial",
            "description": "Adversarial review using Claude",
        },
    ],
    "categories": {
        "quick-check": "Fast, cost-effective reviews",
        "adversarial": "Stress-testing and critical examination",
    },
}

SAMPLE_EVALUATOR_YAML = """name: gemini-flash
description: Fast evaluation using Gemini 2.5 Flash
model: gemini/gemini-2.5-flash
api_key_env: GEMINI_API_KEY
output_suffix: -gemini-flash.md
timeout: 180
prompt: |
  You are a document evaluator...
"""


class TestEvaluatorEntry:
    """Tests for EvaluatorEntry model."""

    def test_from_dict(self):
        data = {
            "name": "gemini-flash",
            "provider": "google",
            "path": "evaluators/google/gemini-flash",
            "model": "gemini/gemini-2.5-flash",
            "category": "quick-check",
            "description": "Fast evaluation",
        }
        entry = EvaluatorEntry.from_dict(data)
        assert entry.name == "gemini-flash"
        assert entry.provider == "google"
        assert entry.category == "quick-check"

    def test_full_name(self):
        entry = EvaluatorEntry(
            name="gemini-flash",
            provider="google",
            path="test",
            model="test",
            category="test",
            description="test",
        )
        assert entry.full_name == "google/gemini-flash"


class TestIndexData:
    """Tests for IndexData model."""

    def test_from_dict(self):
        index = IndexData.from_dict(SAMPLE_INDEX)
        assert index.version == "1.2.0"
        assert len(index.evaluators) == 3
        assert "quick-check" in index.categories

    def test_get_evaluator(self):
        index = IndexData.from_dict(SAMPLE_INDEX)
        entry = index.get_evaluator("google", "gemini-flash")
        assert entry is not None
        assert entry.name == "gemini-flash"

    def test_get_evaluator_not_found(self):
        index = IndexData.from_dict(SAMPLE_INDEX)
        entry = index.get_evaluator("invalid", "invalid")
        assert entry is None

    def test_filter_by_provider(self):
        index = IndexData.from_dict(SAMPLE_INDEX)
        filtered = index.filter_by_provider("google")
        assert len(filtered) == 1
        assert filtered[0].provider == "google"

    def test_filter_by_category(self):
        index = IndexData.from_dict(SAMPLE_INDEX)
        filtered = index.filter_by_category("quick-check")
        assert len(filtered) == 2


class TestInstalledEvaluatorMeta:
    """Tests for InstalledEvaluatorMeta model."""

    def test_from_dict(self):
        data = {
            "source": "adversarial-evaluator-library",
            "source_path": "google/gemini-flash",
            "version": "1.2.0",
            "installed": "2026-02-03T10:00:00Z",
        }
        meta = InstalledEvaluatorMeta.from_dict(data)
        assert meta is not None
        assert meta.provider == "google"
        assert meta.name == "gemini-flash"
        assert meta.version == "1.2.0"

    def test_from_dict_invalid(self):
        meta = InstalledEvaluatorMeta.from_dict(None)
        assert meta is None


class TestUpdateInfo:
    """Tests for UpdateInfo model."""

    def test_status_outdated(self):
        info = UpdateInfo(
            name="test",
            installed_version="1.0.0",
            available_version="1.2.0",
            is_outdated=True,
        )
        assert info.status == "Update available"

    def test_status_up_to_date(self):
        info = UpdateInfo(
            name="test",
            installed_version="1.2.0",
            available_version="1.2.0",
            is_outdated=False,
        )
        assert info.status == "Up to date"

    def test_status_local_only(self):
        info = UpdateInfo(
            name="test",
            installed_version="1.0.0",
            available_version="-",
            is_outdated=False,
            is_local_only=True,
        )
        assert info.status == "Local only"


class TestCacheManager:
    """Tests for CacheManager."""

    def test_set_and_get(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager(cache_dir=Path(tmpdir))
            data = {"test": "value"}
            cache.set("test-key", data)
            result = cache.get("test-key")
            assert result == data

    def test_get_nonexistent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager(cache_dir=Path(tmpdir))
            result = cache.get("nonexistent")
            assert result is None

    def test_cache_expiry(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager(cache_dir=Path(tmpdir), ttl=0)  # Immediate expiry
            cache.set("test-key", {"test": "value"})
            result = cache.get("test-key")
            assert result is None  # Expired immediately

    def test_get_stale(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager(cache_dir=Path(tmpdir), ttl=0)
            data = {"test": "stale"}
            cache.set("test-key", data)
            result = cache.get_stale("test-key")
            assert result == data  # Returns stale data

    def test_invalidate(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager(cache_dir=Path(tmpdir))
            cache.set("test-key", {"test": "value"})
            cache.invalidate("test-key")
            result = cache.get("test-key")
            assert result is None

    def test_clear(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager(cache_dir=Path(tmpdir))
            cache.set("key1", {"a": 1})
            cache.set("key2", {"b": 2})
            count = cache.clear()
            assert count == 2
            assert cache.get("key1") is None
            assert cache.get("key2") is None


class TestLibraryClient:
    """Tests for LibraryClient."""

    def test_fetch_index_caches_result(self):
        """Test that index is cached after successful fetch."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = LibraryClient(cache_dir=Path(tmpdir))

            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps(SAMPLE_INDEX).encode()
            mock_response.__enter__ = lambda s: s
            mock_response.__exit__ = MagicMock(return_value=False)

            with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
                # First call
                index1, from_cache1 = client.fetch_index()
                assert not from_cache1
                assert mock_urlopen.call_count == 1

                # Second call should use cache
                index2, from_cache2 = client.fetch_index()
                assert from_cache2
                assert mock_urlopen.call_count == 1  # Not called again

    def test_fetch_index_no_cache_flag(self):
        """Test that --no-cache bypasses cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = LibraryClient(cache_dir=Path(tmpdir))

            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps(SAMPLE_INDEX).encode()
            mock_response.__enter__ = lambda s: s
            mock_response.__exit__ = MagicMock(return_value=False)

            with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
                # First call
                client.fetch_index(no_cache=True)
                assert mock_urlopen.call_count == 1

                # Second call with no_cache should fetch again
                client.fetch_index(no_cache=True)
                assert mock_urlopen.call_count == 2

    def test_fetch_index_network_error_uses_stale_cache(self):
        """Test fallback to stale cache on network error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Pre-populate cache
            cache = CacheManager(cache_dir=Path(tmpdir))
            cache.set("library-index", SAMPLE_INDEX)

            client = LibraryClient(cache_dir=Path(tmpdir))

            with patch("urllib.request.urlopen", side_effect=Exception("Network error")):
                index, from_cache = client.fetch_index()
                assert from_cache
                assert index.version == "1.2.0"

    def test_fetch_index_network_error_no_cache_raises(self):
        """Test that network error with no cache raises exception."""
        import urllib.error

        with tempfile.TemporaryDirectory() as tmpdir:
            client = LibraryClient(cache_dir=Path(tmpdir))

            # Use URLError which is what urllib raises for network errors
            with patch(
                "urllib.request.urlopen", side_effect=urllib.error.URLError("Network error")
            ):
                with pytest.raises(NetworkError):
                    client.fetch_index()

    def test_fetch_index_invalid_json_raises(self):
        """Test that invalid JSON raises ParseError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = LibraryClient(cache_dir=Path(tmpdir))

            mock_response = MagicMock()
            mock_response.read.return_value = b"not valid json"
            mock_response.__enter__ = lambda s: s
            mock_response.__exit__ = MagicMock(return_value=False)

            with patch("urllib.request.urlopen", return_value=mock_response):
                with pytest.raises(ParseError):
                    client.fetch_index()

    def test_fetch_evaluator(self):
        """Test fetching an evaluator config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = LibraryClient(cache_dir=Path(tmpdir))

            mock_response = MagicMock()
            mock_response.read.return_value = SAMPLE_EVALUATOR_YAML.encode()
            mock_response.__enter__ = lambda s: s
            mock_response.__exit__ = MagicMock(return_value=False)

            with patch("urllib.request.urlopen", return_value=mock_response):
                content = client.fetch_evaluator("google", "gemini-flash")
                assert "name: gemini-flash" in content

    def test_clear_cache(self):
        """Test clearing the cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = LibraryClient(cache_dir=Path(tmpdir))

            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps(SAMPLE_INDEX).encode()
            mock_response.__enter__ = lambda s: s
            mock_response.__exit__ = MagicMock(return_value=False)

            with patch("urllib.request.urlopen", return_value=mock_response):
                client.fetch_index()

            count = client.clear_cache()
            assert count >= 1
