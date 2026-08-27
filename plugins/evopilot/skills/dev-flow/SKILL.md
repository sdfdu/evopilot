---
name: dev-flow
description: Implement, debug, test, and improve software while adapting to the user's proven repository and tool habits. Use for coding work after the desired outcome is clear.
---

# Dev Flow

Load relevant EvoPilot context before choosing a workflow. Explicit task and repository instructions override memory.

- Inspect the smallest relevant project surface and preserve unrelated user changes.
- Make reasonable low-risk implementation decisions autonomously.
- Validate in proportion to risk: targeted checks first, broader checks when warranted.
- Use `evopilot_observe` to record the workflow category and outcome, not raw source, secrets, or terminal output.
- Record a preference only when explicit or supported by repeated evidence.
- On repeated failures, try safe alternatives with a bounded stopping condition; then report the actual blocker.
- Before external publication, destructive operations, credential use, or system-wide changes, call `evopilot_review_action` and require a person when directed.

Finish with the outcome, verification, and one evidence-based learning note when something durable was learned.
