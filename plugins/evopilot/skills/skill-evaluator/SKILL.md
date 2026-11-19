---
name: skill-evaluator
description: Evaluate an existing or proposed skill with representative prompts. Check when it activates, what actions it takes, and whether its output meets the request.
---

# Skill Evaluator

1. Select the skill and version to evaluate. Read its description and workflow, then identify overlapping skills and the task boundaries that matter to the user.
2. Build cases from sanitized examples. Include clear and ambiguous triggers, similar requests that should route elsewhere, and a follow-up that changes scope or grants authorization. For each case, define the expected selection, action boundary, and deliverable before running it.
3. When an isolated evaluation environment is available, run cases using fixtures with disposable state and simulated external effects. Otherwise perform a static walkthrough and label the cases as unexecuted. Treat an inferred skill choice as an inference unless a trace or explicit invocation confirms it.
4. Report expected versus observed behavior with pass, fail, or unverified for each case. Distinguish routing errors from execution errors and prioritize fixes by their impact. Rerun affected cases after an authorized change.
