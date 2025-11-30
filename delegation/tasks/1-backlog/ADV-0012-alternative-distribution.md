# ADV-0012: Alternative Package Distribution

**Status**: Backlog
**Priority**: low
**Assigned To**: unassigned
**Estimated Effort**: 1-2 hours per channel
**Created**: 2025-11-30

## Related Tasks

**Depends On**: Stable PyPI release
**Blocks**: None
**Related**: ADV-0004 (parent meta-task), ADV-0007 (PyPI release)
**Split From**: ADV-0004-E6

## Overview

Publish adversarial-workflow through alternative distribution channels beyond PyPI to reach users with different installation preferences.

**Context**: Some users prefer installing via conda, Homebrew, Docker, or system package managers. Alternative distribution expands reach and simplifies installation in specific environments.

## Requirements

### Functional Requirements
1. Package available through alternative channels
2. Installation instructions documented
3. Version parity with PyPI release
4. Automated publishing workflow (if feasible)

### Non-Functional Requirements
- [ ] Same functionality as PyPI package
- [ ] Clear documentation per channel
- [ ] Maintainable long-term

## Distribution Candidates

| Channel | Priority | Effort | Target Users |
|---------|----------|--------|--------------|
| Docker image | High | 1 hr | CI/CD, containers |
| Homebrew | Medium | 1.5 hrs | macOS users |
| conda-forge | Medium | 2 hrs | Data science users |
| Snap | Low | 1.5 hrs | Linux users |

## Implementation Plan

### Option 1: Docker Image

```dockerfile
# Dockerfile
FROM python:3.12-slim

LABEL maintainer="adversarial-workflow"
LABEL version="0.5.0"

RUN pip install --no-cache-dir adversarial-workflow

WORKDIR /workspace
ENTRYPOINT ["adversarial"]
```

Usage:
```bash
docker run -v $(pwd):/workspace -e OPENAI_API_KEY adversarial-workflow evaluate task.md
```

### Option 2: Homebrew Formula

```ruby
# Formula/adversarial-workflow.rb
class AdversarialWorkflow < Formula
  desc "Multi-stage AI code review system"
  homepage "https://github.com/movito/adversarial-workflow"
  url "https://pypi.io/packages/source/a/adversarial-workflow/adversarial_workflow-0.5.0.tar.gz"
  sha256 "..."
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end
end
```

### Option 3: conda-forge Recipe

```yaml
# recipe/meta.yaml
package:
  name: adversarial-workflow
  version: "0.5.0"

source:
  url: https://pypi.io/packages/source/a/adversarial-workflow/adversarial_workflow-{{ version }}.tar.gz
  sha256: ...

build:
  number: 0
  script: python -m pip install . -vv

requirements:
  host:
    - python >=3.10
    - pip
  run:
    - python >=3.10
    - pyyaml >=6.0
    - python-dotenv >=0.19.0
    - aider-chat >=0.86.0
```

### Option 4: Snap Package

```yaml
# snap/snapcraft.yaml
name: adversarial-workflow
version: '0.5.0'
summary: Multi-stage AI code review system
description: |
  Adversarial workflow for task evaluation using GPT-4o.

grade: stable
confinement: strict

apps:
  adversarial:
    command: bin/adversarial

parts:
  adversarial:
    plugin: python
    python-packages:
      - adversarial-workflow
```

## Acceptance Criteria

### Must Have (per channel)
- [ ] Package installable from channel
- [ ] `adversarial --version` works
- [ ] Core commands functional
- [ ] Documentation updated

### Should Have
- [ ] Automated publishing in release workflow
- [ ] Version sync with PyPI

## Time Estimate

| Channel | Time | Status |
|---------|------|--------|
| Docker | 1 hr | [ ] |
| Homebrew | 1.5 hrs | [ ] |
| conda-forge | 2 hrs | [ ] |
| Snap | 1.5 hrs | [ ] |
| **Total** | **6 hrs** | [ ] |

## References

- **PyPI**: https://pypi.org/project/adversarial-workflow/
- **Docker Hub**: TBD
- **Homebrew taps**: https://docs.brew.sh/How-to-Create-and-Maintain-a-Tap
- **conda-forge**: https://conda-forge.org/docs/maintainer/adding_pkgs.html

---

**Template Version**: 2.0.0
**Project**: adversarial-workflow
**Last Updated**: 2025-11-30
