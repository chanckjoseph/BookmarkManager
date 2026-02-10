---
description: Workflow for the QA Engineer to verify features and prevent regressions
---

# QA Workflow: Verification & Testing

1. **Test Planning**
   - Read `task.md` to identify the feature to verify.
   - Read `implementation_plan.md` and `walkthrough.md` to understand expected behavior.
   - **Rule**: If `walkthrough.md` is missing, reject the task immediately.

2. **Test Execution**
   - **Automated**: Run `pytest tests/` or relevant scripts.
   - **Manual**: Perform the steps listed in `walkthrough.md`.
   - **Exploratory**: Try to break it (Edge cases, empty inputs, weird characters).

3. **Reporting**
   - Create/Update `test_report.md`.
   - Log any failures in `task.md` as new bugs (do not fix them yourself, just report).
   - Only mark the original task as `[VERIFIED]` if ALL tests pass.

4. **Sign-off**
   - Notify the PM/User that verification is complete.
   - Link the `test_report.md` in the notification.
