#  Code Reviewer Fast

**Source**: .adversarial/inputs/ADV-0071-code-review-input.md
**Evaluator**: code-reviewer-fast
**Model**: gemini/gemini-2.5-flash
**Generated**: 2026-04-15 07:14 UTC

---

### Findings

**[CORRECTNESS]: Direct execution of `cli.py` fails due to relative import**
- **Location**: `adversarial_workflow/cli.py`
- **Edge case**: Running `cli.py` directly as a script (e.g., `python adversarial_workflow/cli.py` from the project root) rather than as a module (`python -m adversarial_workflow.cli`).
- **What happens**: `ImportError: attempted relative import with no known parent package` is raised on the line `from . import __version__`. This is because Python does not treat `adversarial_workflow` as a package when `cli.py` is the top-level script, breaking a common development and debugging pattern. The previous approach (with a hardcoded fallback) would likely have allowed direct execution, albeit with a static version string.
- **Tested?**: No. Current tests use `python -m adversarial_workflow.cli`, which correctly treats `cli.py` as part of a package.

**[ROBUSTNESS]: `__init__.py` import fails if package is not discoverable by `importlib.metadata`**
- **Location**: `adversarial_workflow/__init__.py:_get_version`
- **Edge case**: The `adversarial-workflow` package is not installed (e.g., running from source without an editable install `pip install -e .`, or in an environment where installation is incomplete).
- **What happens**: `importlib.metadata.PackageNotFoundError` is raised, preventing the entire `adversarial_workflow` package from being imported. While removing hardcoded fallbacks is noted as a design decision, for development or CI environments where the package might not always be formally installed or discoverable, this leads to an immediate crash during import rather than a graceful fallback (e.g., `version="unknown"`).
- **Tested?**: No. Tests are run in an environment where the package is installed (likely in editable mode), thus `importlib.metadata` successfully finds the version.

**[ROBUSTNESS]: `cli_python` fixture relies on `pytest` running in the exact target environment**
- **Location**: `tests/conftest.py:cli_python`
- **Edge case**: `pytest` is executed from a Python environment (e.g., a globally installed `pytest` or a base environment) that is *different* from the Python environment where `adversarial-workflow` is actually installed (e.g., a specific virtual environment).
- **What happens**: The `cli_python` fixture uses `sys.executable`, which points to the Python interpreter running `pytest`. If `adversarial-workflow` is not installed or discoverable within *that specific Python interpreter's environment*, then `run_cli`'s call to `python -m adversarial_workflow.cli` will result in a `ModuleNotFoundError` or `PackageNotFoundError` within the subprocess. This is a shift in assumption from the previous `shutil.which("adversarial")` which might have found the correct executable even if the `pytest` runner was in a different environment, as long as the CLI script was on the PATH.
- **Tested?**: No explicit test for this environment mismatch. The `test_version_flag` will fail if this occurs, but the root cause might be obscured.

### Test Gap Summary
| Edge Case | Function | Tested? | Risk |
|---|---|---|---|
| Direct execution of `cli.py` | `adversarial_workflow/cli.py` | No | High |
| `PackageNotFoundError` on import | `adversarial_workflow/__init__.py` | No | Medium |
| `cli_python` environment mismatch | `tests/conftest.py:cli_python` | No | Medium |

### Verdict

- **FAIL**: Correctness bugs found. The inability to run `cli.py` directly is a regression in developer usability and a correctness issue for a script designed to be executable. Robustness gaps regarding package discoverability and test environment assumptions are also present.

---

### Response (Round 2)

**Finding 1 — FIXED**: Reverted `from . import __version__` to direct
`importlib.metadata.version()` call in `cli.py`. This preserves direct execution
(`python adversarial_workflow/cli.py`) while still eliminating the hardcoded
fallback. Both `__init__.py` and `cli.py` call `_get_version("adversarial-workflow")`
— the lookup mechanism is duplicated but the version value cannot drift since
both read from the same `pyproject.toml` metadata.

**Finding 2 — By design**: `PackageNotFoundError` propagation is the intentional
behavior specified in the task spec: "If the package isn't installed,
`_get_version()` raises `PackageNotFoundError` — this should propagate (not be
silently swallowed), since an uninstalled package can't run anyway."

**Finding 3 — Improvement over prior behavior**: The old `shutil.which("adversarial")`
found stale system-wide installs (e.g., `/opt/homebrew/bin/adversarial` reporting
0.9.9 while the venv had 0.9.10). Using `sys.executable` ensures the subprocess
tests the same package as the in-process metadata. If pytest runs from a different
environment than the package, that is a misconfigured test setup.