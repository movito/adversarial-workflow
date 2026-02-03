"""Integration tests for library functionality.

These tests require network access and interact with the real
adversarial-evaluator-library repository.

Run with: pytest tests/test_library_integration.py -v
Skip in CI with: pytest -m "not network"
"""

import tempfile
from pathlib import Path

import pytest

from adversarial_workflow.library.client import LibraryClient
from adversarial_workflow.library.commands import library_install, library_list

# Mark all tests in this module as requiring network access
pytestmark = pytest.mark.network


class TestRealLibraryFetch:
    """Integration tests that fetch from the real library."""

    def test_fetch_real_index(self):
        """Test fetching the real index.json from GitHub."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = LibraryClient(cache_dir=Path(tmpdir))
            index, _from_cache = client.fetch_index(no_cache=True)

            assert index.version  # Has a version
            assert len(index.evaluators) > 0  # Has evaluators
            assert "quick-check" in index.categories  # Has expected category

    def test_fetch_real_evaluator(self):
        """Test fetching a real evaluator config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = LibraryClient(cache_dir=Path(tmpdir))
            yaml_content = client.fetch_evaluator("google", "gemini-flash")

            assert "name: gemini-flash" in yaml_content or "name:" in yaml_content
            assert "prompt:" in yaml_content

    def test_real_library_list(self, capsys):
        """Test listing evaluators from the real library."""
        result = library_list(no_cache=True)
        assert result == 0

        captured = capsys.readouterr()
        assert "evaluators available" in captured.out.lower() or "evaluator" in captured.out.lower()

    def test_real_library_install(self):
        """Test installing an evaluator from the real library."""
        with tempfile.TemporaryDirectory() as tmpdir:
            eval_dir = Path(tmpdir) / ".adversarial" / "evaluators"

            from unittest.mock import patch

            with patch(
                "adversarial_workflow.library.commands.get_evaluators_dir",
                return_value=eval_dir,
            ):
                result = library_install(["google/gemini-flash"])
                assert result == 0

                # Verify file was created with provider-name format
                assert (eval_dir / "google-gemini-flash.yml").exists()

                # Verify content
                content = (eval_dir / "google-gemini-flash.yml").read_text()
                assert "_meta:" in content
                assert "adversarial-evaluator-library" in content

    def test_cache_is_used_on_second_fetch(self):
        """Test that cache is populated and used."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = LibraryClient(cache_dir=Path(tmpdir))

            # First fetch - from network
            index1, from_cache1 = client.fetch_index(no_cache=True)
            assert not from_cache1

            # Second fetch - from cache
            index2, from_cache2 = client.fetch_index()
            assert from_cache2
            assert index1.version == index2.version


class TestOfflineScenarios:
    """Tests for offline handling scenarios."""

    def test_uses_stale_cache_when_offline(self):
        """Test that stale cache is used when network fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = LibraryClient(cache_dir=Path(tmpdir))

            # First, populate the cache
            index1, _ = client.fetch_index(no_cache=True)

            # Now create a client with invalid URL (simulating offline)
            offline_client = LibraryClient(
                base_url="https://invalid.example.com",
                cache_dir=Path(tmpdir),
            )

            # Should fall back to stale cache
            index2, from_cache = offline_client.fetch_index()
            assert from_cache
            assert index1.version == index2.version
