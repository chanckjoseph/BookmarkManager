---
description: Workflow for the Doc Manager to update the HTML Docs Hub
---

# Doc Manager Workflow: Documentation Hub Sync

1. **Drift Audit (The "Fidelity Check")**
   - Read `implementation_plan.md` (The Brain).
   - Read `docs/arch/plan.html` (The Hub).
   - **Goal**: Ensure the HTML matches the Brain 1:1. If not, update the HTML.

2. **Sprint Documentation**
   - Creating a new folder: `docs/sprints/sprint-[XX]/`.
   - Convert `sprint_[XX]_plan.md` -> `index.html`.
   - Convert `test_report.md` -> `test_report.html` (or link to it).

3. **Walkthrough Integration**
   - When a feature is completed (marked in `task.md`), read the `walkthrough.md`.
   - Update the relevant "Feature Page" in `docs/features/` or create a new one.

4. **Sidebar Update**
   - If new pages were created, update `docs/js/sidebar.js` (or static HTML sidebars) to include links.
   - Ensure the "Last Updated" timestamp in the footer is current.

5. **Commit**
   - Commit strict documentation changes: `git commit -m "docs: sync hub with sprint [XX]"`.
