---
name: extension-foundry
description: Analyze repeated EvoPilot observations and promote proven workflows into versioned Skills, plugins, scripts, or MCP drafts. Use when improving or extending the agent itself.
---

# Extension Foundry

Evolve capability through promotion, testing, and rollback rather than uncontrolled self-modification.

1. Run `evopilot_analyze_habits`; ignore patterns supported by fewer than three observations.
2. At three observations, describe a candidate habit. At five with successful outcomes, draft a workflow. At eight with at least three successes, consider it stable.
3. Prefer a Skill when existing tools are sufficient. Add a deterministic script for repeatable mechanics.
4. Draft an MCP server only when live data, authentication, controlled external actions, or a missing tool genuinely requires one.
5. Keep generated artifacts versioned and test them in an isolated workspace.
6. Compare success rate, retries, corrections, time, and user acceptance against the previous workflow.
7. Automatically activate only local low-risk Skills that pass validation. Require human approval before installing or enabling MCP, adding credentials, expanding access, or publishing.
8. Roll back when the new workflow performs worse or routes unrelated requests.

Never modify EvoPilot's approval policy through learned behavior. Explicit user instructions outrank learned memories.
