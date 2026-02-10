---
description: Workflow for initializing a new development sprint
---

# Flow: Start Sprint

This flow is triggered by the command: **"Start sprint flow"**.
It orchestrates the **Product Manager** and **Architect** to define the cycle's objectives.

## 1. Requirements Alignment (PM)
- Audit the backlog and define the sprint goal.
- Create `sprint_[XX]_plan.md` in `docs/sprints/`.
- Ensure acceptance criteria are "Audit-Ready".

## 2. Technical Tasking (Architect)
- Create a new sprint branch (`sprint/[XX]`).
- Break down requirements into atomic tasks in `task.md`.
- Assign tasks to specific roles (Engineer, QA, etc.).

## 3. Documentation Initialization (Doc Manager)
- Initialize the HTML Docs Hub for the new sprint.
- Update the sidebar navigation.

## 4. Owner Kickoff
- Present the sprint objective and wait for approval to begin EXECUTION.
