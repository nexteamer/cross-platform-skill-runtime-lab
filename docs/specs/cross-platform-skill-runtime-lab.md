# Cross-platform Skill Runtime Lab Specification

## Problem Statement

Installing, operating, diagnosing, and accepting a Skill-backed local application currently requires an Agent to rediscover platform behavior on Windows and macOS during each project. The Agent repeatedly assembles shell commands, resolves runtimes, manages services and ports, interprets Codex executable identity, investigates network failures, verifies artifacts, and invents cleanup and evidence conventions. This consumes substantially more time and reasoning than the business workflow itself and frequently turns an ordinary product failure into a multi-round system-integration exercise.

The historical Public Image acceptance work exposed recurring failures across Python discovery, offline dependency resolution, PowerShell argument and encoding behavior, installation promotion, filesystem durability, data-root inheritance, listener ownership, Codex executable selection, provider transport, Desktop sandboxing, workflow timeouts, artifact identity, recording, and exact cleanup. These failures do not all belong to the same layer, but the absence of deterministic interfaces made their ownership and proof boundaries unclear.

A Public Image-specific controller would reduce immediate pain but would require each later project to rebuild the same platform atoms. A universal framework or free-form generator would overgeneralize before common behavior has been proven. The required solution must therefore solve the immediate Public Image compatibility problem while producing reusable evidence about what is genuinely product-neutral.

The development model must also let a Coding Agent such as Grok perform routine repository engineering without depending on strong GUI operation. Hosted CI must remain credential-free and economical on public GitHub runners, while real Windows, macOS, and Codex Desktop evidence remains a separate and truthful acceptance obligation.

## Solution

Build a two-phase Compatibility Lab program around one deterministic `productctl` interface. Phase 1 creates a new Public-Source Lab Repository containing a deliberately small short-essay Flask product, a product-owned Product Adapter, and a pre-1.0 Candidate Core Package. The short-essay workflow proves a sequential analysis stage, two concurrent polish candidates, sequential synthesis, durable run state, artifacts, installation, service ownership, diagnostics, and exact cleanup without importing Public Image business complexity.

Every product declares a confirmed, schema-validated Product Contract. The Product Contract is the authority for product identity, lifecycle, supported platforms, runtime and payload behavior, service and health behavior, workflow stages, artifacts, mutation ownership, secrets, cleanup, and acceptance. The Candidate Core provides product-neutral control atoms, while the Product Adapter supplies product-specific values and behavior. Every command returns the same versioned Control Envelope.

The single highest-level test seam is the confirmed Product Contract entering `productctl acceptance core` and producing a Control Envelope plus a Run Artifact Set. Hosted CI, Real Lab Canary, and final Desktop E2E proof exercise this same contract at progressively more realistic environments. Atomic command fixtures remain available to diagnose historical failures, but they do not create competing top-level acceptance definitions.

After Phase 1 passes Hosted CI and repeated Windows/macOS Real Lab acceptance, Phase 2 creates a second Public-Source Lab Repository from a sanitized, allowlisted export of one immutable Public Image revision. Protected Prompt Assets are excluded and replaced by Synthetic Prompt Fixtures that preserve only the required two-stage content-to-minimal-XML-to-simple-image contract. The second product consumes an immutable Candidate Core release and proves whether the proposed shared boundary survives a real integration.

Only after both products pass the shared Conformance Suite will an Adapter Scaffolding Skill be built. It may inspect a repository and propose a Product Contract draft, but it generates only the Product Adapter skeleton, conformance tests, Hosted CI workflow, and thin product Skill after the contract is explicitly confirmed. It never regenerates Candidate Core atoms.

## User Stories

1. As a product owner, I want one deterministic control interface for a Skill-backed local product, so that platform acceptance does not depend on an Agent inventing commands during every run.
2. As a product owner, I want the first implementation proven on a deliberately small product, so that business complexity does not hide control-layer defects.
3. As a product owner, I want the method validated against Public Image only after Phase 1 passes, so that the second project tests reuse instead of shaping an unproven abstraction.
4. As a product owner, I want both phases developed in new Public-Source Lab Repositories, so that public GitHub-hosted runners can be used without mutating the original products.
5. As a product owner, I want the repositories to remain unlicensed initially, so that source visibility is not mistaken for an open-source grant.
6. As a product owner, I want a bounded final claim, so that successful delivery is described as a proven candidate method rather than a universal framework.
7. As a Coding Agent, I want a confirmed Product Contract, so that I do not guess success, ownership, cleanup, or secret semantics from repository layout.
8. As a Coding Agent, I want one versioned Control Envelope, so that I can interpret every command without learning platform-specific JSON shapes.
9. As a Coding Agent, I want stable exit categories separated from stdout and stderr, so that native diagnostic output is not mistaken for process failure.
10. As a Coding Agent, I want every result to identify its run and stage tree, so that I can stop at the first failed stage instead of launching an exploratory shell session.
11. As a Coding Agent, I want evidence paths and observations in each stage result, so that repairs are grounded in retained facts.
12. As a Coding Agent, I want mutation ownership recorded before cleanup, so that I never stop or delete resources based on a guessed name or path prefix.
13. As a Coding Agent, I want a single acceptance command, so that the same external behavior can be exercised in CI, Real Labs, and Desktop validation.
14. As a Coding Agent, I want atomic diagnostic commands beneath that seam, so that a failed acceptance can be localized without redefining success.
15. As a Coding Agent, I want product-critical subprocesses launched with explicit executable paths and argument arrays, so that shell quoting and native argument rewriting are removed from the product path.
16. As a Coding Agent, I want a Product Contract schema, so that invalid or incomplete adapters fail before installation or mutation.
17. As a Coding Agent, I want a Historical Failure Registry, so that every known High or Extreme product-side incident remains tied to a regression fixture.
18. As a Coding Agent, I want externally owned failures mapped to their real Lab, Desktop, recording, or publication proof lane, so that fake product tests do not imply coverage.
19. As a Windows operator, I want runtime discovery to test required capabilities rather than assume base `pip`, so that a usable Python installation is not rejected.
20. As a Windows operator, I want payload verification to evaluate the actual target Python and platform markers, so that missing CP311, CP312, or Windows-only wheels block release before installation.
21. As a Windows operator, I want installation to use staging, promotion, rollback, and a final-path smoke test, so that a promoted environment never retains a launcher pointing at deleted staging files.
22. As a Windows operator, I want JSON receipts written in a consistent encoding, so that PowerShell BOM behavior cannot invalidate otherwise correct evidence.
23. As a Windows operator, I want fixed read-only platform probes where PowerShell is unavoidable, so that product-critical logic is not rewritten as temporary scripts.
24. As a Windows operator, I want listener ownership proved before port use, so that an old service cannot be misreported as the new installation.
25. As a Windows operator, I want Codex executable resolution to report all candidates and the selection reason, so that AppX resources and managed-cache generations are not conflated.
26. As a Windows operator, I want Publisher identity normalized semantically, so that harmless formatting differences do not reject a valid signed executable.
27. As a Windows operator, I want process identity to remain safe under PID reuse and access-denied conditions, so that ownership never fails open.
28. As a macOS operator, I want installed dispatchers checked for executable permission, so that an invalid payload fails before a Desktop task reaches it.
29. As a macOS operator, I want service preflight to select a lifecycle supported by the Desktop sandbox, so that launchd registration is not assumed where command-held execution is required.
30. As a macOS operator, I want lease failures to preserve permission, stale-owner, and busy distinctions, so that a directory permission error is not reported as an active runtime.
31. As a macOS operator, I want provider transport probes to record the resolved model, transport, redacted child environment, and timeout stage, so that competing proxy hypotheses can be falsified.
32. As a macOS operator, I want workflow deadlines, cancellation, service lifetime, and terminal database state to share one transaction, so that a timeout cannot leave a run permanently marked as running.
33. As a Linux maintainer, I want Linux x86_64 regression coverage, so that Windows and macOS changes do not break the existing command-line path.
34. As a product user, I want to submit short text through a minimal Flask page or API, so that the Phase 1 control flow can be demonstrated without special tooling.
35. As a product user, I want analysis to finish before polish begins, so that the workflow respects the intended dependency order.
36. As a product user, I want two polish candidates to execute concurrently, so that the lab exercises real parallel process and state behavior.
37. As a product user, I want synthesis to start only after the candidate stage reaches a terminal state, so that the final result has a deterministic input set.
38. As a product user, I want one surviving polish candidate to produce a `partial_success` result, so that useful work is retained without hiding the failed branch.
39. As a product user, I want both failed candidates to fail the run, so that synthesis never fabricates success without a valid input.
40. As a product user, I want the control layer to avoid silent Codex retries, so that cost, latency, and failure evidence remain explicit.
41. As a product user, I want input, analysis, candidate, synthesis, manifest, and receipt artifacts inventoried together, so that I can understand exactly what one run produced.
42. As a product user, I want duplicate human-readable titles to retain unique artifact names, so that outputs cannot overwrite each other.
43. As a product user, I want artifact hashes and a manifest, so that later inspection can distinguish missing, changed, or moved results.
44. As an operator, I want the Phase 1 service bound to loopback on a recorded dynamic port, so that concurrent or stale runs do not contend for a fixed public listener.
45. As an operator, I want the Public Image service to retain port 3130 with ownership preflight, so that compatibility is preserved without accepting a foreign listener.
46. As an operator, I want `doctor` to validate the exact installation, data root, service, database, Codex resolution, and artifact root, so that a generic environment check cannot produce a false PASS.
47. As an operator, I want `network probe` to distinguish route, DNS, proxy, TLS, certificate-revocation, and target-HTTP stages, so that a reachable listener is not mistaken for usable connectivity.
48. As an operator, I want `diagnostics collect` to create one sanitized evidence bundle, so that a failed run does not require many follow-up probes.
49. As an operator, I want failed installation and run state retained by default, so that diagnosis and retest occur against the evidence-bearing environment.
50. As an operator, I want exact cleanup scoped to a run identifier, so that cleanup never damages unrelated processes, tasks, or data.
51. As a Lab operator, I want VM identity, checkpoints, vTPM, SSH, network, and capacity to remain in the existing Lab layer, so that `productctl` does not become a VM-management framework.
52. As a Lab operator, I want the exact platform baseline restored once at milestone completion and the acceptance repeated, so that repeatability is proven without destroying ordinary failure evidence too early.
53. As a Desktop acceptance reviewer, I want the final flow initiated through a new Codex Desktop task, so that shell or CLI evidence is not mislabeled as Desktop E2E.
54. As a Desktop acceptance reviewer, I want runtime setup, restart usability, real generation, and artifact inspection included, so that installation alone cannot satisfy compatibility.
55. As a recording reviewer, I want product and recording verdicts reported independently, so that a broken recording backend cannot turn a successful product run into a product failure or vice versa.
56. As a security reviewer, I want public CI to run without real Codex credentials or protected prompts, so that pull-request execution cannot expose private assets.
57. As a security reviewer, I want secrets represented only by safe metadata when necessary, so that logs and receipts never publish authentication values.
58. As a security reviewer, I want redaction, secret scanning, and protected-prompt scanning to block publication, so that a sanitized repository is proven rather than assumed.
59. As a security reviewer, I want third-party Actions pinned to full commit identities and ordinary jobs limited to read permission, so that the public CI trust surface is bounded.
60. As a GitHub maintainer, I want fast pull-request and push checks separated from a manually dispatched full matrix, so that routine feedback remains economical.
61. As a GitHub maintainer, I want superseded runs cancelled, jobs timed out, expensive matrices unscheduled, and diagnostic retention bounded, so that public-runner and storage use remain controlled.
62. As a release maintainer, I want Candidate Core released with a pre-1.0 version, immutable package identity, manifest, and SHA-256 checksum, so that the second product consumes a reproducible implementation.
63. As a release maintainer, I want exact dependency versions, artifact hashes, license inventory, and required notices, so that reproducibility does not ignore third-party obligations.
64. As a release maintainer, I want breaking pre-1.0 changes accompanied by migration notes and schema versioning, so that both adapters can evolve deliberately.
65. As a component evaluator, I want each third-party candidate tested against the Conformance Suite and Historical Failure Registry, so that popularity is not treated as adoption evidence.
66. As a component evaluator, I want `platformdirs` evaluated against explicit path overrides and child inheritance, so that platform conventions do not recreate split data roots.
67. As a component evaluator, I want `portalocker` and `filelock` compared against contention, crash, permission, stale-owner, and exact-path behavior, so that at most one safe lock primitive is selected.
68. As a component evaluator, I want `psutil` evaluated against process identity, listener ownership, PID reuse, and access denial, so that fewer platform branches do not weaken safety.
69. As a component evaluator, I want `uv` used for development and Hosted CI without assuming it is installed on target machines, so that workflow speed is separated from the product contract.
70. As a component evaluator, I want failed spikes recorded as rejected or deferred while retaining the proven atom, so that a wrapper cannot conceal weaker behavior.
71. As a Public Image maintainer, I want Phase 2 exported from one immutable approved revision, so that dirty working-tree changes cannot leak into the public integration lab.
72. As a Public Image maintainer, I want every source file classified and hashed before the second public remote is created, so that the export boundary is reviewable.
73. As a Public Image maintainer, I want Protected Prompt Assets excluded entirely, so that business methodology is not exposed through a public compatibility exercise.
74. As a Public Image maintainer, I want Synthetic Prompt Fixtures to preserve required slots and parseable output shapes, so that the two-stage integration remains technically representative.
75. As a Public Image maintainer, I want the synthetic flow to convert content into minimal XML and then one simple image, so that integration cost stays low while the stage contract remains real.
76. As a Public Image maintainer, I want the original repositories, agent instructions, historical workflows, operational evidence, generated outputs, and local state left untouched, so that the compatibility work remains isolated.
77. As a future product maintainer, I want product-neutral atoms changed once in Candidate Core and re-proven against both adapters, so that fixes are shared without copying implementation code.
78. As a future product maintainer, I want an Adapter Scaffolding Skill to propose a Product Contract draft from repository evidence, so that onboarding a later project starts from structured facts.
79. As a future product maintainer, I want the draft explicitly confirmed before generation, so that safety and success semantics are never inferred automatically.
80. As a future product maintainer, I want the Skill to generate only adapter boundaries, conformance tests, CI, and a thin product Skill, so that Core algorithms remain versioned and hand-maintained.
81. As a future product maintainer, I want the scaffolding flow tested against an ephemeral third dummy contract, so that reuse is demonstrated without creating another product repository.
82. As a future product maintainer, I want Copier reconsidered only after two common structural changes across both real adapters, so that template machinery is adopted in response to measured maintenance cost.
83. As a future product maintainer, I want PyApp evaluated only if Python bootstrap remains a leading Phase 2 failure, so that a native launcher is not built speculatively.
84. As a future product maintainer, I want Velopack, Tauri, and `pluggy` deferred until their documented product-shape triggers occur, so that current scope is not enlarged by unrelated platform tooling.
85. As an auditor, I want Hosted CI, Real Lab Canary, Desktop E2E, and recording evidence reported separately, so that one green layer cannot imply an unexecuted later layer.
86. As an auditor, I want full Real Lab evidence kept local unless separately sanitized, so that public transparency does not require publishing sensitive operational state.
87. As an auditor, I want one named evidence authority for each final verdict, so that stale summaries cannot override the current result.
88. As an auditor, I want remaining gaps reported explicitly, so that incomplete Desktop or recording work is never converted into inferred success.

## Implementation Decisions

- The product shape is a deterministic Python Product Control Package exposed through one `productctl` CLI, with a thin Skill as the Agent-facing entrypoint. It is not a background middleware service or a universal framework.
- Phase 1 and Phase 2 use separate new Public-Source Lab Repositories. The original repositories remain read-only. The second remote is not created until Phase 1 passes and the sanitized export gate succeeds.
- Each repository initially carries no software license. Third-party dependencies are limited in the first version to MIT, BSD, or Apache-2.0 components and still require exact inventory and notices.
- The Candidate Core Package and short-essay application coexist as separate modules in the Phase 1 repository. Candidate Core uses `0.y.z` releases and is distributed initially as GitHub Release artifacts rather than PyPI.
- Each product owns a versioned Product Contract validated by JSON Schema. Repository inspection may prepare a draft, but identity, success, ownership, cleanup, secret, and acceptance semantics require explicit confirmation.
- The Product Contract declares product identity, entrypoint, supported operating systems and Python versions, runtime discovery, install payload, service and health behavior, data roots, Codex resolution, workflow stages and concurrency, artifacts, mutations, cleanup, secrets, and acceptance.
- Every command supports JSON output and returns a versioned Control Envelope containing run identity, stage tree, status, stable error category, observations, evidence references, and ownership.
- The atomic public surface covers runtime discovery, payload verification, process probing, transactional installation, service preflight and lifecycle, lease status and release, doctor, network probing, Codex resolution and probing, workflow execution, artifact inventory and verification, diagnostics collection, exact cleanup, and core acceptance.
- Product-critical subprocesses use absolute executable identities, argument arrays, and no shell mediation. Fixed version-controlled read-only probes are allowed only where a platform API requires them.
- Phase 1 supports Python 3.11 and 3.12 already present on the target. It proves discovery, pinned installation, staging, promotion, rollback, and final-path smoke behavior without promising a bundled interpreter or complete wheelhouse.
- The short-essay application exposes a minimal Flask API and server-rendered page. It persists run, stage, and error state in SQLite and persists bounded artifacts and receipts as files.
- The short-essay workflow is sequential analysis, two concurrent polish candidates, then sequential synthesis. One failed candidate yields `partial_success` with the surviving branch; both failed candidates fail the run. Codex failures are never silently retried.
- Phase 1 binds the product service to loopback on a dynamically allocated recorded port. Phase 2 retains port 3130 but requires listener ownership proof before use.
- VM identity, checkpoint, vTPM, SSH, network baseline, and capacity remain in existing Lab capabilities. Desktop UI operation, recording, and cloud publication remain distinct proof layers.
- Phase 2 begins from an allowlisted export of immutable Public Image revision `931d4245` with new history. The export classifies and hashes every file and excludes repository metadata, agent instructions, previous workflows, operational evidence, generated artifacts, local state, and Protected Prompt Assets.
- Synthetic Prompt Fixtures preserve only required role boundaries, slots, and parseable shapes. The public Phase 2 business flow converts content into minimal XML and then one simple image.
- Phase 2 consumes an immutable Candidate Core release identity and checksum. Candidate Core is not copied into the second repository, and a shared change must pass both Conformance Suites.
- Hosted CI runs a credential-free fake Codex executable and JSONL stream. Real Codex identity and model/transport resolution are reserved for Real Lab and Desktop gates.
- Fast Hosted CI runs on pull requests and pushes. The extended concurrency, packaging, rollback, and historical-failure matrix is manually dispatched and unscheduled.
- The supported Hosted CI matrix is Ubuntu 24.04, Windows Server 2022, and macOS 15 arm64 with Python 3.11 and 3.12.
- Ordinary GitHub Actions use read-only contents permission, no product secrets, full commit SHA pins for third-party Actions, cancellation of superseded work, and bounded timeouts. Release publication uses a separate tag/manual workflow with only required write authority.
- Successful CI publishes a compact summary and receipt. Failed CI retains a sanitized diagnostic bundle for seven days. Release artifacts include packages, manifests, checksums, dependency inventories, and notices.
- Hosted CI is not a Desktop acceptance claim. Real Lab and Desktop runs record requested and resolved Codex model/transport identity and never silently fall back.
- Phase 1 does not promise a fully offline install. Phase 2 preserves the existing offline payload-install boundary; real Codex inference remains online.
- Secrets, authentication files, protected prompts, and sensitive environment values never enter contracts or public evidence. Redaction and secret/prompt scanning are release gates.
- Ordinary product failures retain installation and run state. Rollback is reserved for contamination, invalid conditions, unclear causality, clean-install proof, or milestone completion. Each platform milestone ends with an exact baseline restore and one repeated acceptance.
- Third-party components enter Candidate Core only through bounded Component Spikes. The planned order is `platformdirs`, then a `portalocker`/`filelock` bake-off, then `psutil`. `uv` is a development and CI tool first and receives a target-runtime evaluation only in Phase 2.
- Copier is deferred until both adapters experience at least two common replayable structural changes. PyApp, Velopack, Tauri, and `pluggy` remain trigger-based evaluations rather than current dependencies.
- The Adapter Scaffolding Skill is built only after both product adapters pass. It generates adapter, test, CI, and thin-Skill surfaces after Product Contract confirmation and is validated against an ephemeral dummy product.
- Breaking pre-1.0 changes require migration notes, a schema version increase where applicable, same-milestone updates to both adapters, and retention of prior releases.
- The completion claim is limited to a proven candidate method for user-space, Skill-backed applications on Linux x86_64, Windows x64, and Apple Silicon macOS.

## Testing Decisions

- A good test observes externally visible behavior: command inputs, exit category, Control Envelope, persisted state, owned mutations, artifacts, and cleanup. Tests do not assert private function layout or select a dependency merely because its internal API is convenient.
- The single primary test seam is a confirmed Product Contract entering `productctl acceptance core` and producing a versioned Control Envelope plus a Run Artifact Set. Lower atomic commands exist for diagnosis and targeted historical regression fixtures, not as competing acceptance definitions.
- The same seam is exercised in three distinct proof lanes: credential-free Hosted CI with fake Codex, Real Lab Canary with the actual platform/runtime/account environment, and Codex Desktop E2E initiated from a new Desktop task.
- The Conformance Suite establishes equivalent control semantics for the Phase 1 and Phase 2 Product Adapters. A shared Candidate Core change is not accepted unless both products pass.
- The Historical Failure Registry is the prior-art source for targeted tests. Every known High or Extreme product-owned failure maps to an owning command/stage, expected structured outcome, applicable platforms, and synthetic CI or Real Lab proof lane.
- Hosted CI covers Linux x86_64, Windows x64, and Apple Silicon macOS across Python 3.11 and 3.12. It covers argument preservation, JSON encoding, path inheritance, filesystem behavior, concurrency from zero through four branches, partial failure, cancellation, timeout, listener ownership, artifact collision, diagnostics, and negative cleanup ownership.
- Fake Codex fixtures cover successful streams, malformed or truncated streams, nonzero exits, stderr with success and failure, startup failure, timeout, one-branch failure, two-branch failure, and explicit model/transport identity. They never require a real account secret.
- Installation tests observe discovery, target-specific dependency availability, staging, promotion, rollback, final-path launch, idempotent reinstall, and receipt persistence.
- Service and lease tests observe caller/owner/root/version identity, foreign listeners, stale ownership, permission denial, process exit, PID reuse, and exact release behavior.
- Network tests observe distinct route, DNS, proxy, TLS, certificate-revocation, and target-HTTP failure categories. Real endpoint behavior is proven only in Real Labs.
- Artifact tests observe unique physical files, stable page/order identity, manifests, hashes, missing or moved files, partial-success evidence, and exact cleanup. Raw sensitive Codex internals are not public test artifacts.
- Component Spikes run the same external conformance and historical fixtures before and after the candidate component. Adoption requires maintained or improved behavior, less platform code or materially stronger correctness, reproducible packaging, and acceptable license/security posture.
- Phase 1 exits only after Hosted CI is green and both Real Labs pass install, doctor, real Codex short-essay E2E, diagnostics, cleanup, exact baseline restore, and one repeat.
- Phase 2 export tests fail on any unclassified file, hash mismatch, secret/prompt scan result, or unsuccessful manual readback before the second public remote is created.
- Phase 2 exits only after the same Candidate Core revision passes both Product Adapters and both Real Labs without product-specific Core forks.
- Final Desktop E2E proves GitHub installation, Desktop runtime setup, restart usability, the real simplified workflow, and visible artifact inspection on Windows x64 and Apple Silicon macOS, with Linux CLI regression remaining green.
- Recording acceptance begins with a real short shakedown and reports recording validity independently from the product verdict.
- The Adapter Scaffolding Skill is tested by generating an ephemeral adapter from a third dummy Product Contract and running schema, static, and conformance checks without creating a third repository or regenerating Core atoms.

## Out of Scope

- A stable universal cross-platform framework or a `1.0` Core API.
- Intel macOS, Windows ARM, system-wide privileged installation, kernel services, or administrator-managed enterprise deployment.
- Replacing existing Windows or macOS Lab management, checkpoint, SSH, capacity, Desktop-operation, recording, or Cloudflare publication capabilities.
- A production-quality business workflow or quality benchmark for the short-essay application.
- Publishing Public Image Protected Prompt Assets, redacted variants of those prompts, original repository history, existing agent instructions, or operational evidence.
- A full offline Phase 1 interpreter and wheelhouse, PyPI publication, automatic application updates, code signing, or notarization.
- A conventional standalone desktop GUI, Tauri shell, Velopack installer, or custom Rust launcher unless a later trigger changes the product shape.
- Dynamic plugin discovery through `pluggy` before multiple real products demonstrate the need.
- Copier-based template distribution before repeated structural changes demonstrate acceptable replay value.
- Treating Hosted CI, CLI, sample output, screenshots, or recording alone as proof of Codex Desktop compatibility.
- Automatic publication of full Real Lab diagnostic evidence.
- Modifying either original Public Image repository.

## Further Notes

- The Phase 1 repository is intended to be `cross-platform-skill-runtime-lab`. The later Phase 2 repository is intended to be `public-image-ppt-3-0-compatibility-lab` and is created only at its sanitized export gate.
- The repositories are public to use standard public GitHub-hosted runner capacity, but lack of a repository license means the source should be described as public-source rather than open source.
- The initial development loop is repository-centered: a Coding Agent changes code and tests, Hosted CI returns structured evidence, Real Labs run deterministic entrypoints at milestone gates, and the Agent fixes the first failed stage. Strong GUI automation is required only at the final Desktop proof layer.
- Historical failures remain a compatibility asset, not merely retrospective notes. Command removal or consolidation must not leave a registered failure without a deterministic owner and proof lane.
- Any future claim of broader reuse requires evidence from additional products rather than inference from the two planned labs.
