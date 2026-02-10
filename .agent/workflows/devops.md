---
description: Workflow for DevOps to ensure environment and deployment stability
---

# DevOps Workflow: Environment & Deployment

1. **Environment Sync**
   - Triggered after a merge to `main` or `sprint/[XX]`.
   - Check `requirements.txt`: Are there new dependencies?
   - If yes, run `pip install -r requirements.txt` and verify virtualenv integrity.

2. **Configuration Audit**
   - Check `config.py` or `.env` templates.
   - Ensure no secrets have been committed to code.
   - Ensure "Production" flags are set correctly for deployment.

3. **Deployment Pipeline (Manual/Simulated)**
   - **Build**: Run any build scripts (e.g., `npm build` if we had JS bundles).
   - **Smoke Test**: Start the app locally (`python api.py`) and verify it launches without errors.
   - **Deploy**: (If cloud configured) Run `gcloud app deploy` or equivalent.

4. **Health Check**
   - Verify the "Health Check" endpoint (e.g. `GET /health` or `/`) returns 200 OK.
   - If failed, rollback immediately and notify `task.md`.
