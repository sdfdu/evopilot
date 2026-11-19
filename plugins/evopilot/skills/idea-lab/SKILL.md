---
name: idea-lab
description: Develop vague ideas into decisions through focused options and discussion, then create the artifact only after the user says to generate, build, or otherwise proceed.
---

# Idea Lab

Turn an undeveloped idea into a buildable definition without prematurely producing the wrong artifact.

1. Restate the intended outcome in one sentence and surface only material ambiguities.
2. Offer concise, mutually exclusive choices with a recommended default. Let the user answer with short codes.
3. Keep a visible decision record: confirmed, assumed, and unresolved.
4. Challenge conflicts and scope creep with concrete consequences.
5. Do not create project files or external state while the user is still discussing the design.
6. When the user asks for options and also says to start, present the options, recommendation, and tradeoffs before editing. Then proceed with reversible work that serves every option. Defer option-specific changes until the user chooses.
7. When the user chooses an option after authorizing work, hand the confirmed goal, option, constraints, and acceptance criteria to the relevant execution skill. Continue through verification without asking the user to confirm the same choice again. Apply the same handoff when the user explicitly asks to build an already defined outcome.

After a successful task, record durable interaction preferences with `evopilot_remember`. Treat a single correction as task evidence, not automatically as a universal preference.
