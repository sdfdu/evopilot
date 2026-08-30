<div align="center">

# EvoPilot

### The workflow compiler for AI agents.

Turn repeated work into evidence-backed, portable Agent Skills.

</div>

![EvoPilot workflow compiler demo](docs/demo.gif)

EvoPilot watches privacy-minimized outcomes, detects workflows that repeatedly succeed, and compiles them into reviewable [Open Agent Skills](https://agentskills.io/) bundles. It gives your agent a way to improve from real work without silently changing permissions or model weights.

> EvoPilot learns workflows, not personalities. Explicit user instructions always win, and generated Skills are never installed automatically.

## See it in 60 seconds

Requirements: Python 3.10+.

```bash
git clone https://github.com/sdfdu/evopilot.git
cd evopilot
python plugins/evopilot/scripts/evopilot.py doctor
python plugins/evopilot/scripts/evopilot.py demo --destination ./evopilot-demo
```

The demo is clearly marked as simulated and never enters your learned history. It creates:

```text
evopilot-demo/
└── workspace-inspect-workspace-apply-patch-terminal/
    ├── SKILL.md       # portable workflow instructions
    └── evopilot.json  # provenance, evidence, status, and review state
```

Open those two files to see the whole product loop: observe outcomes, detect repetition, compile a portable Skill, and require human review before installation.

Then validate any compiled bundle before reviewing it:

```bash
python plugins/evopilot/scripts/evopilot.py validate-skill ./evopilot-demo/workspace-inspect-workspace-apply-patch-terminal
```

The demo receives `demo_only` even when structurally valid, so simulated evidence can never be mistaken for a production-ready workflow.

## Why it is useful

AI agents are powerful, but most improvements remain trapped in chat history or one-off prompts. EvoPilot turns repeated success into a reusable artifact:

```text
work normally → measure outcomes → find repeated success → compile Skill → review → install
```

- **Faster recurring work:** package the inspect-edit-test or research-draft-review sequence you already use.
- **More consistent agents:** keep a proven workflow as a versioned file instead of hoping the next conversation remembers it.
- **Portable learning:** the compiled bundle follows the Open Agent Skills format rather than a private prompt database.
- **Auditable evolution:** every bundle includes the evidence that qualified it for compilation.
- **Controlled autonomy:** local, recoverable work can proceed; dangerous or externally consequential actions require a person.

## Install in Codex

```bash
codex plugin marketplace add sdfdu/evopilot
codex plugin add evopilot@evopilot
```

Fully restart Codex and start a new task so its Skills, hooks, and MCP tools load from the installed version. Then ask:

```text
Run the EvoPilot 60-second workflow compiler demo.
```

Or initialize it for real work:

```text
Use EvoPilot while we work. Remember explicit non-sensitive preferences, measure repeated workflow outcomes, and show me which workflow is ready to become a portable Skill. Ask before dangerous or external actions.
```

## What ships today

- Local SQLite memory with explicit/inferred sources, conflicts, corrections, history, and confidence decay.
- Privacy-minimized Codex hooks that store tool categories, outcomes, and a one-way workspace hash—not raw paths, arguments, or responses.
- Transparent two-to-six-step workflow detection with evidence and success thresholds.
- Portable Skill compilation with `SKILL.md` plus machine-readable `evopilot.json` provenance.
- A deterministic demo that cannot contaminate real learning data.
- `doctor` diagnostics for Python, plugin files, and database health.
- Weekly evidence reports covering outcomes, failures, corrections, conflicts, and promotion candidates.
- Deterministic bundle validation with a 0–100 quality score and explicit limitations.
- A dependency-free MCP server exposing 17 memory, learning, compilation, validation, diagnostics, export, and approval tools.
- Six focused Skills for ideation, development, tool operation, coaching, monitoring, and extension creation.

## Evidence thresholds

EvoPilot does not promote a sequence after one lucky run.

| State | Requirement |
|---|---|
| Candidate | At least 3 observations |
| Draft ready | At least 5 observations and 3 successful outcomes |
| Stable | At least 8 observations and 3 successful outcomes |

Compilation is allowed only for `draft_ready` or `stable` workflows. The result remains uninstalled with `pending_human_review` recorded in its evidence file.

Before recommending review, the validator checks required files, frontmatter, directory naming, provenance, workflow shape, evidence arithmetic, promotion thresholds, safety boundaries, review state, and portable format. This is structural validation: it does not execute the workflow or claim compatibility with every agent client.

## Safety model

| Action | Default |
|---|---|
| Read, search, analyze | Autonomous |
| Edit an authorized workspace | Autonomous |
| Run tests and builds | Autonomous |
| Compile an uninstalled Skill bundle | Autonomous |
| Delete material data | Human required |
| Send, publish, purchase, or make public | Human required |
| Use credentials or change system settings | Human required |
| Enable a new MCP or expand access | Human required |
| Unknown action | Fail closed; human required |

For risky Bash or MCP actions, EvoPilot blocks execution and returns an exact approval ID. After the user confirms that exact action, `evopilot_authorize_once` grants a ten-minute, single-use authorization bound to the complete tool call. Changed arguments require a new approval.

EvoPilot complements—not replaces—Codex sandboxing, filesystem boundaries, network policy, and native approvals.

## CLI

```bash
python plugins/evopilot/scripts/evopilot.py doctor
python plugins/evopilot/scripts/evopilot.py demo
python plugins/evopilot/scripts/evopilot.py context
python plugins/evopilot/scripts/evopilot.py sequences
python plugins/evopilot/scripts/evopilot.py compile-skill <fingerprint> <destination>
python plugins/evopilot/scripts/evopilot.py validate-skill <bundle-directory>
python plugins/evopilot/scripts/evopilot.py report --days 7
```

The older `draft-skill` command remains as a compatibility alias for `compile-skill`.

## Architecture

```text
Codex Skills ───── workflow guidance and routing
Codex hooks ────── privacy-minimized observations + safety gate
EvoPilot MCP ───── inspectable memory, analysis, compilation, and approvals
Local SQLite ───── memories, outcomes, candidates, and audit history
Portable bundle ── SKILL.md + evopilot.json
```

No third-party Python package is required at runtime.

## Local development

```bash
python -m unittest discover -s tests -v
python plugins/evopilot/scripts/evopilot.py doctor --plugin-root plugins/evopilot
python tools/render_demo.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [ROADMAP.md](ROADMAP.md), and [LAUNCH.md](LAUNCH.md).

## Current limits

- Workflow detection is transparent rule-based sequence mining, not model training or semantic imitation.
- Codex hooks see tool events, not every gesture inside arbitrary desktop applications.
- A compiled Skill is a proposal. A user must review, validate, and install it.
- EvoPilot does not generate or enable credentialed MCP servers automatically.
- The policy gate uses deterministic command and tool-name patterns and cannot prove that every command is safe.
- EvoPilot does not train or modify model weights.

## License

MIT — see [LICENSE](LICENSE).
