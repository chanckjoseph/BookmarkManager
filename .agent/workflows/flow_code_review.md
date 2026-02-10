---
description: Workflow for conducting a formal code review and audit
---

# Flow: Code Review

This flow is triggered by the command: **"Code review flow"**.
It orchestrates the **PM** and **Architect** to verify work before merging.

## 1. Evidence Audit (PM)
- Review `walkthrough.md` for visual proof of work.
- Compare actual results against the acceptance criteria in the sprint plan.

## 2. Logic & Integrity Audit (Architect)
- Review the code for adherence to global standards.
- Ensure no "Technical Debt" was accidentally introduced.
- Verify that `implementation_plan.md` was followed.

## 3. Verification Check (QA)
- Confirm that `test_report.md` shows all green lights.

## 4. Decision
- **Approve**: Hand off to **Release Manager** for merging.
- **Revise**: Log specific issues in `task.md` and return to the **Engineer**.
