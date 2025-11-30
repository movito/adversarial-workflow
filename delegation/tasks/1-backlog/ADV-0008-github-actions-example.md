# ADV-0008: GitHub Actions Example Workflow

**Status**: Backlog
**Priority**: low
**Assigned To**: unassigned
**Estimated Effort**: 30-60 minutes
**Created**: 2025-11-30

## Related Tasks

**Depends On**: None
**Blocks**: None
**Related**: ADV-0004 (parent meta-task)
**Split From**: ADV-0004-E1

## Overview

Create an example GitHub Actions workflow file that demonstrates how to use adversarial-workflow in CI/CD pipelines. This helps users quickly onboard and integrate the tool into their projects.

**Context**: Users who want to automate task evaluation in their CI/CD may struggle with initial setup. An example workflow provides a quick starting point.

## Requirements

### Functional Requirements
1. Create `.github/workflows/adversarial-workflow-example.yml`
2. Demonstrate installation from PyPI
3. Show `adversarial init` for project setup
4. Example `adversarial evaluate` with sample task
5. Include failure handling and artifact upload

### Non-Functional Requirements
- [ ] Well-documented with comments explaining each step
- [ ] Works on ubuntu-latest runner
- [ ] Uses caching for faster runs
- [ ] Follows GitHub Actions best practices

## TDD Workflow (Mandatory)

**Note**: This is a documentation/example task - TDD not directly applicable. Use manual testing:

1. **Test Plan**: Verify workflow syntax with `act` or GitHub Actions dry-run
2. **Implementation**: Create the workflow file
3. **Verification**: Run the workflow in a test repo

## Implementation Plan

### Step 1: Create Example Workflow

```yaml
# .github/workflows/adversarial-workflow-example.yml
name: Adversarial Task Evaluation

on:
  pull_request:
    paths:
      - 'tasks/**/*.md'
  workflow_dispatch:
    inputs:
      task_file:
        description: 'Task file to evaluate'
        required: true

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          
      - name: Install adversarial-workflow
        run: pip install adversarial-workflow
        
      - name: Run evaluation
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          adversarial evaluate ${{ github.event.inputs.task_file || 'tasks/example.md' }}
          
      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: evaluation-results
          path: .adversarial/logs/
```

### Step 2: Add README Section

Add documentation in README.md explaining how to use the example workflow.

## Acceptance Criteria

### Must Have
- [ ] Valid GitHub Actions workflow file
- [ ] Workflow runs successfully on ubuntu-latest
- [ ] Demonstrates core adversarial commands
- [ ] Comments explain each step

### Should Have
- [ ] Caching for pip dependencies
- [ ] Artifact upload for evaluation results
- [ ] Manual trigger option

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Create workflow file | 20 min | [ ] |
| Test in sample repo | 20 min | [ ] |
| Documentation | 10 min | [ ] |
| **Total** | **50 min** | [ ] |

## References

- **GitHub Actions docs**: https://docs.github.com/en/actions
- **Python setup action**: https://github.com/actions/setup-python
- **Example location**: `.github/workflows/adversarial-workflow-example.yml`

---

**Template Version**: 2.0.0
**Project**: adversarial-workflow
**Last Updated**: 2025-11-30
