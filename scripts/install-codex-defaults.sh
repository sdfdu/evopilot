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

if [ "${EVOPILOT_SKIP_CODEX_CLI:-0}" != "1" ] && command -v codex >/dev/null 2>&1; then
  if ! codex plugin marketplace add sdfdu/evopilot; then
    printf '%s\n' "Warning: codex marketplace setup failed; applying config fallback." >&2
  fi
  if ! codex plugin add evopilot@evopilot; then
    printf '%s\n' "Warning: codex plugin setup failed; applying config fallback." >&2
  fi
fi

"$PYTHON_BIN" - "$CONFIG_FILE" "$AGENTS_FILE" <<'PY'
from pathlib import Path
import re
import sys

config_path = Path(sys.argv[1])
agents_path = Path(sys.argv[2])

config = config_path.read_text(encoding="utf-8")

def upsert_table(text: str, header: str, values: dict[str, str]) -> str:
    pattern = re.compile(
        rf"(?ms)^(?P<header>{re.escape(header)}\n)(?P<body>.*?)(?=^\[|\Z)"
    )
    match = pattern.search(text)
    if not match:
        block = header + "\n" + "".join(f"{key} = {value}\n" for key, value in values.items())
        if text and not text.endswith("\n"):
            text += "\n"
        if text.strip():
            text += "\n"
        return text + block

    body = match.group("body")
    for key, value in values.items():
        key_pattern = re.compile(rf"(?m)^({re.escape(key)}\s*=\s*).*$")
        replacement = rf"\g<1>{value}"
        if key_pattern.search(body):
            body = key_pattern.sub(replacement, body, count=1)
        else:
            if body and not body.endswith("\n"):
                body += "\n"
            body += f"{key} = {value}\n"
    return text[:match.start("body")] + body + text[match.end("body"):]

config = upsert_table(
    config,
    "[marketplaces.evopilot]",
    {
        "source_type": '"git"',
        "source": '"https://github.com/sdfdu/evopilot.git"',
    },
)
config = upsert_table(
    config,
    '[plugins."evopilot@evopilot"]',
    {"enabled": "true"},
)

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
