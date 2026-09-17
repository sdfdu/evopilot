# Behavior Cloning Lite

EvoPilot's Behavior Cloning Lite learns workflow policy from successful work without replaying full history into prompts.

It is not model-weight training. It stores structured, privacy-minimized episodes, promotes only stable low-risk fingerprints, and returns short policy cards at runtime.

## Flow

```text
episode -> fingerprint -> score -> promote -> token-capped runtime context
```

An episode records:

- task type;
- ordered workflow steps;
- outcome;
- validation steps;
- short decision-point labels;
- risk level.

It does not store raw terminal output, raw prompts, raw tool inputs, raw diffs, credentials, or private page content.

## Promotion thresholds

A policy can be promoted only when it has:

- at least 5 observations;
- at least 3 successful outcomes;
- at least 75% success rate;
- no correction episodes;
- non-high risk.

Promotion is reviewed and reversible. Retired policies are not returned in runtime context.

## Runtime context

Runtime retrieval returns only promoted policy cards for the requested task type:

```bash
python3 plugins/evopilot/scripts/evopilot.py runtime-context --task-type repo_onboarding --token-budget 250
```

The response is deterministic and token-capped. Full episodes stay in SQLite and are not injected into the prompt.

## CLI example

```bash
python3 plugins/evopilot/scripts/evopilot.py observe-episode \
  --task-type repo_onboarding \
  --step inspect \
  --step apply_patch \
  --step test \
  --step doctor \
  --validation-step "syntax check" \
  --validation-step "unit tests" \
  --validation-step doctor \
  --outcome success

python3 plugins/evopilot/scripts/evopilot.py workflows --task-type repo_onboarding
python3 plugins/evopilot/scripts/evopilot.py promote-policy <fingerprint>
python3 plugins/evopilot/scripts/evopilot.py runtime-context --task-type repo_onboarding
```

Use `retire-policy <fingerprint>` when a policy stops matching how work should be done.
