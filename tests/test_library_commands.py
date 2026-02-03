"""Unit tests for library CLI commands."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from adversarial_workflow.library.commands import (
    generate_provenance_header,
    library_check_updates,
    library_install,
    library_list,
    library_update,
    scan_installed_evaluators,
)
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
    ],
    "categories": {
        "quick-check": "Fast, cost-effective reviews",
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


class TestGenerateProvenanceHeader:
    """Tests for provenance header generation."""

    def test_basic_header(self):
        header = generate_provenance_header("google", "gemini-flash", "1.2.0")
        assert "# Installed from adversarial-evaluator-library" in header
        assert "# Source: google/gemini-flash" in header
        assert "# Version: 1.2.0" in header
        assert "_meta:" in header
        assert "source: adversarial-evaluator-library" in header
        assert "source_path: google/gemini-flash" in header
        assert 'version: "1.2.0"' in header

    def test_header_is_valid_yaml(self):
        header = generate_provenance_header("google", "gemini-flash", "1.2.0")
        # Should parse without error
        parsed = yaml.safe_load(header)
        assert parsed is not None
        assert parsed["_meta"]["source"] == "adversarial-evaluator-library"


class TestScanInstalledEvaluators:
    """Tests for scanning installed evaluators."""

    def test_scan_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("adversarial_workflow.library.commands.get_evaluators_dir") as mock_dir:
                mock_dir.return_value = Path(tmpdir) / ".adversarial" / "evaluators"
                result = scan_installed_evaluators()
                assert result == []

    def test_scan_with_library_evaluator(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            eval_dir = Path(tmpdir) / ".adversarial" / "evaluators"
            eval_dir.mkdir(parents=True)

            # Create an installed evaluator with _meta
            eval_content = {
                "_meta": {
                    "source": "adversarial-evaluator-library",
                    "source_path": "google/gemini-flash",
                    "version": "1.2.0",
                    "installed": "2026-02-03T10:00:00Z",
                },
                "name": "gemini-flash",
                "description": "Test",
                "model": "test",
                "api_key_env": "TEST",
                "prompt": "Test",
                "output_suffix": "-test.md",
            }
            with open(eval_dir / "gemini-flash.yml", "w") as f:
                yaml.dump(eval_content, f)

            with patch("adversarial_workflow.library.commands.get_evaluators_dir") as mock_dir:
                mock_dir.return_value = eval_dir
                result = scan_installed_evaluators()
                assert len(result) == 1
                assert result[0].name == "gemini-flash"
                assert result[0].version == "1.2.0"

    def test_scan_ignores_local_evaluators(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            eval_dir = Path(tmpdir) / ".adversarial" / "evaluators"
            eval_dir.mkdir(parents=True)

            # Create a local evaluator without _meta
            eval_content = {
                "name": "custom-eval",
                "description": "Test",
                "model": "test",
                "api_key_env": "TEST",
                "prompt": "Test",
                "output_suffix": "-test.md",
            }
            with open(eval_dir / "custom-eval.yml", "w") as f:
                yaml.dump(eval_content, f)

            with patch("adversarial_workflow.library.commands.get_evaluators_dir") as mock_dir:
                mock_dir.return_value = eval_dir
                result = scan_installed_evaluators()
                assert result == []  # No library evaluators found


class TestLibraryList:
    """Tests for library list command."""

    def _mock_fetch_index(self, *_args, **_kwargs):
        """Mock fetch_index to return sample data."""
        return IndexData.from_dict(SAMPLE_INDEX), False

    def test_list_all(self, capsys):
        with patch.object(
            __import__(
                "adversarial_workflow.library.client", fromlist=["LibraryClient"]
            ).LibraryClient,
            "fetch_index",
            self._mock_fetch_index,
        ):
            result = library_list()
            assert result == 0
            captured = capsys.readouterr()
            assert "gemini-flash" in captured.out
            assert "fast-check" in captured.out
            assert "2 evaluators available" in captured.out

    def test_list_filter_by_provider(self, capsys):
        with patch.object(
            __import__(
                "adversarial_workflow.library.client", fromlist=["LibraryClient"]
            ).LibraryClient,
            "fetch_index",
            self._mock_fetch_index,
        ):
            result = library_list(provider="google")
            assert result == 0
            captured = capsys.readouterr()
            assert "gemini-flash" in captured.out
            assert "1 evaluators shown" in captured.out

    def test_list_filter_by_category(self, capsys):
        with patch.object(
            __import__(
                "adversarial_workflow.library.client", fromlist=["LibraryClient"]
            ).LibraryClient,
            "fetch_index",
            self._mock_fetch_index,
        ):
            result = library_list(category="quick-check")
            assert result == 0
            captured = capsys.readouterr()
            assert "gemini-flash" in captured.out
            assert "fast-check" in captured.out

    def test_list_invalid_provider(self, capsys):
        with patch.object(
            __import__(
                "adversarial_workflow.library.client", fromlist=["LibraryClient"]
            ).LibraryClient,
            "fetch_index",
            self._mock_fetch_index,
        ):
            result = library_list(provider="invalid")
            assert result == 1
            captured = capsys.readouterr()
            assert "No evaluators found for provider" in captured.out


class TestLibraryInstall:
    """Tests for library install command."""

    def _mock_fetch_index(self, *_args, **_kwargs):
        return IndexData.from_dict(SAMPLE_INDEX), False

    def _mock_fetch_evaluator(self, _provider, _name):
        return SAMPLE_EVALUATOR_YAML

    def test_install_success(self):
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
                result = library_install(["google/gemini-flash"])
                assert result == 0

                # Verify file was created with provider-name format
                assert (eval_dir / "google-gemini-flash.yml").exists()

                # Verify provenance header
                content = (eval_dir / "google-gemini-flash.yml").read_text()
                assert "_meta:" in content
                assert "source: adversarial-evaluator-library" in content

    def test_install_invalid_spec(self, capsys):
        with patch.object(
            __import__(
                "adversarial_workflow.library.client", fromlist=["LibraryClient"]
            ).LibraryClient,
            "fetch_index",
            self._mock_fetch_index,
        ):
            result = library_install(["invalid-spec"])
            assert result == 1
            captured = capsys.readouterr()
            assert "Invalid evaluator spec" in captured.out

    def test_install_not_found(self, capsys):
        with patch.object(
            __import__(
                "adversarial_workflow.library.client", fromlist=["LibraryClient"]
            ).LibraryClient,
            "fetch_index",
            self._mock_fetch_index,
        ):
            result = library_install(["unknown/unknown"])
            assert result == 1
            captured = capsys.readouterr()
            assert "Evaluator not found" in captured.out

    def test_install_no_force_existing(self, capsys):
        with tempfile.TemporaryDirectory() as tmpdir:
            eval_dir = Path(tmpdir) / ".adversarial" / "evaluators"
            eval_dir.mkdir(parents=True)

            # Create existing file with new naming convention
            (eval_dir / "google-gemini-flash.yml").write_text("existing content")

            with (
                patch.object(
                    __import__(
                        "adversarial_workflow.library.client", fromlist=["LibraryClient"]
                    ).LibraryClient,
                    "fetch_index",
                    self._mock_fetch_index,
                ),
                patch(
                    "adversarial_workflow.library.commands.get_evaluators_dir",
                    return_value=eval_dir,
                ),
            ):
                result = library_install(["google/gemini-flash"])
                assert result == 1  # No evaluators installed
                captured = capsys.readouterr()
                assert "already exists" in captured.out

    def test_install_with_force(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            eval_dir = Path(tmpdir) / ".adversarial" / "evaluators"
            eval_dir.mkdir(parents=True)

            # Create existing file with new naming convention
            (eval_dir / "google-gemini-flash.yml").write_text("existing content")

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
                result = library_install(["google/gemini-flash"], force=True)
                assert result == 0

                # Verify file was overwritten with new naming convention
                content = (eval_dir / "google-gemini-flash.yml").read_text()
                assert "_meta:" in content


class TestLibraryCheckUpdates:
    """Tests for library check-updates command."""

    def _mock_fetch_index(self, *_args, **_kwargs):
        return IndexData.from_dict(SAMPLE_INDEX), False

    def test_no_installed_evaluators(self, capsys):
        with patch(
            "adversarial_workflow.library.commands.scan_installed_evaluators",
            return_value=[],
        ):
            result = library_check_updates()
            assert result == 0
            captured = capsys.readouterr()
            assert "No library-installed evaluators found" in captured.out


class TestLibraryUpdate:
    """Tests for library update command."""

    def test_update_requires_name_or_all(self, capsys):
        result = library_update()
        assert result == 1
        captured = capsys.readouterr()
        assert "Specify an evaluator name or use --all" in captured.out

    def test_update_no_installed_evaluators(self, capsys):
        with patch(
            "adversarial_workflow.library.commands.scan_installed_evaluators",
            return_value=[],
        ):
            result = library_update(all_evaluators=True)
            assert result == 0
            captured = capsys.readouterr()
            assert "No library-installed evaluators found" in captured.out
