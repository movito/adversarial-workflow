"""
Test Python version compatibility requirements.

This test validates that the project configuration correctly specifies
Python version requirements to match aider-chat dependency constraints.
"""
import sys
import tomllib
from pathlib import Path


def test_python_version_requirement_in_pyproject():
    """Test that pyproject.toml requires Python >=3.10."""
    # Load pyproject.toml
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)

    # Verify requires-python is set correctly
    requires_python = config["project"]["requires-python"]
    assert requires_python == ">=3.10", (
        f"Expected requires-python='>=3.10', got '{requires_python}'. "
        "This should match aider-chat dependency requirements."
    )


def test_python_classifiers_exclude_old_versions():
    """Test that Python 3.8 and 3.9 are not in classifiers."""
    # Load pyproject.toml
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)

    classifiers = config["project"]["classifiers"]

    # Check that 3.8 and 3.9 are NOT in classifiers
    python_38_classifier = "Programming Language :: Python :: 3.8"
    python_39_classifier = "Programming Language :: Python :: 3.9"

    assert python_38_classifier not in classifiers, (
        f"Python 3.8 classifier should be removed: {python_38_classifier}"
    )
    assert python_39_classifier not in classifiers, (
        f"Python 3.9 classifier should be removed: {python_39_classifier}"
    )

    # Check that 3.10+ are still present
    python_310_classifier = "Programming Language :: Python :: 3.10"
    python_311_classifier = "Programming Language :: Python :: 3.11"
    python_312_classifier = "Programming Language :: Python :: 3.12"

    assert python_310_classifier in classifiers, (
        f"Python 3.10 classifier should be present: {python_310_classifier}"
    )
    assert python_311_classifier in classifiers, (
        f"Python 3.11 classifier should be present: {python_311_classifier}"
    )
    assert python_312_classifier in classifiers, (
        f"Python 3.12 classifier should be present: {python_312_classifier}"
    )


def test_current_python_version_compatibility():
    """Test that current Python version meets minimum requirement."""
    # This test ensures we're actually running on a supported Python version
    python_version = sys.version_info
    assert python_version >= (3, 10), (
        f"Current Python version {python_version.major}.{python_version.minor} "
        "is below minimum requirement of 3.10"
    )


def test_black_target_versions_updated():
    """Test that black tool configuration excludes old Python versions."""
    # Load pyproject.toml
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)

    # Check black configuration
    black_config = config.get("tool", {}).get("black", {})
    target_version = black_config.get("target-version", [])

    # Should not include py38 or py39
    assert "py38" not in target_version, "Black should not target py38"
    assert "py39" not in target_version, "Black should not target py39"

    # Should include py310+
    assert "py310" in target_version, "Black should target py310"
    assert "py311" in target_version, "Black should target py311"
    assert "py312" in target_version, "Black should target py312"