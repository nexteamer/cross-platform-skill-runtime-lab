# Cross-platform control delivery plan

Status: plan confirmed on 2026-08-21. Implementation has not started and requires a separate user instruction to begin.

## Outcome and bounded claim

Deliver a proven candidate method for installing, operating, diagnosing, and accepting user-space, Skill-backed local applications on Linux x86_64, Windows x64, and Apple Silicon macOS. The method consists of a deterministic Candidate Core Package, product-owned adapters, a thin product Skill, and a later Adapter Scaffolding Skill. It is not yet a universal application framework.

## Repository sequence

1. Create `cross-platform-skill-runtime-lab` as a new Public-Source Lab Repository from this directory. It contains the Candidate Core Package and a deliberately small short-essay Flask product.
2. Do not create the second remote until Phase 1 passes. Then export exact Public Image revision `931d4245` through the reviewed allowlist into a new-history `public-image-ppt-3-0-compatibility-lab` Public-Source Lab Repository.
3. Do not modify either original product repository. Do not copy its `AGENTS.md`, prior GitHub workflows, protected prompts, operational evidence, generated artifacts, or local state.
4. Both public repositories initially have no software license. Third-party dependency license and notice duties still apply.

## Product Contract and control surface

Each product owns a confirmed, schema-validated `productctl.contract.json`. The contract supplies the product-specific values consumed by one `productctl` CLI whose atomic commands are:

- `runtime discover`
- `payload verify`
- `process probe`
- `install`
- `service preflight|start|stop|status`
- `lease status|release`
- `doctor`
- `network probe`
- `codex resolve|probe`
- `workflow run short-essay` (and the phase-specific Public Image workflow)
- `artifacts inventory|verify`
- `diagnostics collect`
- `cleanup exact`
- `acceptance core`

Every command supports `--json`, stable exit categories, the shared Control Envelope, evidence references, and mutation ownership. VM/checkpoint/SSH/capacity stays in the existing Lab layer; Desktop UI operation and recording stay in their own later proof layers.

## Phase 1 product behavior

The short-essay product exposes a minimal Flask API and server-rendered page. One run performs sequential analysis, starts two polish candidates concurrently, then performs sequential synthesis. Test fixtures cover zero through four concurrent branches, timeouts, cancellation, and partial failure. If one candidate fails, the run becomes `partial_success` and synthesis uses the survivor while preserving failure evidence; if both fail, the run fails. The control layer never silently retries Codex.

SQLite stores run, stage, and structured error state. Files store the Run Artifact Set: input snapshot, analysis JSON, candidate Markdown outputs, final Markdown, manifest, and control receipts. A partial-success set retains the failed candidate's sanitized evidence but never publishes raw sensitive Codex internals.

The Phase 1 installer assumes Python 3.11 or 3.12 is present, then proves interpreter discovery, pinned wheel/virtual-environment installation, staging, promotion, rollback, and a final smoke test. It does not promise a bundled Python runtime or complete wheelhouse. The service binds `127.0.0.1` on a dynamically allocated port recorded in its receipt.

## Phase 2 product behavior

The sanitized Public Image export keeps the actual backend, Flask surface, database, packaging, CLI, required UI/static assets, and relevant tests. A machine-readable export manifest records the source commit, allowlist, denylist, and per-file hashes; any unclassified file, secret scan result, prompt scan result, or failed manual readback blocks creation of the public remote.

Protected business prompts are absent. Synthetic Prompt Fixtures preserve only the required slots, role boundaries, and parseable result shapes: content becomes minimal XML, then one simple image is generated. The service retains port `3130` but must prove ownership before use. The repository consumes an immutable Candidate Core tag/commit plus checksum rather than copying Core code.

## Hosted CI and GitHub Actions

The fast workflow runs on pull requests and pushes across Ubuntu 24.04, Windows Server 2022, and macOS 15 arm64 with Python 3.11 and 3.12. It uses a contract-faithful fake Codex executable/JSONL stream and no account secrets, real login, or GUI. A manually dispatched full workflow runs the extended concurrency, packaging, rollback, and historical failure suites.

Successful jobs publish a compact job summary and small receipt. Failed jobs retain a sanitized diagnostic bundle for seven days. Release artifacts are GitHub Release wheels, manifests, checksums, dependency inventories, and third-party notices. Caches remain below 10 GB. Once stable, branch protection requires the fast checks and blocks force pushes; human review is not mandatory for this personal lab.

Passing Hosted CI does not imply Real Lab Canary or Desktop E2E success.

All workflows use least privilege. Ordinary jobs default to `contents: read`; pull-request jobs receive no product secrets; referenced third-party Actions are pinned to full commit SHAs. Release publication is isolated in a tag/manual workflow with only its required write permission. Fast runs cancel superseded executions, every job has a bounded timeout, the expensive matrix has no schedule, and failures retain only the planned seven-day sanitized bundle.

## Codex, network, and offline boundary

Every Real Lab or Desktop run records both requested and resolved Codex model/transport identity. Acceptance uses an explicit configuration per platform. An unavailable configuration produces a visible failure or a documented platform-specific override; no layer silently switches models or transports.

Hosted CI has no credentials and uses fake Codex streams. Real Labs may reach the Codex and GitHub endpoints required by their declared stages. Each install receipt distinguishes network-required, network-optional, and offline stages. Phase 1 does not promise a fully offline install. Phase 2 retains the Public Image offline payload-install boundary, while real Codex inference remains an online operation.

## Secrets and public evidence

Contracts, receipts, diagnostic bundles, CI logs, and public artifacts never contain token values, authentication files, protected prompts, or sensitive environment values. They may record a required variable's name, presence, source category, and a non-reversible hash only where necessary. Redaction fixtures and secret/prompt scans are release gates. Full Real Lab evidence remains local by default; publication requires a separate sanitized readback.

## Real Lab state policy

An ordinary product failure preserves the installed state and independent evidence root for diagnosis, repair, and retest. Rollback is reserved for contamination, invalid state, unclear causality, explicit clean-install proof, or milestone completion. Each Windows and macOS completion gate restores the exact recorded baseline once, re-verifies machine identity and readiness, repeats acceptance, and then performs exact owned cleanup.

## Third-party component policy

Adoption follows `open-source-component-evaluation.md`. Flask and pytest are baselines; `uv` is used for development and Hosted CI but is not a target-machine prerequisite. Phase 1 evaluates `platformdirs`, then at most one of `portalocker`/`filelock`, then `psutil`. Each candidate must pass the same three-platform/two-Python matrix, mapped historical failures, packaging and cleanup contracts, and license/security gates. Failure keeps or restores the proven atom behind the same interface.

Copier, PyApp, Velopack, Tauri, and `pluggy` do not enter the current implementation merely because prior research identified them. Their evaluation begins only at the documented trigger.

## Evidence and cleanup

Every run has an independent evidence root. Diagnosis does not automatically delete a failed installation or run. After successful acceptance, archive a compact receipt and execute `cleanup exact --run-id` against only the resources owned by that run. Public CI artifacts contain sanitized fixtures and summaries, not credentials or protected prompts.

## Milestones

| Milestone | Deliverable | Exit gate |
|---|---|---|
| M0 | Product Contract schema and confirmed lab contract; Control Envelope; Conformance Suite skeleton; Historical Failure Registry | Every High/Extreme product-side historical failure maps to an owning layer, command/stage, expected structured outcome, and Hosted CI or Real Lab proof lane |
| M1 | Candidate Core and short-essay Flask Product Adapter | Local workflow, partial-success semantics, install transaction, receipts, and exact cleanup pass |
| M2 | Hosted CI and Component Spikes | Fast and manual matrices pass; every evaluated component has an adopted/rejected/deferred receipt |
| M3 | Windows and macOS Real Lab acceptance | Clean install, doctor, real Codex business E2E, diagnostics, and cleanup pass on both; restore exact baseline and repeat once |
| M4 | Sanitized Public Image source export | Export from `931d4245` passes manifest classification, hashes, secret/prompt scans, and manual review before public remote creation |
| M5 | Public Image Product Adapter and synthetic XML-to-image flow | Install, port ownership, two-stage contract, artifact verification, diagnostics, and cleanup pass locally |
| M6 | Both-product conformance and Real Lab acceptance | One immutable Candidate Core revision passes both suites and both real platforms without product-specific Core forks |
| M7 | Adapter Scaffolding Skill | A confirmed dummy Product Contract generates an ephemeral adapter that passes schema, static, and conformance checks without generating Core atoms |
| M8 | Public Image Desktop E2E | A new Codex Desktop task performs installation/runtime setup, restart, real simplified image generation, and artifact inspection on Windows and macOS; Linux CLI regression remains green |
| M9 | Recording verdict and final cleanup | Separate recording proof is complete, evidence authority is named, exact baseline restoration is proven, and remaining gaps are reported as gaps rather than inferred success |

## Historical Failure Registry shape

Store the registry at `tests/fixtures/historical_failures/index.json`. Each entry records issue identity, responsible layer, `productctl` command, stage, expected error category, affected platforms, sanitized fixture path, and required proof lane. All known High/Extreme failures owned by the product control layer require a regression fixture; Lab-, Desktop-, or recording-owned failures require an explicit external proof reference rather than a fake product test.

The planning-time reverse map is maintained in `historical-failure-command-coverage.md`. A command may not be removed or merged if doing so leaves a historical row without one deterministic entrypoint and owner.

## Candidate Core and scaffolding evolution

Candidate Core uses `0.y.z` versions and GitHub Release wheels, manifests, and SHA-256 checksums; it is not initially published to PyPI. A breaking pre-1.0 change requires an explicit migration note, a schema version bump when the contract changes, and both adapters updated and re-proven in the same milestone; prior releases remain available.

The Adapter Scaffolding Skill may inspect source to populate a Product Contract draft, but it must stop for confirmation rather than inventing success, ownership, cleanup, or secret semantics. It generates adapter boundaries, tests, workflows, and the thin Skill only. Copier is reconsidered after both real adapters exist and two common structural changes demonstrate that template replay would save work with acceptable conflicts.

## Implementation start gate

Plan confirmation does not itself mutate external systems. On a separate instruction to begin, first read back the current GitHub identity and its Public-repository and Actions permissions. Initialize and publish only the Phase 1 repository. Create the Phase 2 public remote only after the exact-revision sanitized export has passed classification, hash, secret/prompt scan, and manual readback. The source Public Image repositories remain read-only throughout.

## Terminal attempt budget

The Windows Desktop E2E, macOS Desktop E2E, Windows recording, macOS recording, and final bounded-verdict tickets permit at most five attempts for the same unresolved failure category. There is no sixth attempt. A Desktop ticket that exhausts its budget makes its dependent recording ticket `SKIPPED`; a recording ticket that exhausts its budget stops that platform branch. Terminal evidence is preserved, and the final verdict distinguishes `PASS`, `BLOCKED`, and `SKIPPED` without inferring success.
