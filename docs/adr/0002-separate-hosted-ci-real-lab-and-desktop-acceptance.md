---
status: accepted
---

# Separate Hosted CI, Real Lab, and Desktop acceptance

Use three distinct gates: credential-free Hosted CI for deterministic cross-platform behavior, Real Lab Canary runs for the actual Windows and macOS runtime environments, and Desktop E2E for the final user-visible Codex flow. Hosted CI may use a contract-faithful fake Codex process but cannot claim a real Codex result; passing one gate never implies that a later gate has passed. Every real run records the requested and resolved Codex model/transport identity. Acceptance uses an explicit known configuration per platform and never silently falls back; an unavailable configuration fails or uses a documented platform override. This keeps routine Grok development independent of GUI operation without weakening final product evidence.
