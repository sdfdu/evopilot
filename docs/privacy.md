# Privacy model

EvoPilot is local-first. Its default job is to learn workflow shape and outcome evidence, not personal identity, secrets, or private content.

## What EvoPilot stores

- Tool family and normalized action category.
- Outcome: `unknown`, `success`, `failure`, or `abandoned`.
- Session id when available.
- Optional duration.
- One-way workspace hash when hooks receive a working directory.
- Non-sensitive memories that are explicit or evidence-backed.

## What EvoPilot avoids storing

- Raw prompts.
- Raw tool inputs.
- Raw tool outputs.
- Raw file paths.
- API keys, access tokens, cookies, passwords, private keys, and authorization headers.

Sensitive-looking keys or values are rejected or redacted before storage.

## Human control

Generated Skills are never installed automatically. Publish, delete, credential, permission, system-setting, payment, and unknown actions require human approval at the execution boundary.

Use:

```bash
python plugins/evopilot/scripts/evopilot.py export ./evopilot-export.json
python plugins/evopilot/scripts/evopilot.py forget --all
```

Exports exclude active one-time approvals.
