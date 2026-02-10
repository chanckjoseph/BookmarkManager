---
description: Workflow for systematic debugging and root-cause analysis
---

# Flow: Debug Issue

This flow is triggered by the command: **"Debug flow"**.
It orchestrates the **QA Engineer** and **Engineer** to solve a problem with verification.

## 1. Reproduction (QA)
- Create a minimal reproduction script (`reproduce_[issue].py/js`).
- Log the "Observed" vs "Expected" behavior.

## 2. Diagnosis (Engineer)
- Analyze the codebase based on the reproduction script.
- Propose a fix in the `implementation_plan.md` (or a sub-note).

## 3. Implementation (Engineer)
- Apply the fix.
- Ensure the reproduction script now passes.

## 4. Regression Check (QA)
- Run the full test suite to ensure no collateral damage.
- Generate a `debug_report.md`.

## 5. Closure
- Merge the fix and update `task.md`.
