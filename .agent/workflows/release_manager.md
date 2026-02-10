---
description: Workflow for the Release Manager to manage git branching and merges
---

# Release Manager Workflow: Git Hygiene & Merge Protocol

1. **Prerequisite Check**
   - Read `pm_review.md` to ensure Product Approval is "GO".
   - Read `test_report.md` to ensure QA Verification is "PASSED".
   - Ensure you are on the `sprint/[XX]` branch.

2. **Branch Audit**
   - Check for any lingering `feat/` branches that are merged but not deleted.
   - Run `git branch` to spot "Stale" branches.
   - **Rule**: Only clean up branches that are fully merged and verified.

3. **Merge Protocol (Sprint End)**
   - Checkout `main`.
   - Pull latest remote changes: `git pull origin main`.
   - Merge Sprint Branch: `git merge sprint/[XX] --no-ff`.
   - **Conflict Resolution**: If conflicts arise, request Architect intervention.

4. **Tagging & Push**
   - Tag the release: `git tag -a v[X.Y] -m "Release Sprint [XX]"`.
   - Push to remote: `git push origin main --tags`.

5. **Post-Release Hygiene**
   - Create next sprint branch: `git checkout -b sprint/[XX+1]`.
   - Update `task.md` to reflect the new sprint context.
