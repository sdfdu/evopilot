# EvoPilot v0.2.0 (local candidate)

## Highlights

- Learn repeated multi-step tool sequences with evidence and success thresholds.
- Preserve memory corrections and conflicts; decay stale inferred confidence without weakening explicit preferences.
- Block risky and unknown Bash/MCP calls before execution, with exact single-use approvals after human confirmation.
- Generate review-only Skill drafts from proven workflows.
- Produce evidence-based weekly learning reports.
- Expand the MCP surface from 7 to 13 tools and migrate v0.1 databases in place.

# EvoPilot v0.1.2

## Fixes

- Negotiate the MCP protocol revision requested during initialization instead of pinning the obsolete `2025-03-26` revision.
- Enable unbuffered UTF-8 I/O for reliable Windows plugin paths and stdio communication.
- Accept a missing or null hook working directory and report the exception type when memory startup fails.
- Test MCP startup from installed paths containing spaces and Unicode characters.

# EvoPilot v0.1.0

The first public release of EvoPilot: a local-first Codex copilot that learns proven work habits and grows through safe, versioned extensions.

## Highlights

- Local SQLite memory with confidence, evidence, scope, risk, and timestamps.
- Privacy-minimized Codex hooks that record tool categories and outcomes—not raw inputs or outputs.
- Transparent habit detection and workflow promotion thresholds.
- Dependency-free stdio MCP server with seven inspectable tools.
- Human-in-the-loop policy for destructive, external, financial, credential, system-wide, publication, and permission-expanding actions.
- Six focused Skills: Idea Lab, Dev Flow, Tool Operator, Knowledge Coach, Automation Watcher, and Extension Foundry.
- Explicit memory deletion and portable JSON export.
- Windows-tested database lifecycle and MCP protocol tests.

## Install

```bash
codex plugin marketplace add sdfdu/evopilot
```

Install EvoPilot from the Codex plugin interface, enable its MCP server under your preferred approval policy, and start a new task.

## Known limitations

- v0.1 analyzes action frequency and outcomes, not complete cross-app sequences.
- Hooks observe Codex tool activity, not every interaction inside arbitrary desktop applications.
- Generated extensions remain a guided promotion workflow rather than unrestricted runtime self-modification.
