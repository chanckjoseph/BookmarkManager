# Persona Package: Multi-Agent Workflow

This package contains the configuration files and scripts needed to initialize the **Architect Persona** and the **Multi-Agent Development Workflow** in any project.

## Quick Start

### Linux / macOS
1.  Copy `setup_persona.sh` to your project root.
2.  Run the script:
    ```bash
    bash setup_persona.sh
    ```

### Windows
1.  Copy `setup_persona.ps1` to your project root.
2.  Run the script in PowerShell:
    ```powershell
    powershell -ExecutionPolicy Bypass -File setup_persona.ps1
    ```
3.  The following will be created:
    - `.agent/persona.md`: Core identity and behavior protocol.
    - `.agent/workflows/`: Standard operating procedures for all roles.
    - `.cursorrules`: Enforcement for Cursor/Antigravity.
    - `.github/copilot-instructions.md`: Enforcement for VS Code/Copilot.
    - `task.md`: The active project state tracking.

## Configuration
- **Antigravity / Cursor**: Automatic. The agent reads `.cursorrules` on every chat start.
- **VS Code**: Automatic if Using GitHub Copilot (via `.github/copilot-instructions.md`).
- **Other IDEs**: Copy the content of `.agent/persona.md` into your system instructions or project rules.

## Ensuring Persona Adoption (The Cold Boot)
To ensure the agent correctly adopts the **Architect** persona in a new chat session, follow the **Cold Boot Protocol**:
1.  Start your first message with a tool-triggering request, such as **"Review active tasks"** or **"What is our current sprint objective?"**.
2.  This forces the agent to read `.cursorrules` and `.agent/persona.md` before it commits to an identity.
3.  If the agent fails to adopt the persona, explicitly ask: **"Initialize Architect mode from .cursorrules."**

## Deployment Pathways
You can initialize this persona and workflow in any project using two methods:

### 1. Manual Pathway (Script)
Run the setup script appropriate for your OS from the project root:
- **Linux/macOS**: `bash package/setup_persona.sh`
- **Windows**: `powershell -File package/setup_persona.ps1`

### 2. Agent Pathway (Autonomous)
If you are already speaking with an AI agent, you can simply point it to the `package/` folder and say:
> **"Deploy the persona package."**

The agent will use its own tools to initialize the directory structure, deploy the rules, and activate the Architect persona.

## The Architect as Advisor
In this project, the **Architect** acts as your primary strategic advisor. 
- **Proactive Guidance**: The agent will suggest "Flow Commands" based on the project state.
- **Orchestration**: Commands trigger specialized multi-agent workflows.

## Available Flow Commands
To trigger a specific phase of the project, use these exact phrases:
- **"Start project flow"**: For initial repository and environment setup.
- **"Start sprint flow"**: To initialize a new development cycle.
- **"Code review flow"**: For formal audit before merging a sprint.
- **"Debug flow"**: For structured root-cause analysis and verification fixes.

Always check `task.md` to see the current active sprint and role requirements.
