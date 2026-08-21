---
status: accepted
---

# Generate adapters, not Core implementations

After both lab products prove the shared boundaries, build an Adapter Scaffolding Skill that first derives a Product Contract draft for explicit confirmation, then produces only a Product Adapter skeleton, conformance tests, Hosted CI workflow, and thin product Skill. It references the versioned Candidate Core Package and never regenerates process, locking, runtime, installation transaction, ownership, receipt, or cleanup atoms. Validate the Skill by generating an adapter from a third, deliberately small dummy Product Contract in a temporary directory and running schema, static, and conformance checks; this does not create a third product repository. Copier remains conditional on repeated structural changes across both projects rather than becoming the initial generator.
