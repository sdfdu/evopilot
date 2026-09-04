<div align="center">

# EvoPilot

### Turn repeated AI-agent work into evidence-backed, quality-checked Skills.

[![CI](https://github.com/sdfdu/evopilot/actions/workflows/ci.yml/badge.svg)](https://github.com/sdfdu/evopilot/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/sdfdu/evopilot)](https://github.com/sdfdu/evopilot/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

![EvoPilot workflow compiler demo](docs/demo.gif)

AI agents repeatedly rediscover useful workflows. EvoPilot observes privacy-minimized outcomes, detects sequences that consistently work, and compiles qualified workflows into portable [Open Agent Skills](https://agentskills.io/) bundles.

It does not train model weights, store raw tool logs, or silently expand permissions. Every generated bundle includes its evidence, provenance, review state, and quality findings.

## Try it in 60 seconds

Requirements: Python 3.10+.

```bash
git clone https://github.com/sdfdu/evopilot.git
cd evopilot
python plugins/evopilot/scripts/evopilot.py doctor
python plugins/evopilot/scripts/evopilot.py demo --destination ./evopilot-demo
python plugins/evopilot/scripts/evopilot.py validate-skill ./evopilot-demo/workspace-inspect-workspace-apply-patch-terminal
```

The deterministic demo is marked `demo_only` and never enters learned history. Inspect these files:

```text
evopilot-demo/workspace-inspect-workspace-apply-patch-terminal/
├── SKILL.md
├── evopilot.json
├── QUALITY_REPORT.md
└── WHAT_HAPPENED.md
```

## Why EvoPilot instead of memory or prompts?

| Approach | Remembers facts | Captures a repeatable workflow | Evidence and quality gates | Portable and versionable |
|---|---:|---:|---:|---:|
| Chat history | Yes | No | No | No |
| Saved prompt | Sometimes | Manually | No | Sometimes |
| Agent memory | Yes | Sometimes | Usually no | Usually no |
| EvoPilot Skill | Yes | Yes | Yes | Yes |

## How it works

```text
work normally → measure outcomes → detect repeated success → compile → validate → review → install
```

1. Hooks record tool categories and outcomes, never raw arguments or responses.
2. Transparent thresholds identify repeated workflows instead of promoting one lucky run.
3. The compiler creates `SKILL.md`, provenance, evidence, and a human-readable quality report.
4. Structural and semantic gates block generic, repetitive, unsafe, or underspecified Skills.
5. Installation requires an exact one-time confirmation bound to the reviewed bundle and destination.

| State | Evidence requirement |
|---|---|
| Candidate | At least 3 observations |
| Draft ready | At least 5 observations and 3 successes |
| Stable | At least 8 observations and 3 successes |

## Install in Codex

```bash
codex plugin marketplace add sdfdu/evopilot
codex plugin add evopilot@evopilot
```

Restart Codex, start a new task, and ask:

```text
Run the EvoPilot 60-second workflow compiler demo.
```

To make EvoPilot the default workflow layer for future tasks:

```bash
./scripts/install-codex-defaults.sh
```

See [How to use EvoPilot](docs/how-to-use.md) for real-work commands and the Skill review flow.

## What ships today

- Local SQLite memory with corrections, conflicts, history, evidence, and confidence decay.
- Privacy-minimized Codex hooks and a fail-closed safety gate.
- Repeated workflow detection with visible evidence thresholds.
- Portable Skill compilation with provenance and review state.
- Structural validation plus semantic quality assessment and annotations.
- Install blocking for generic, repetitive, unsafe, low-evidence, or underspecified Skills.
- A dependency-free MCP server exposing 23 inspectable tools.
- Six focused Skills for ideation, development, tool operation, coaching, monitoring, and extension creation.
- A deterministic demo, diagnostics, weekly reports, and 24 behavioral tests.

## Safety boundaries

| Action | Default |
|---|---|
| Read, search, analyze | Autonomous |
| Edit an authorized workspace | Autonomous |
| Run tests and builds | Autonomous |
| Compile an uninstalled Skill bundle | Autonomous |
| Delete material data | Human required |
| Send, publish, purchase, or make public | Human required |
| Use credentials or change system settings | Human required |
| Enable MCP or expand access | Human required |
| Unknown action | Fail closed |

EvoPilot complements Codex sandboxing, operating-system permissions, and service-side authorization; it does not replace them.

## Limits

- Workflow detection uses transparent sequence mining, not model training or semantic imitation.
- Hooks observe Codex tool events, not every gesture inside arbitrary desktop applications.
- Validation checks the bundle; it does not prove every workflow succeeds in every environment.
- EvoPilot does not generate or enable credentialed MCP servers automatically.
- The deterministic policy gate cannot prove that every command is safe.

## Development

```bash
python -m unittest discover -s tests -v
python plugins/evopilot/scripts/evopilot.py doctor --plugin-root plugins/evopilot
python tools/render_demo.py
```

See [Contributing](CONTRIBUTING.md), [Roadmap](ROADMAP.md), [Security](SECURITY.md), [Support](SUPPORT.md), [Privacy](docs/privacy.md), and [Quality gates](docs/quality-gates.md).

MIT License. See [LICENSE](LICENSE).
