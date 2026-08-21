# Cross-platform Skill Runtime Lab

Public compatibility lab for a deterministic Candidate Core Package and a small
short-essay product. The lab proves install, operate, diagnose, and accept
behavior for Skill-backed local applications on Linux x86_64, Windows x64, and
Apple Silicon macOS.

This repository is **public-source**, not an open-source grant. There is no
software license. Copyright is reserved. Third-party dependency licenses and
notices still apply.

Hosted CI, Real Lab Canary, Desktop E2E, and recording are separate proof lanes.
A green result in one lane does not imply that a later lane has passed.

## Control surface

```text
productctl --json acceptance core --contract products/short-essay/productctl.contract.json
```

A confirmed Product Contract is the adapter authority. Invalid or incomplete
contracts fail before installation, process launch, or filesystem mutation.

## Status

Implementation is in progress against the published GitHub issues. The bounded
completion claim is a proven candidate method, not a universal framework.
