---
name: extension-foundry
description: Analyze repeated EvoPilot observations and compile proven workflows into portable, versioned Agent Skills or other reviewed extensions. Use when improving or extending the agent itself.
---

# Extension Foundry

Evolve capability through promotion, testing, and rollback rather than uncontrolled self-modification.

1. Run `evopilot_analyze_sequences`; use `evopilot_analyze_habits` only to inspect individual actions. Ignore patterns supported by fewer than three observations.
2. At three observations, describe a candidate workflow. At five with at least three successful outcomes, it becomes `draft_ready`. At eight with at least three successes, consider it stable.
3. Prefer a Skill when existing tools are sufficient. Add a deterministic script for repeatable mechanics.
4. Draft an MCP server only when live data, authentication, controlled external actions, or a missing tool genuinely requires one.
5. Use `evopilot_compile_skill` only for a `draft_ready` or `stable` fingerprint, then run `evopilot_validate_skill`. Review both `SKILL.md` and `evopilot.json`, keep the bundle uninstalled, version it, and test it in an isolated workspace. Treat structural validation as a pre-review check, not proof that the workflow executes correctly.
6. Compare success rate, retries, corrections, time, and user acceptance against the previous workflow.
7. When a workflow reaches `draft_ready` or `stable`, proactively explain its evidence before generating it. Compile and validate locally, then present the exact installation approval. After the user explicitly confirms, consume the one-time approval and install the Skill. Never install silently or treat an earlier general preference as installation approval.
8. Roll back when the new workflow performs worse or routes unrelated requests.

Never modify EvoPilot's approval policy through learned behavior. Explicit user instructions outrank learned memories.

When the PreToolUse gate blocks an exact action, show its approval ID and ask the user. Call `evopilot_authorize_once` only after the user explicitly confirms that action, then retry it once.
