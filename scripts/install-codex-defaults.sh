#!/usr/bin/env bash
set -euo pipefail

CODEX_HOME="${CODEX_HOME:-"$HOME/.codex"}"
CONFIG_FILE="$CODEX_HOME/config.toml"
AGENTS_FILE="$CODEX_HOME/AGENTS.md"

mkdir -p "$CODEX_HOME"
touch "$CONFIG_FILE" "$AGENTS_FILE"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  printf '%s\n' "Python 3 is required to update Codex defaults." >&2
  exit 1
fi

if command -v codex >/dev/null 2>&1; then
  codex plugin marketplace add sdfdu/evopilot || true
  codex plugin add evopilot@evopilot || true
fi

"$PYTHON_BIN" - "$CONFIG_FILE" "$AGENTS_FILE" <<'PY'
from pathlib import Path
import re
import sys

config_path = Path(sys.argv[1])
agents_path = Path(sys.argv[2])

config = config_path.read_text(encoding="utf-8")

blocks = [
    (
        '[marketplaces.evopilot]',
        '[marketplaces.evopilot]\nsource_type = "git"\nsource = "https://github.com/sdfdu/evopilot.git"\n',
    ),
    (
        '[plugins."evopilot@evopilot"]',
        '[plugins."evopilot@evopilot"]\nenabled = true\n',
    ),
]

for header, block in blocks:
    if header not in config:
        if config and not config.endswith("\n"):
            config += "\n"
        if config.strip():
            config += "\n"
        config += block

config_path.write_text(config, encoding="utf-8")

managed = """<!-- EVOPILOT DEFAULTS START -->
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
<!-- EVOPILOT DEFAULTS END -->"""

agents = agents_path.read_text(encoding="utf-8")
pattern = re.compile(
    r"<!-- EVOPILOT DEFAULTS START -->.*?<!-- EVOPILOT DEFAULTS END -->",
    re.DOTALL,
)

if pattern.search(agents):
    agents = pattern.sub(managed, agents)
else:
    if agents and not agents.endswith("\n"):
        agents += "\n"
    if agents.strip():
        agents += "\n"
    agents += managed + "\n"

agents_path.write_text(agents, encoding="utf-8")
PY

printf '%s\n' "EvoPilot Codex defaults are installed."
printf '%s\n' "Restart Codex, then start a new task."
