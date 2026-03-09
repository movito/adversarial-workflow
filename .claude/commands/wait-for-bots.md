---
description: Wait for BugBot and CodeRabbit to post reviews (polling with backoff)
argument-hint: "[optional PR number]"
---

# Wait for Bot Reviews

Wait for both bots to review the current PR. Polls every 30 seconds for up
to 10 minutes.

## Step 1: Run the wait-for-bots script

```bash
./scripts/core/wait-for-bots.sh $ARGUMENTS
```

The script polls check-bots.sh every 30 seconds and prints progress to stderr.
When both bots are CURRENT, it prints the full status to stdout and exits 0.
If timeout is reached (10 minutes), it exits 1.

## Step 2: Report result

- **If exit 0**: Both bots have reviewed HEAD. Report the final status and
  suggest `/triage-threads` if unresolved threads exist.
- **If exit 1**: Timeout reached. Report which bot(s) are still STALE/MISSING
  and suggest manual investigation with `/check-bots`.

## Options

Override defaults by passing flags:

```bash
./scripts/core/wait-for-bots.sh --interval 15 --timeout 300
```

| Flag | Default | Description |
|------|---------|-------------|
| `--interval SECONDS` | 30 | Poll interval |
| `--timeout SECONDS` | 600 | Max wait time |
| `PR_NUMBER` | auto-detect | Positional PR number |
