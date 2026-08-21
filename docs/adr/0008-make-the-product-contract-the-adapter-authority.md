---
status: accepted
---

# Make the Product Contract the adapter authority

Store each confirmed Product Contract as a versioned `productctl.contract.json` validated by a repository-owned JSON Schema. The contract declares product identity, entrypoint, supported platforms and Python versions, runtime discovery, install payload, service and health behavior, data roots, Codex executable resolution, workflow stages and concurrency, artifacts, mutation ownership, cleanup, secrets boundaries, and acceptance requirements. Repository inspection may populate a draft, but generation stops until a human confirms all safety and success semantics; those fields are never guessed from source layout or documentation.
