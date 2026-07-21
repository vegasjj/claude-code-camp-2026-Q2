---
name: tba-mud
description: Connects to tbaMUD on localhost:4000 using dummy/helloworld, and runs commands to play and navigate the MUD's world. Supports both single/multi-command batch execution and interactive sessions.
---

# tbaMUD Navigation & Play Skill

This skill allows the agent to connect to, play, and navigate the tbaMUD world using the `dummy` character (password: `helloworld`).

## Component Files
*   **MUD Client Script**: [scripts/mud_client.py](file:///workspaces/claude-code-camp-2026-Q2/week0_explore/explore_architecture/002_agent_skills/.agents/skills/tba-mud/scripts/mud_client.py) - Manages connection via `nc` subprocess, handles automatic login, and strips ANSI codes.
*   **Command Reference**: [references/commands.md](file:///workspaces/claude-code-camp-2026-Q2/week0_explore/explore_architecture/002_agent_skills/.agents/skills/tba-mud/references/commands.md) - Contains standard in-game navigation, equipment, inventory, and object interaction commands.

---

## How to Use This Skill

### 1. Single Command Execution (Batch Mode)
For running one command or a list of comma-separated commands and getting the results immediately:

```bash
# Run a single command:
python3 .agents/skills/tba-mud/scripts/mud_client.py --cmd "look"

# Run multiple commands sequentially:
python3 .agents/skills/tba-mud/scripts/mud_client.py --cmds "look, south, west, look, east, north"
```

### 2. Interactive Terminal Session (Persistent Mode)
For running a continuous session where the agent can send commands to a running instance and read state over time:

1.  **Launch the interactive client** in a persistent terminal:
    ```bash
    python3 .agents/skills/tba-mud/scripts/mud_client.py --interactive
    ```
2.  **Wait for the client** to output `MUD_CLIENT_READY>`.
3.  **Send commands** using the `manage_task` tool with action `send_input` to the task ID of the running command:
    *   Input: `look`
    *   Input: `south`
    *   Input: `score`
4.  **Exit** the session by sending `exit` or `quit`.

---

## In-Game Prompt and Output Format
The client automatically turns off ANSI color formatting (`color off`) upon login to ensure clean, readable plaintext.

The standard prompt looks like:
`22H 100M 2V (news) (motd) > `
*   `22H`: Current Hit Points (HP)
*   `100M`: Current Mana
*   `2V`: Current Moves/Vigor
*   `>`: The command input prompt.

Use the [Command Reference](file:///workspaces/claude-code-camp-2026-Q2/week0_explore/explore_architecture/002_agent_skills/.agents/skills/tba-mud/references/commands.md) for a comprehensive list of actions.
