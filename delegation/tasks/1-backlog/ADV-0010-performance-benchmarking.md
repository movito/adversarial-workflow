# ADV-0010: Performance Benchmarking

**Status**: Backlog
**Priority**: low
**Assigned To**: unassigned
**Estimated Effort**: 1-2 hours
**Created**: 2025-11-30

## Related Tasks

**Depends On**: None
**Blocks**: None
**Related**: ADV-0004 (parent meta-task)
**Split From**: ADV-0004-E3

## Overview

Create performance benchmarks to establish baseline metrics for adversarial-workflow operations. This enables future performance comparisons and helps identify regressions.

**Context**: As the tool grows, it's valuable to track performance of key operations like init, evaluate, and split. Baselines help detect regressions and guide optimization.

## Requirements

### Functional Requirements
1. Benchmark `adversarial init` time
2. Benchmark `adversarial split` on various file sizes
3. Benchmark template rendering
4. Benchmark config file operations
5. Create reproducible benchmark script

### Non-Functional Requirements
- [ ] Benchmarks run in < 5 minutes total
- [ ] Results stored in standard format (JSON/CSV)
- [ ] Easy to run locally and in CI
- [ ] Minimal dependencies

## TDD Workflow (Mandatory)

### Red Phase
1. Create benchmark test file with timing assertions
2. Define acceptable performance thresholds
3. Tests fail if thresholds exceeded

### Green Phase
1. Implement benchmark runner script
2. Capture timing data
3. Store results for comparison

### Refactor Phase
1. Add CI integration (optional)
2. Create performance dashboard or report
3. Document how to run benchmarks

## Implementation Plan

### Step 1: Create Benchmark Script

```python
# benchmarks/run_benchmarks.py
import time
import tempfile
import json
from pathlib import Path

def benchmark_init():
    """Benchmark adversarial init command."""
    with tempfile.TemporaryDirectory() as tmpdir:
        start = time.perf_counter()
        # Run init
        result = subprocess.run(
            ["adversarial", "init", tmpdir],
            capture_output=True
        )
        elapsed = time.perf_counter() - start
        return {"operation": "init", "time_seconds": elapsed}

def benchmark_split(file_lines):
    """Benchmark split on file of given size."""
    # Create test file, measure split time
    pass

def main():
    results = []
    results.append(benchmark_init())
    results.append(benchmark_split(100))
    results.append(benchmark_split(500))
    results.append(benchmark_split(1000))
    
    with open("benchmarks/results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
```

### Step 2: Define Thresholds

| Operation | Expected | Threshold | Notes |
|-----------|----------|-----------|-------|
| init | < 1s | 2s | Template copying |
| split (100 lines) | < 0.5s | 1s | Small file |
| split (500 lines) | < 1s | 2s | Medium file |
| split (1000 lines) | < 2s | 4s | Large file |

### Step 3: Create Test File

```python
# tests/test_performance.py
import pytest

@pytest.mark.benchmark
def test_init_performance(benchmark):
    result = benchmark(run_init)
    assert result < 2.0, "Init took too long"
```

## Acceptance Criteria

### Must Have
- [ ] Benchmark script for core operations
- [ ] Baseline results documented
- [ ] Reproducible on developer machines

### Should Have
- [ ] CI integration for regression detection
- [ ] Performance thresholds defined
- [ ] Historical comparison support

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Create benchmark script | 45 min | [ ] |
| Run and document baselines | 30 min | [ ] |
| Add pytest integration | 30 min | [ ] |
| **Total** | **1.75 hrs** | [ ] |

## References

- **pytest-benchmark**: https://pytest-benchmark.readthedocs.io/
- **Benchmark location**: `benchmarks/`
- **Results location**: `benchmarks/results.json`

---

**Template Version**: 2.0.0
**Project**: adversarial-workflow
**Last Updated**: 2025-11-30
