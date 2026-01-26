"""Tests for scripts/project functionality.

Tests the find_task_file function for boundary-aware task ID matching.
This tests the algorithm from scripts/project to ensure ADV-1 doesn't match ADV-10.
"""

from pathlib import Path
from typing import Optional

import pytest


def find_task_file(task_id: str, project_dir: Path) -> Optional[Path]:
    """Find a task file by ID across all workflow folders.

    Mirror of scripts/project:find_task_file for testing.
    Uses boundary-aware matching to prevent ADV-1 from matching ADV-10, etc.
    """
    tasks_dir = project_dir / "delegation" / "tasks"
    task_id_upper = task_id.upper()

    for folder in tasks_dir.iterdir():
        if not folder.is_dir():
            continue
        for file in folder.glob("*.md"):
            name_upper = file.name.upper()
            if name_upper.startswith(task_id_upper):
                rest = name_upper[len(task_id_upper) :]
                if not rest or not rest[0].isdigit():
                    return file
    return None


class TestFindTaskFile:
    """Test find_task_file() boundary-aware matching."""

    @pytest.fixture
    def task_dir(self, tmp_path: Path) -> Path:
        """Create a temporary task directory structure with test files."""
        tasks_dir = tmp_path / "delegation" / "tasks"
        todo_folder = tasks_dir / "2-todo"
        todo_folder.mkdir(parents=True)

        # Create test task files
        (todo_folder / "ADV-1-first-task.md").write_text("# ADV-1")
        (todo_folder / "ADV-10-tenth-task.md").write_text("# ADV-10")
        (todo_folder / "ADV-100-hundredth-task.md").write_text("# ADV-100")
        (todo_folder / "ADV-11-eleventh-task.md").write_text("# ADV-11")
        (todo_folder / "ASK-0001-question.md").write_text("# ASK-0001")
        (todo_folder / "ASK-0010-another-question.md").write_text("# ASK-0010")

        return tmp_path

    def test_adv1_matches_adv1_only(self, task_dir: Path):
        """ADV-1 should match ADV-1-first-task.md, not ADV-10 or ADV-100."""
        result = find_task_file("ADV-1", task_dir)
        assert result is not None
        assert "ADV-1-first-task.md" in str(result)

    def test_adv1_does_not_match_adv10(self, task_dir: Path):
        """ADV-1 should NOT match ADV-10-tenth-task.md."""
        result = find_task_file("ADV-1", task_dir)
        assert result is not None
        # Should be ADV-1, not ADV-10 or ADV-100 or ADV-11
        assert "ADV-1-" in str(result)
        assert "ADV-10" not in str(result)
        assert "ADV-100" not in str(result)
        assert "ADV-11" not in str(result)

    def test_adv10_matches_adv10_only(self, task_dir: Path):
        """ADV-10 should match ADV-10-tenth-task.md, not ADV-100."""
        result = find_task_file("ADV-10", task_dir)
        assert result is not None
        assert "ADV-10-tenth-task.md" in str(result)

    def test_adv10_does_not_match_adv100(self, task_dir: Path):
        """ADV-10 should NOT match ADV-100-hundredth-task.md."""
        result = find_task_file("ADV-10", task_dir)
        assert result is not None
        assert "ADV-10-" in str(result)
        assert "ADV-100" not in str(result)

    def test_adv100_matches_adv100(self, task_dir: Path):
        """ADV-100 should match ADV-100-hundredth-task.md."""
        result = find_task_file("ADV-100", task_dir)
        assert result is not None
        assert "ADV-100-hundredth-task.md" in str(result)

    def test_case_insensitive_matching(self, task_dir: Path):
        """Task ID matching should be case insensitive."""
        result_upper = find_task_file("ADV-1", task_dir)
        result_lower = find_task_file("adv-1", task_dir)
        assert result_upper is not None
        assert result_lower is not None
        assert result_upper == result_lower

    def test_padded_task_id_ask0001(self, task_dir: Path):
        """ASK-0001 should match ASK-0001-question.md."""
        result = find_task_file("ASK-0001", task_dir)
        assert result is not None
        assert "ASK-0001-question.md" in str(result)

    def test_padded_task_id_does_not_match_different_number(self, task_dir: Path):
        """ASK-0001 should NOT match ASK-0010-another-question.md."""
        result = find_task_file("ASK-0001", task_dir)
        assert result is not None
        assert "ASK-0001-" in str(result)
        assert "ASK-0010" not in str(result)

    def test_nonexistent_task_returns_none(self, task_dir: Path):
        """Non-existent task ID should return None."""
        result = find_task_file("ADV-999", task_dir)
        assert result is None

    def test_empty_tasks_dir_returns_none(self, tmp_path: Path):
        """Empty tasks directory should return None."""
        tasks_dir = tmp_path / "delegation" / "tasks"
        tasks_dir.mkdir(parents=True)
        result = find_task_file("ADV-1", tmp_path)
        assert result is None
