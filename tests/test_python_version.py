"""
Test Python version compatibility requirements.

This test validates that the project configuration correctly specifies
Python version requirements for the adversarial-workflow package.
"""

import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


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
        "Python 3.10+ is required for adversarial-workflow."
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


def test_ruff_target_version_updated():
    """Test that ruff tool configuration targets py310+."""
    # Load pyproject.toml
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)

    # Check ruff configuration (replaced black)
    ruff_config = config.get("tool", {}).get("ruff", {})
    target_version = ruff_config.get("target-version", "")

    # Should target py310
    assert target_version == "py310", f"Ruff should target py310, got {target_version}"
