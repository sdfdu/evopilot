# Codex defaults for EvoPilot

EvoPilot works as soon as the plugin is installed and Codex is restarted. To make EvoPilot the default workflow layer for future Codex tasks, install the plugin and add a short global `AGENTS.md` preference.

## One-command setup

From a clone of this repository:

```bash
./scripts/install-codex-defaults.sh
```

The installer is safe to run more than once. It:

- enables the EvoPilot marketplace and plugin when the `codex` CLI is available;
- falls back to appending missing `~/.codex/config.toml` blocks when the CLI is unavailable;
- creates or updates an EvoPilot-managed block in `~/.codex/AGENTS.md`;
- leaves unrelated user settings untouched.

After setup, fully restart Codex and start a new task.

## What gets added

The installer adds this managed block to `~/.codex/AGENTS.md`:

```markdown
<!-- EVOPILOT DEFAULTS START -->
## EvoPilot defaults

Prefer EvoPilot as the default workflow layer for recurring Codex work.

- When a request matches an EvoPilot skill, use the relevant EvoPilot skill before acting.
- Use `evopilot:dev-flow` for coding, debugging, testing, and repository improvements.
- Use `evopilot:idea-lab` for vague ideas or product shaping until the outcome is clear.
- Use `evopilot:tool-operator` for local tool, terminal, browser, and app coordination.
- Use `evopilot:automation-watcher` for reminders, recurring checks, stalled-work follow-ups, reviews, or maintenance monitors.
- Use `evopilot:knowledge-coach` for knowledge organization and evidence-based encouragement.
- Use `evopilot:extension-foundry` for compiling repeated successful workflows into portable skills.
- Keep explicit user instructions, repository `AGENTS.md`, safety rules, and official documentation requirements higher priority than this preference.
- Never store secrets, raw tool inputs, raw tool outputs, or private page contents as EvoPilot memory.
<!-- EVOPILOT DEFAULTS END -->
```

## Manual setup

If you prefer to make the changes yourself:

```bash
codex plugin marketplace add sdfdu/evopilot
codex plugin add evopilot@evopilot
```

Then add the managed block above to `~/.codex/AGENTS.md`, restart Codex, and begin a new task.
