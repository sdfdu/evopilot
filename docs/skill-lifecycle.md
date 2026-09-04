# Skill lifecycle

EvoPilot automatically announces promotion-ready workflows. Generation and validation can proceed locally, while installation remains an exact, one-time confirmed action.

## 1. Observe

Hooks and MCP tools record privacy-minimized outcomes from normal work.

## 2. Detect

Repeated actions become habit candidates. Repeated multi-step work becomes workflow candidates.

| State | Requirement |
|---|---|
| Candidate | At least 3 observations |
| Draft ready | At least 5 observations and 3 successful outcomes |
| Stable | At least 8 observations and 3 successful outcomes |

## 3. Compile

At task startup, EvoPilot tells the agent when the strongest learned workflow reaches `draft_ready` or `stable`. The agent explains the evidence before compiling:

```bash
python plugins/evopilot/scripts/evopilot.py compile-skill <fingerprint> ./drafts
```

The output bundle contains:

- `SKILL.md`
- `evopilot.json`
- `WHAT_HAPPENED.md`

## 4. Validate

```bash
python plugins/evopilot/scripts/evopilot.py validate-skill ./drafts/<skill-name>
```

Validation checks structure, evidence arithmetic, promotion thresholds, safety boundaries, human review state, and portable format. It does not execute the workflow.

## 5. Review

A person should confirm:

- The workflow matches work that should be repeated.
- Explicit user instructions remain higher priority than learned behavior.
- Dangerous or external actions still require approval.
- The evidence is real and sufficient.

## 6. Install or discard

Prepare the exact installation after review:

```bash
python plugins/evopilot/scripts/evopilot.py prepare-skill-install ./drafts/<skill-name>
```

The result contains an approval ID bound to the reviewed bundle contents and destination. After the user explicitly confirms that exact installation, authorize the ID and install:

```bash
python plugins/evopilot/scripts/evopilot.py approve <approval-id>
python plugins/evopilot/scripts/evopilot.py install-skill ./drafts/<skill-name> <approval-id>
```

The approval expires after ten minutes, works once, and becomes invalid if the bundle changes. Discard weak, stale, overbroad, or unsafe bundles.
