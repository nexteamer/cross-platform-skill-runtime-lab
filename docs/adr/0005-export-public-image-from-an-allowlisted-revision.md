---
status: accepted
---

# Export Public Image from an allowlisted revision

Create the Public Image Integration Lab from an allowlisted export of exact revision `931d4245`, not from either dirty working tree and not by rewriting the original repository's history. The export receives a new Git history and preserves the runtime backend, Flask surface, database, packaging, CLI, necessary UI/static assets, and relevant tests. It excludes repository metadata, agent instructions, prior workflows, operational plans and evidence, generated artifacts, local state, and Protected Prompt Assets; Synthetic Prompt Fixtures preserve only the required contracts. A machine-readable export manifest must classify and hash every included file before any public remote is created.
