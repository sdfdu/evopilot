# EvoPilot launch kit

## One-line pitch

EvoPilot is a local-first Codex copilot that learns proven work habits and promotes them into safe, reusable Skills and MCP extensions.

## Show HN

### Title

Show HN: EvoPilot – a local-first Codex copilot that improves with use

### Post

I built EvoPilot because most assistants either forget how you work or hide adaptation behind an opaque memory feature.

EvoPilot records privacy-minimized workflow signals, detects repeated patterns, and promotes successful workflows into versioned Codex Skills. When a workflow genuinely needs live data or external actions, it can draft an MCP integration—but enabling new permissions stays human-approved.

The core is dependency-free Python and SQLite. It does not train model weights, store raw tool inputs/outputs, or learn permission grants from repetition. Unknown and dangerous actions fail closed.

The first release includes six Skills, local memory, Codex lifecycle hooks, a stdio MCP server, tests, export/deletion tools, and an explicit promotion/rollback model.

Repository: https://github.com/sdfdu/evopilot

I would especially appreciate feedback on workflow evaluation metrics and safe extension promotion.

## X / Bluesky

I built EvoPilot: a local-first Codex copilot that gets better at *your* work.

It learns repeated workflow patterns, promotes what works into versioned Skills, drafts MCP integrations when needed, and keeps dangerous actions human-approved.

No cloud account. No raw tool logs. MIT licensed.

https://github.com/sdfdu/evopilot

## Reddit

### Title

I built a local-first Codex agent that turns repeated work habits into Skills

### Body

EvoPilot is an experiment in making agent adaptation inspectable instead of magical. It stores structured local memories with confidence and evidence counts, observes tool categories and outcomes without retaining raw commands, and detects repeated workflows.

Stable workflows can be promoted into Codex Skills. MCP integrations are drafted only when external data or controlled actions are actually needed, and enabling new permissions requires human approval.

The v0.1 release is dependency-free Python with SQLite, six focused Skills, hooks, a stdio MCP server, tests, and JSON export/deletion tools.

I would love feedback on the promotion thresholds and on which app-specific pack should come first.

https://github.com/sdfdu/evopilot

## LinkedIn

I have released EvoPilot, an open-source, local-first adaptive copilot for Codex.

Instead of unrestricted “self-improvement,” EvoPilot uses a controlled learning loop: observe privacy-minimized workflow signals, detect repeated patterns, trial a workflow, measure outcomes, promote successful behavior into a versioned Skill, and roll back when it performs worse.

External integrations and dangerous actions remain behind human approval. The first release includes six Skills, SQLite memory, Codex hooks, an MCP server, tests, and portable exports.

Project: https://github.com/sdfdu/evopilot

## Suggested GitHub topics

`ai-agent`, `codex`, `mcp`, `model-context-protocol`, `agent-memory`, `adaptive-agent`, `developer-tools`, `productivity`, `python`, `sqlite`

