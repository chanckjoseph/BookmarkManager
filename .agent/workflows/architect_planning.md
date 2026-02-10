---
description: Workflow for the Architect to define technical strategy and breakdown tasks
---

# Architect Workflow: detailed planning & tasking

1. **Analyze Requirements**
   - Read `implementation_plan.md` to ensure alignment with global architecture.
   - Review `sprint_[XX]_plan.md` for specific objectives.
   - Identify technical constraints and dependency chains.

2. **Update Task Tracker**
   - Edit `task.md`.
   - Define atomic tasks with clear IDs (e.g., `<!-- id: 1 -->`).
   - Group tasks by "Phase" or "Component".
   - **Crucial**: Ensure logical ordering (Backend -> Frontend -> Integration).

3. **Architectural Review**
   - If new patterns are introduced, update `implementation_plan.md`.
   - specificy any strict technical constraints (e.g., "Must use SQLite", "No external pip packages").

4. **Handoff**
   - assignments are clear in `task.md`.
   - Notify the user that "Strategy & Tasking" is complete.
