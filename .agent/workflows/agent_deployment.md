---
description: Instructions for the agent to deploy the persona package autonomously
---

# Agent-Led Persona Deployment
This workflow is triggered when the owner asks you to **"Deploy the persona package"**. 
It allows you to initialize a project with the Architect persona and multi-agent workflows using your own tools.

## 1. Directory Initialization
- Create the `.agent/workflows` directory.
- Create the `.github` directory if needed for Copilot support.

## 2. Rule Deployment
- Read the template files from the provided `package/` directory.
- Use `write_to_file` to deploy:
    - `.agent/persona.md`
    - `.cursorrules`
    - `.github/copilot-instructions.md`

## 3. Workflow Migration
- Copy all `.md` files from `package/` (or the internal script templates) to `.agent/workflows/`.
- Ensure role-based and flow-based workflows are properly placed.

## 4. Confirmation
- Confirm to the owner that the Architect persona is now active and the multi-agent workflow is ready for a "Cold Boot".
