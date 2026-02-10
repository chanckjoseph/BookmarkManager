---
description: Standard OS procedure for building a feature in the Sprint Cycle
---

# Feature Development Workflow

1. **Context & Branching**
   - Read `task.md` to identify the next component.
   - Check current branch: `git branch --show-current`.
   - If starting a new feature, create branch: `git checkout -b feat/[task-id]-[short-desc]`.
   - If resuming, ensure you are on the correct branch.

2. **Implementation (The "Think-Before-Tool" Rule)**
   - Review `implementation_plan.md` for architectural constraints.
   - Write code (Frontend/Backend).
   - **Constraint**: Update `walkthrough.md` incrementally as you work.

3. **Verification (Self-Check)**
   - Run existing tests: `pytest tests/` or specific scripts.
   - If no tests exist, create a reproduction script `reproduce_issue.py` or `verify_feature.py`.
   - **Constraint**: Do not proceed until verification passes.

4. **Documentation Sync**
   - Start the documentation phase.
   - Review `walkthrough.md` and ensure it reflects the precise changes.
   - If significant architectural changes, update `implementation_plan.md`.

5. **Handover**
   - Update `task.md`: Mark item as `[x]` (or `[/]` if waiting for review).
   - Commit changes: `git add . && git commit -m "feat: [description]"`.
   - **Notify User**: Request review of `walkthrough.md` and the implementation.
