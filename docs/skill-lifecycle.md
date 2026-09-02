# Skill lifecycle

EvoPilot treats a generated Skill as a reviewable proposal, not an automatic agent upgrade.

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

Only `draft_ready` and `stable` workflows can be compiled:

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

Install only after review. Discard weak, stale, overbroad, or unsafe bundles.
