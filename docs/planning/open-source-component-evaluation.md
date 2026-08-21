# Open-source component evaluation plan

This plan turns the prior research into bounded Component Spikes. Research popularity alone is not adoption evidence.

## Common admission gate

Every candidate must:

1. pass Linux x86_64, Windows x64, and Apple Silicon macOS tests on Python 3.11 and 3.12;
2. pass the mapped historical failure fixtures and negative ownership cases;
3. preserve structured failure categories, stage evidence, and exact cleanup;
4. install reproducibly from pinned versions and hashes, including the promised offline or prebuilt-wheel boundary;
5. reduce maintained platform code or materially improve correctness;
6. use an MIT, BSD, or Apache-2.0 license and have a maintained release/security posture;
7. be pinned to an exact version and artifact hash, with its license and required notice captured for the release inventory.

Failure of a required gate means reject or defer the component; do not hide the gap behind an application wrapper.

## Evaluation matrix

| Component | Planned status | Capability under test | Adoption evidence | Exit or deferral condition |
|---|---|---|---|---|
| `psutil` | Phase 1 spike | process identity, child trees, executable paths, listeners, memory | Correct PID-reuse/access-denied behavior and fewer platform branches on all target runners | Keep the proven platform adapter if identity or packaging evidence is weaker |
| `platformdirs` | Phase 1 spike | data, config, cache, log, and runtime roots | Matches platform conventions while preserving explicit Product Adapter overrides and child inheritance | Reject if it recreates the historical split-root behavior |
| `portalocker` / `filelock` | Phase 1 bake-off | exclusive lock primitive | One candidate passes contention, crash, permission, stale-owner, and exact-path tests without silently changing protocol | Select at most one; retain the existing lock atom if neither preserves fail-closed ownership semantics |
| `uv` | Adopt for development and Hosted CI; Phase 2 runtime spike | Python discovery, venv, locked dependency installation | Reproducible exact-interpreter installs and clearer receipts than the baseline; target machines must not be assumed to have `uv` | Do not make it the product contract or a mandatory preinstalled runtime |
| Copier | Deferred experiment | repeatable adapter/test/CI scaffolding updates | Both adapters exist and at least two common structural changes can be replayed with acceptable conflicts | Do not use it to distribute Candidate Core implementations |
| `pluggy` | Deferred | multi-adapter extension hooks | At least three products or multiple independently loaded implementations demonstrate stable extension points | A normal typed Product Adapter remains the default |
| PyApp | Triggered evaluation only | native first-run Python bootstrap and optional embedded payload | Phase 2 evidence still identifies Python bootstrap as a leading unresolved failure and PyApp improves size, offline, signing, and recovery trade-offs | Do not build a custom Rust launcher first |
| Velopack | Out of current scope | desktop installer and automatic update | Product scope changes into a conventional independently installed desktop application | It does not replace Product Contract, Codex identity, workflow, or artifact verification |
| Tauri | Not adopted | GUI shell and sidecar pattern | None for the current CLI/Skill architecture | Retain only as an architectural reference unless a real desktop GUI becomes the product |

## Baseline components

Flask is application-specific to the two labs, and pytest is the test harness. Python standard-library modules remain the baseline for subprocess argument arrays, hashing, archives, JSON, SQLite, and filesystem operations until a Component Spike demonstrates a concrete gap.

## Evaluation order

1. Freeze the Product Contract, Control Envelope, Conformance Suite, and Historical Failure Registry before comparing implementations.
2. Establish Flask, pytest, and `uv` as the application, test, and development/Hosted CI baseline; `uv` is not assumed on target machines.
3. Spike `platformdirs` first because path ownership affects every later fixture.
4. Bake off `portalocker` and `filelock`, selecting at most one only after the path contract is stable.
5. Spike `psutil` against process identity, listener ownership, permission, and PID-reuse failures.
6. In Phase 2 only, test whether `uv` materially improves target-machine runtime discovery and installation receipts.
7. Reconsider Copier only after both adapters have experienced at least two common structural changes; evaluate PyApp, Velopack, Tauri, or `pluggy` only when their recorded trigger occurs.

## Evidence produced per spike

Each spike produces a short decision receipt containing the pinned version, artifact hash and source, license and notice duties, tested platforms, mapped historical failures, conformance results, packaging impact, code removed or retained, known gaps, and `adopted`, `rejected`, or `deferred` status.
