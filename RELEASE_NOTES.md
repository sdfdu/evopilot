# EvoPilot v0.4.0 (local candidate)

- Surface the strongest promotion-ready workflow automatically at task startup, including evidence and an instruction to explain it before generation.
- Add `prepare-skill-install` and `install-skill` CLI commands plus matching MCP tools.
- Bind each installation approval to the reviewed bundle contents and destination, consume it once, and mark the installed evidence manifest.
- Preserve the human confirmation boundary: generation and validation are automatic, installation is immediate only after exact approval.

# EvoPilot v0.3.3

## Changed

- Make the SessionStart hook inject default EvoPilot operating guidance in every new task after plugin installation and Codex restart.
- Clarify that relevant EvoPilot Skills and MCP tools should be applied automatically when a task matches, while explicit user instructions and safety approvals still take priority.
- Update README and how-to-use documentation to distinguish automatic startup guidance from optional explicit prompts.

# EvoPilot v0.3.2 (local candidate)

## Added

- Add `quickstart` for copy-pasteable first-run guidance in Codex.
- Add `WHAT_HAPPENED.md` to compiled demo and workflow bundles so reviewers can understand the artifact without reading JSON first.
- Add `forget --all` and `evopilot_forget_all` for a full memory reset that still keeps deletion audit events.
- Add `evopilot_quickstart`, expanding the MCP surface from 17 to 19 tools.
- Add how-to-use, privacy, and Skill lifecycle documentation.
- Add GitHub Actions CI for unit tests, doctor, demo generation, and demo validation.
- Add GitHub issue templates for bugs and feature requests.

## Changed

- Make `doctor` point to `quickstart` as the next step after healthy checks.
- Improve README onboarding for installed Codex plugin users.

# EvoPilot v0.3.1 (local candidate)

## Highlights

- Add deterministic validation and a transparent 0–100 quality score for compiled Skill bundles.
- Detect malformed frontmatter, inconsistent evidence, false promotion claims, missing safety boundaries, and unsafe review state.
- Keep simulated bundles in `demo_only` status even when they pass structural validation.
- Expose validation through `validate-skill` and `evopilot_validate_skill`, expanding the MCP surface from 16 to 17 tools.
- State validation limits explicitly: it does not execute workflows or prove universal client compatibility.

# EvoPilot v0.3.0

## Highlights

- Reposition EvoPilot as a workflow compiler for AI agents.
- Compile proven workflows into portable Open Agent Skills bundles containing `SKILL.md` and evidence-rich `evopilot.json`.
- Add a deterministic 60-second demo that is clearly simulated and never modifies learned user data.
- Add `doctor` diagnostics for the Python runtime, plugin files, and local database.
- Expose `evopilot_compile_skill`, `evopilot_demo`, and `evopilot_doctor`, expanding the MCP surface from 13 to 16 tools.
- Preserve the old `draft-skill` command and MCP tool as compatibility aliases.

# EvoPilot v0.2.0

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
