# Contributing

Thanks for helping EvoPilot become more useful without becoming less trustworthy.

## Development

1. Fork and clone the repository.
2. Create a focused branch.
3. Keep the core dependency-free unless a dependency has a clear, measured benefit.
4. Add or update behavioral tests.
5. Run `python -m unittest discover -s tests -v`.
6. Validate every changed Skill and the plugin manifest.

## Extension rules

- Add a Skill when existing tools can do the work and only workflow guidance is missing.
- Add a script for deterministic, repeatable mechanics.
- Add MCP only for live data, authentication, controlled actions, or genuinely missing tools.
- Do not collect raw private content merely to infer a habit.
- New external permissions must remain human-approved.
- Avoid universal rules based on one user's correction.

Issues should include the observed behavior, expected behavior, reproduction steps, and whether local EvoPilot data was involved. Redact personal memory before sharing logs.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Setup questions and design proposals belong in GitHub Discussions; see [Support](SUPPORT.md).
