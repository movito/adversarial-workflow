---
description: Show active tasks, recent events, and project progress
---

# Status Dashboard

Show the current state of the project using the dispatch status command.

## Step 1: Run status

```bash
dispatch status --since 2h $ARGUMENTS
```

## Step 2: Report

Present the dashboard output to the user. If the command is not available (dispatch CLI not installed), fall back to manual inspection:

```bash
ls .kit/tasks/3-in-progress/ 2>/dev/null || echo "No tasks in progress"
```

```bash
ls .kit/tasks/2-todo/ 2>/dev/null || echo "No pending tasks"
```

```bash
dispatch log --since 2h 2>/dev/null || echo "No recent events (bus unavailable)"
```
