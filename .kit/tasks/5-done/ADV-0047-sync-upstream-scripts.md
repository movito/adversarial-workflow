# ADV-0047: Upstream Sync — Upstream Scripts (As-Is)

**Status**: Done
**Priority**: High
**Type**: Upstream Sync
**Estimated Effort**: 15 minutes
**Created**: 2026-03-07
**Parent**: ADV-0039
**Upstream Commit**: agentive-starter-kit@0c68f0f

## Summary

Copy new utility scripts from upstream. These are copied verbatim — any bot
findings are upstream's responsibility.

## Scope

### Files to Copy (from upstream `scripts/`)

1. `bootstrap.sh` — Project bootstrap script
2. `check-bots.sh` — Check bot review status
3. `create-agent.sh` — Agent definition creator
4. `gh-review-helper.sh` — GitHub review helper
5. `preflight-check.sh` — Pre-push validation
6. `setup-dev.sh` — Development environment setup
7. `verify-ci.sh` — CI status verification
8. `verify-setup.sh` — Setup verification (if exists)
9. `wait-for-bots.sh` — Wait for bot reviews
10. `logging_config.py` — Python logging configuration
11. `__init__.py` — Scripts package init (if needed)

### Files NOT to Copy

- `scripts/core/project` — Handled separately in ADV-0048 (needs find_task_file patch)
- `scripts/core/pattern_lint.py` — Handled separately in ADV-0049
- `scripts/core/ci-check.sh` — Check if we already have this; if so, take upstream version

### Integration Notes

- All scripts should be executable (`chmod +x`)
- These scripts reference project conventions that may use upstream naming
  (e.g., `agentive-starter-kit`). This is expected — the scripts work on
  generic patterns, not project-specific names
- The `logging_config.py` logger namespace should ideally use
  `adversarial-workflow` but this is a minor issue for a follow-up

## Bot Findings (Deferred to Upstream)

From PR #34, CodeRabbit raised ~20 findings about these scripts:
- bootstrap.sh: depth cap on design materials
- ci-check.sh: minor issues
- setup-dev.sh: python3 fallback, dispatch init reference
- verify-ci.sh: timeout validation, stderr mixing, re-invocation flags
- create-agent.sh: md5 handling, lock loop, AWK quoting
- gh-review-helper.sh: quoting, GraphQL injection, pagination
- preflight-check.sh: various

**All deferred to upstream.** Tag PR description accordingly.

## PR Template

```
Title: sync: Add upstream utility scripts (ADV-0047)

Body:
## Summary
Copies ~11 new utility scripts from agentive-starter-kit@0c68f0f.

Upstream sync — copied verbatim. Bot findings about these files
are upstream's responsibility and will be addressed there.

Part of ADV-0039 (upstream sync).
```

## Acceptance Criteria

- [ ] All listed scripts copied to `scripts/`
- [ ] All shell scripts are executable
- [ ] scripts/core/project NOT included (see ADV-0048)
- [ ] CI passes
- [ ] PR created and merged
