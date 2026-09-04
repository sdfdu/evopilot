# Skill quality gates

EvoPilot separates structural validity from semantic quality. A bundle can have valid files and evidence while still being too generic, repetitive, or underspecified to install safely.

## Two independent results

- `validate-skill` checks bundle structure, evidence arithmetic, promotion thresholds, safety text, review state, and portability.
- `assess-skill` checks usefulness, activation boundaries, decision rules, validation guidance, stop conditions, action diversity, repetition, and observed outcomes.

The quality result contains:

- `score`: deterministic score from 0 to 100.
- `level`: `high`, `acceptable`, `needs_revision`, or `blocked`.
- `installable`: whether the bundle passes the semantic quality gate.
- `annotations`: severity-coded findings with stable codes and actionable messages.

## Annotation severities

| Severity | Meaning |
|---|---|
| `info` | Evidence limitation or useful review context. |
| `warning` | The Skill can be improved and may lose quality points. |
| `error` | The Skill cannot be installed until the issue is resolved. |

Examples include `generic-tool-sequence`, `repeated-adjacent-step`, `weak-discovery-description`, `missing-decision-rules`, and `low-success-rate`.

## Generated artifacts

Every newly compiled bundle contains:

- `SKILL.md`: workflow instructions with activation boundaries and decision guidance.
- `evopilot.json`: provenance, evidence, review state, and machine-readable quality annotations.
- `QUALITY_REPORT.md`: the human-readable score and annotation report.
- `WHAT_HAPPENED.md`: a concise explanation and review checklist.

After editing a bundle, refresh its annotations:

```bash
python plugins/evopilot/scripts/evopilot.py annotate-skill ./drafts/<skill-name>
```

Installation preparation refreshes annotations automatically. Approval is issued only when both structural validation and semantic quality pass.

## Anti-sprawl rule

High frequency alone does not make a useful Skill. Pure tool sequences such as `edit -> shell` remain workflow evidence and are excluded from automatic promotion. A promotion candidate needs a task-specific action such as testing, building, or repository inspection, and duplicate adjacent steps are filtered out.

These checks are deterministic. They do not prove domain correctness, real-world utility, or compatibility with every agent client, so human review remains part of installation.
