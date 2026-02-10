---
description: Workflow for starting a new project from scratch
---

# Flow: Start Project

This flow is triggered by the command: **"Start project flow"**. 
It orchestrates the **Architect** and **DevOps** roles to establish a robust project baseline.

## 1. Baseline Requirements (Architect)
- Initialize the directory structure.
- Deploy the Persona rules (`.agent/persona.md`, `.cursorrules`, `.github/copilot-instructions.md`).
- Initialize `task.md` with Sprint 01 goals.

## 2. Environment Setup (DevOps)
- Initialize the git repository.
- Create the virtual environment or project dependencies.
- Sync with the remote repository.

## 3. Initial Planning (Architect + PM)
- Draft the `implementation_plan.md` for the first sprint.
- Call `task_boundary` to set the initial project state.

## 4. Owner Handoff
- Explain the chosen architecture and the next steps for Sprint 01.
