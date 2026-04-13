# Task Management

This folder contains task specifications for adversarial-workflow development.

## Folder Structure

| Folder | Linear Status | Description |
|--------|---------------|-------------|
| `1-backlog/` | Backlog | Planned but not started |
| `2-todo/` | Todo | Ready to work on |
| `3-in-progress/` | In Progress | Currently being worked on |
| `4-in-review/` | In Review | Awaiting review |
| `5-done/` | Done | Completed |
| `6-canceled/` | Canceled | Won't be implemented |
| `7-blocked/` | Blocked | Waiting on dependencies |
| `8-archive/` | - | Historical reference |
| `9-reference/` | - | Templates and docs |

## Task Naming

Tasks use the prefix `ADV-` (Adversarial):
- `ADV-0001-description.md`
- `ADV-0002-another-task.md`

## Creating Tasks

1. Copy template from `9-reference/templates/task-template.md`
2. Place in appropriate folder (usually `2-todo/`)
3. Fill in details
4. Run evaluation if needed: `adversarial evaluate <task-file>`
