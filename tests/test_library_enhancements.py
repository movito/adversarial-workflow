"""Tests for ADV-0014 library CLI enhancements.

Tests cover:
- library info command
- --dry-run flag for install and update
- --category flag for install
- --yes flag and non-TTY detection
- Configuration system (env > file > defaults)
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from adversarial_workflow.library.commands import (
    library_info,
    library_install,
    library_update,
)
from adversarial_workflow.library.config import LibraryConfig, get_library_config
from adversarial_workflow.library.models import IndexData

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
            "name": "deep-review",
            "provider": "anthropic",
            "path": "evaluators/anthropic/deep-review",
            "model": "claude-3-opus",
            "category": "deep-reasoning",
            "description": "Deep analysis using Claude 3 Opus",
        },
    ],
    "categories": {
        "quick-check": "Fast, cost-effective reviews",
        "deep-reasoning": "Thorough, detailed analysis",
    },
}

SAMPLE_EVALUATOR_YAML = """name: gemini-flash
description: Fast evaluation using Gemini 2.5 Flash
model: gemini/gemini-2.5-flash
api_key_env: GEMINI_API_KEY
timeout: 240
"""

SAMPLE_README = """# gemini-flash

Fast evaluation using Gemini 2.5 Flash.

## API Key

Set `GEMINI_API_KEY` environment variable.

## Changelog

- 1.2.0: Increased timeout to 240s
- 1.1.0: Added structured output
- 1.0.0: Initial release

## Cost

Approximately $0.001-0.005 per evaluation.
"""


@pytest.fixture(autouse=True)
def mock_isatty():
    """Mock stdin.isatty() to return True for most tests."""
    with patch.object(sys.stdin, "isatty", return_value=True):
        yield


class TestLibraryInfo:
    """Tests for library info command."""

    def _mock_fetch_index(self, *_args, **_kwargs):
        return IndexData.from_dict(SAMPLE_INDEX), False

    def _mock_fetch_readme(self, provider: str, name: str):
        return SAMPLE_README

    def _mock_fetch_readme_not_found(self, provider: str, name: str):
        return None

    def test_info_displays_basic_fields(self, capsys):
        """Test that info shows basic evaluator information."""
        with (
            patch.object(
                __import__(
                    "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                ).LibraryClient,
                "fetch_index",
                self._mock_fetch_index,
            ),
            patch.object(
                __import__(
                    "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                ).LibraryClient,
                "fetch_readme",
                self._mock_fetch_readme,
            ),
        ):
            result = library_info("google/gemini-flash")
            assert result == 0
            captured = capsys.readouterr()
            assert "google/gemini-flash" in captured.out
            assert "Version:" in captured.out
            assert "Model:" in captured.out
            assert "Category:" in captured.out
            assert "quick-check" in captured.out

    def test_info_shows_extended_info_from_readme(self, capsys):
        """Test that info extracts and shows extended info from README."""
        with (
            patch.object(
                __import__(
                    "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                ).LibraryClient,
                "fetch_index",
                self._mock_fetch_index,
            ),
            patch.object(
                __import__(
                    "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                ).LibraryClient,
                "fetch_readme",
                self._mock_fetch_readme,
            ),
        ):
            result = library_info("google/gemini-flash")
            assert result == 0
            captured = capsys.readouterr()
            # Should show changelog from README
            assert "Changelog:" in captured.out

    def test_info_gracefully_handles_missing_readme(self, capsys):
        """Test that info works even without README."""
        with (
            patch.object(
                __import__(
                    "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                ).LibraryClient,
                "fetch_index",
                self._mock_fetch_index,
            ),
            patch.object(
                __import__(
                    "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                ).LibraryClient,
                "fetch_readme",
                self._mock_fetch_readme_not_found,
            ),
        ):
            result = library_info("google/gemini-flash")
            assert result == 0
            captured = capsys.readouterr()
            # Should still show basic info
            assert "google/gemini-flash" in captured.out
            assert "Extended info unavailable" in captured.out

    def test_info_invalid_format(self, capsys):
        """Test that invalid format returns error."""
        result = library_info("invalid-spec")
        assert result == 1
        captured = capsys.readouterr()
        assert "Invalid format" in captured.out

    def test_info_evaluator_not_found(self, capsys):
        """Test that missing evaluator returns error."""
        with patch.object(
            __import__(
                "adversarial_workflow.library.client", fromlist=["LibraryClient"]
            ).LibraryClient,
            "fetch_index",
            self._mock_fetch_index,
        ):
            result = library_info("unknown/unknown")
            assert result == 1
            captured = capsys.readouterr()
            assert "Evaluator not found" in captured.out


class TestDryRunInstall:
    """Tests for --dry-run flag on install."""

    def _mock_fetch_index(self, *_args, **_kwargs):
        return IndexData.from_dict(SAMPLE_INDEX), False

    def _mock_fetch_evaluator(self, provider: str, name: str):
        return SAMPLE_EVALUATOR_YAML

    def test_install_dry_run_shows_preview(self, capsys):
        """Test that dry-run shows preview without making changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            eval_dir = Path(tmpdir) / ".adversarial" / "evaluators"
            # Don't create the directory - dry-run shouldn't need it

            with (
                patch.object(
                    __import__(
                        "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                    ).LibraryClient,
                    "fetch_index",
                    self._mock_fetch_index,
                ),
                patch.object(
                    __import__(
                        "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                    ).LibraryClient,
                    "fetch_evaluator",
                    self._mock_fetch_evaluator,
                ),
                patch(
                    "adversarial_workflow.library.commands.get_evaluators_dir",
                    return_value=eval_dir,
                ),
            ):
                result = library_install(["google/gemini-flash"], dry_run=True)
                assert result == 0
                captured = capsys.readouterr()
                assert "Dry run:" in captured.out
                assert "Would install" in captured.out
                assert "preview" in captured.out.lower()
                assert "No changes made" in captured.out

    def test_install_dry_run_no_file_written(self):
        """Test that dry-run doesn't write files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            eval_dir = Path(tmpdir) / ".adversarial" / "evaluators"

            with (
                patch.object(
                    __import__(
                        "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                    ).LibraryClient,
                    "fetch_index",
                    self._mock_fetch_index,
                ),
                patch.object(
                    __import__(
                        "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                    ).LibraryClient,
                    "fetch_evaluator",
                    self._mock_fetch_evaluator,
                ),
                patch(
                    "adversarial_workflow.library.commands.get_evaluators_dir",
                    return_value=eval_dir,
                ),
            ):
                library_install(["google/gemini-flash"], dry_run=True)

                # Verify no file was created
                assert not (eval_dir / "google-gemini-flash.yml").exists()

    def test_dry_run_returns_error_when_all_fail(self, capsys):
        """Test that dry-run returns exit code 1 when all previews fail.

        BugBot issue r2770414341: Dry-run should return error exit code
        when no evaluators could be previewed (e.g., network errors).
        """
        from adversarial_workflow.library.client import NetworkError

        def _mock_fetch_evaluator_fail(self_client, provider: str, name: str):
            raise NetworkError("Network unavailable")

        with tempfile.TemporaryDirectory() as tmpdir:
            eval_dir = Path(tmpdir) / ".adversarial" / "evaluators"

            with (
                patch.object(
                    __import__(
                        "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                    ).LibraryClient,
                    "fetch_index",
                    self._mock_fetch_index,
                ),
                patch.object(
                    __import__(
                        "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                    ).LibraryClient,
                    "fetch_evaluator",
                    _mock_fetch_evaluator_fail,
                ),
                patch(
                    "adversarial_workflow.library.commands.get_evaluators_dir",
                    return_value=eval_dir,
                ),
            ):
                # Dry-run with network failure should return exit code 1
                result = library_install(["google/gemini-flash"], dry_run=True)
                assert result == 1
                captured = capsys.readouterr()
                assert "failed" in captured.out.lower() or "error" in captured.out.lower()


class TestDryRunUpdate:
    """Tests for --dry-run flag on update."""

    def _mock_fetch_index(self, *_args, **_kwargs):
        return IndexData.from_dict(SAMPLE_INDEX), False

    def test_update_dry_run_shows_diff(self, capsys):
        """Test that update dry-run shows diff without applying."""
        with tempfile.TemporaryDirectory() as tmpdir:
            eval_dir = Path(tmpdir) / ".adversarial" / "evaluators"
            eval_dir.mkdir(parents=True)

            # Create an old version file
            old_content = """# Installed from adversarial-evaluator-library
# Source: google/gemini-flash
# Version: 1.0.0
# Installed: 2026-01-01T00:00:00Z

_meta:
  source: adversarial-evaluator-library
  source_path: google/gemini-flash
  version: "1.0.0"
  installed: "2026-01-01T00:00:00Z"

name: gemini-flash
timeout: 180
"""
            (eval_dir / "google-gemini-flash.yml").write_text(old_content)

            # Mock installed evaluator scan
            from adversarial_workflow.library.models import InstalledEvaluatorMeta

            installed_meta = InstalledEvaluatorMeta(
                source="adversarial-evaluator-library",
                source_path="google/gemini-flash",
                version="1.0.0",
                installed="2026-01-01T00:00:00Z",
                file_path=str(eval_dir / "google-gemini-flash.yml"),
            )

            with (
                patch.object(
                    __import__(
                        "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                    ).LibraryClient,
                    "fetch_index",
                    self._mock_fetch_index,
                ),
                patch.object(
                    __import__(
                        "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                    ).LibraryClient,
                    "fetch_evaluator",
                    return_value=SAMPLE_EVALUATOR_YAML,
                ),
                patch(
                    "adversarial_workflow.library.commands.scan_installed_evaluators",
                    return_value=[installed_meta],
                ),
                patch(
                    "adversarial_workflow.library.commands.get_evaluators_dir",
                    return_value=eval_dir,
                ),
            ):
                result = library_update(name="gemini-flash", dry_run=True)
                assert result == 0
                captured = capsys.readouterr()
                assert "dry run" in captured.out.lower()
                assert "no changes" in captured.out.lower()


class TestCategoryInstall:
    """Tests for --category flag on install."""

    def _mock_fetch_index(self, *_args, **_kwargs):
        return IndexData.from_dict(SAMPLE_INDEX), False

    def _mock_fetch_evaluator(self, provider: str, name: str):
        return SAMPLE_EVALUATOR_YAML

    def test_install_category_lists_evaluators(self, capsys):
        """Test that category install lists evaluators before installing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            eval_dir = Path(tmpdir) / ".adversarial" / "evaluators"

            with (
                patch.object(
                    __import__(
                        "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                    ).LibraryClient,
                    "fetch_index",
                    self._mock_fetch_index,
                ),
                patch.object(
                    __import__(
                        "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                    ).LibraryClient,
                    "fetch_evaluator",
                    self._mock_fetch_evaluator,
                ),
                patch(
                    "adversarial_workflow.library.commands.get_evaluators_dir",
                    return_value=eval_dir,
                ),
            ):
                # Use --yes to skip confirmation prompt
                result = library_install([], category="quick-check", yes=True)
                assert result == 0
                captured = capsys.readouterr()
                # Should show evaluators in the category
                assert "quick-check" in captured.out
                assert "google/gemini-flash" in captured.out
                assert "openai/fast-check" in captured.out

    def test_install_category_empty(self, capsys):
        """Test that empty category returns error."""
        with patch.object(
            __import__(
                "adversarial_workflow.library.client", fromlist=["LibraryClient"]
            ).LibraryClient,
            "fetch_index",
            self._mock_fetch_index,
        ):
            result = library_install([], category="nonexistent")
            assert result == 1
            captured = capsys.readouterr()
            assert "No evaluators found in category" in captured.out

    def test_category_dry_run_skips_confirmation(self, capsys):
        """Test that --category --dry-run works without confirmation prompt.

        BugBot issue r2770414329: Category confirmation should be skipped
        for dry-run since no changes are made.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            eval_dir = Path(tmpdir) / ".adversarial" / "evaluators"

            with (
                patch.object(
                    __import__(
                        "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                    ).LibraryClient,
                    "fetch_index",
                    self._mock_fetch_index,
                ),
                patch.object(
                    __import__(
                        "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                    ).LibraryClient,
                    "fetch_evaluator",
                    self._mock_fetch_evaluator,
                ),
                patch(
                    "adversarial_workflow.library.commands.get_evaluators_dir",
                    return_value=eval_dir,
                ),
                # Simulate non-TTY (CI/CD environment)
                patch.object(sys.stdin, "isatty", return_value=False),
            ):
                # With --dry-run (but NOT --yes), should work in non-TTY
                # because dry-run doesn't need confirmation
                result = library_install([], category="quick-check", dry_run=True, yes=False)
                assert result == 0
                captured = capsys.readouterr()
                # Should show dry-run output
                assert "Dry run:" in captured.out or "dry run" in captured.out.lower()


class TestNonInteractiveMode:
    """Tests for --yes flag and non-TTY detection."""

    def _mock_fetch_index(self, *_args, **_kwargs):
        return IndexData.from_dict(SAMPLE_INDEX), False

    def test_yes_flag_skips_prompt(self, capsys):
        """Test that --yes flag allows operation without prompt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            eval_dir = Path(tmpdir) / ".adversarial" / "evaluators"

            with (
                patch.object(
                    __import__(
                        "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                    ).LibraryClient,
                    "fetch_index",
                    self._mock_fetch_index,
                ),
                patch.object(
                    __import__(
                        "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                    ).LibraryClient,
                    "fetch_evaluator",
                    return_value=SAMPLE_EVALUATOR_YAML,
                ),
                patch(
                    "adversarial_workflow.library.commands.get_evaluators_dir",
                    return_value=eval_dir,
                ),
            ):
                # With --yes, should work without TTY
                result = library_install([], category="quick-check", yes=True)
                assert result == 0

    def test_no_tty_without_yes_errors(self, capsys):
        """Test that non-TTY without --yes produces error."""
        # Override the autouse fixture for this specific test
        with (
            patch.object(sys.stdin, "isatty", return_value=False),
            patch.object(
                __import__(
                    "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                ).LibraryClient,
                "fetch_index",
                self._mock_fetch_index,
            ),
        ):
            result = library_install(["google/gemini-flash"])
            assert result == 1
            captured = capsys.readouterr()
            assert "non-interactive mode" in captured.out.lower()


class TestLibraryConfig:
    """Tests for configuration system."""

    def test_config_defaults(self):
        """Test that defaults are used when no config file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = get_library_config(config_path=Path(tmpdir) / "nonexistent.yml")
            assert (
                config.url
                == "https://raw.githubusercontent.com/movito/adversarial-evaluator-library/main"
            )
            assert config.ref == "main"
            assert config.cache_ttl == 3600
            assert config.enabled is True

    def test_config_file_override(self):
        """Test that config file values override defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text(
                yaml.dump(
                    {
                        "library": {
                            "url": "https://custom.url",
                            "ref": "v2.0.0",
                            "cache_ttl": 7200,
                        }
                    }
                )
            )

            config = get_library_config(config_path=config_path)
            assert config.url == "https://custom.url"
            assert config.ref == "v2.0.0"
            assert config.cache_ttl == 7200

    def test_config_env_override(self):
        """Test that env vars override config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text(
                yaml.dump(
                    {
                        "library": {
                            "url": "https://config-file.url",
                        }
                    }
                )
            )

            # Set env var
            with patch.dict(
                os.environ,
                {"ADVERSARIAL_LIBRARY_URL": "https://env-var.url"},
            ):
                config = get_library_config(config_path=config_path)
                # Env var should win
                assert config.url == "https://env-var.url"

    def test_config_no_cache_env(self):
        """Test that ADVERSARIAL_LIBRARY_NO_CACHE disables caching."""
        with patch.dict(os.environ, {"ADVERSARIAL_LIBRARY_NO_CACHE": "1"}):
            config = get_library_config(config_path=Path("/nonexistent"))
            assert config.cache_ttl == 0

    def test_config_cache_ttl_env(self):
        """Test that ADVERSARIAL_LIBRARY_CACHE_TTL overrides TTL."""
        with patch.dict(os.environ, {"ADVERSARIAL_LIBRARY_CACHE_TTL": "600"}):
            config = get_library_config(config_path=Path("/nonexistent"))
            assert config.cache_ttl == 600

    def test_config_no_cache_takes_precedence_over_ttl(self):
        """Test that ADVERSARIAL_LIBRARY_NO_CACHE takes precedence over CACHE_TTL."""
        # When both NO_CACHE and CACHE_TTL are set, NO_CACHE should win
        with patch.dict(
            os.environ,
            {
                "ADVERSARIAL_LIBRARY_NO_CACHE": "1",
                "ADVERSARIAL_LIBRARY_CACHE_TTL": "7200",
            },
        ):
            config = get_library_config(config_path=Path("/nonexistent"))
            # NO_CACHE should always set TTL to 0, even when CACHE_TTL is also set
            assert config.cache_ttl == 0

    def test_config_precedence_env_over_file(self):
        """Test complete precedence: env > file > defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yml"
            config_path.write_text(
                yaml.dump(
                    {
                        "library": {
                            "url": "https://file.url",
                            "ref": "from-file",
                            "cache_ttl": 1800,
                        }
                    }
                )
            )

            with patch.dict(
                os.environ,
                {
                    "ADVERSARIAL_LIBRARY_URL": "https://env.url",
                    # Don't override ref - should come from file
                },
            ):
                config = get_library_config(config_path=config_path)
                # URL from env
                assert config.url == "https://env.url"
                # Ref from file
                assert config.ref == "from-file"
                # TTL from file
                assert config.cache_ttl == 1800

    def test_config_handles_non_dict_yaml(self):
        """Test that config handles YAML files with non-dict content.

        BugBot issue r2770414385: If config.yml contains valid YAML but
        not a dictionary (e.g., a list or scalar), should use defaults
        instead of crashing with AttributeError.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test with list YAML
            config_path = Path(tmpdir) / "list-config.yml"
            config_path.write_text('["this", "is", "a", "list"]')

            config = get_library_config(config_path=config_path)
            # Should not crash, should return defaults
            assert (
                config.url
                == "https://raw.githubusercontent.com/movito/adversarial-evaluator-library/main"
            )
            assert config.ref == "main"

            # Test with scalar YAML
            scalar_path = Path(tmpdir) / "scalar-config.yml"
            scalar_path.write_text("just a string")

            config = get_library_config(config_path=scalar_path)
            # Should not crash, should return defaults
            assert config.ref == "main"

            # Test with null YAML
            null_path = Path(tmpdir) / "null-config.yml"
            null_path.write_text("null")

            config = get_library_config(config_path=null_path)
            # Should not crash, should return defaults
            assert config.ref == "main"

    def test_config_ref_wired_up_in_client(self):
        """Test that ADVERSARIAL_LIBRARY_REF env var is actually used by client.

        BugBot issue r2770414349: The ref field was loaded from config but
        never used by LibraryClient. Now it should affect the base URL.
        """
        from adversarial_workflow.library.client import LibraryClient

        # Test that ref from config is used in URL
        with patch.dict(os.environ, {"ADVERSARIAL_LIBRARY_REF": "v2.0.0"}):
            client = LibraryClient()
            # The base URL should include the ref
            assert "v2.0.0" in client.base_url
            assert client.ref == "v2.0.0"

        # Test default ref
        with patch.dict(os.environ, {}, clear=True):
            # Remove any existing env vars that might interfere
            for key in list(os.environ.keys()):
                if key.startswith("ADVERSARIAL_LIBRARY"):
                    del os.environ[key]

            client = LibraryClient()
            assert "main" in client.base_url
            assert client.ref == "main"

    def test_config_url_wired_up_in_client(self):
        """Test that ADVERSARIAL_LIBRARY_URL env var is actually used by client.

        BugBot PR #23 follow-up: The url field was loaded from config but
        never used by LibraryClient. Now custom URLs should be honored.
        """
        from adversarial_workflow.library.client import LibraryClient

        # Test that custom URL from env var is used
        custom_url = "https://my-private-mirror.example.com/library"
        with patch.dict(os.environ, {"ADVERSARIAL_LIBRARY_URL": custom_url}):
            client = LibraryClient()
            # The base URL should be the custom URL (without trailing slash)
            assert client.base_url == custom_url

        # Test that default URL uses the template (not config.url default)
        with patch.dict(os.environ, {}, clear=True):
            # Remove any existing env vars that might interfere
            for key in list(os.environ.keys()):
                if key.startswith("ADVERSARIAL_LIBRARY"):
                    del os.environ[key]

            client = LibraryClient()
            # Should use default template with main ref
            assert "raw.githubusercontent.com" in client.base_url
            assert "main" in client.base_url
