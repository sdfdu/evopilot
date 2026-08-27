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
