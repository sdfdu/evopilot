# How to use EvoPilot

## First run in Codex

1. Install the plugin:

```bash
codex plugin marketplace add sdfdu/evopilot
codex plugin add evopilot@evopilot
```

2. Fully restart Codex.
3. Start a new task. EvoPilot injects default guidance automatically at task start.
4. To see the product loop, paste:

```text
Run the EvoPilot 60-second workflow compiler demo.
```

The demo is simulated. It shows the full loop without writing to learned user history.

## Real work

After restart, EvoPilot is active by default in new tasks. For maximum clarity, start a fresh task with:

```text
Use EvoPilot while we work. Remember explicit non-sensitive preferences, measure repeated workflow outcomes, and show me which workflow is ready to become a portable Skill. Ask before dangerous or external actions.
```

Then work normally. EvoPilot records privacy-minimized tool categories and outcomes, not raw prompts, raw tool inputs, raw tool outputs, or secrets.

## Useful commands

```bash
python3 plugins/evopilot/scripts/evopilot.py quickstart
python3 plugins/evopilot/scripts/evopilot.py doctor
python3 plugins/evopilot/scripts/evopilot.py context
python3 plugins/evopilot/scripts/evopilot.py sequences
python3 plugins/evopilot/scripts/evopilot.py workflows
python3 plugins/evopilot/scripts/evopilot.py report --days 7
```

## Compile a workflow

When `sequences` or `report` shows a `draft_ready` or `stable` workflow:

```bash
python3 plugins/evopilot/scripts/evopilot.py compile-skill <fingerprint> ./drafts
python3 plugins/evopilot/scripts/evopilot.py validate-skill ./drafts/<skill-name>
```

Review `SKILL.md`, `evopilot.json`, and `WHAT_HAPPENED.md` before installing or sharing the bundle.

## Promote a behavior policy

Behavior Cloning Lite stores structured episodes and promotes only short policy cards, so full history does not enter prompts.

```bash
python3 plugins/evopilot/scripts/evopilot.py observe-episode --task-type repo_onboarding --step inspect --step apply_patch --step test --outcome success
python3 plugins/evopilot/scripts/evopilot.py workflows --task-type repo_onboarding
python3 plugins/evopilot/scripts/evopilot.py promote-policy <fingerprint>
python3 plugins/evopilot/scripts/evopilot.py runtime-context --task-type repo_onboarding --token-budget 250
```

Use `retire-policy <fingerprint>` when a policy should stop being returned.

## Reset memory

Forget one memory:

```bash
python3 plugins/evopilot/scripts/evopilot.py forget <key>
```

Forget all stored memories while retaining deletion audit events:

```bash
python3 plugins/evopilot/scripts/evopilot.py forget --all
```
