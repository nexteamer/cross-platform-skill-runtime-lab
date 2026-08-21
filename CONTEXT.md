# Cross-platform Skill Runtime Lab

This context defines the language for proving that a Skill-backed local product can be installed, operated, diagnosed, and accepted consistently across supported desktop platforms.

## Language

**Compatibility Lab**:
A public, non-sensitive short-essay product used to discover and prove cross-platform control behavior before applying it to Public Image.
_Avoid_: Universal framework, Public Image clone, toy app

**Product Control Package**:
A deterministic package that exposes one product's lifecycle and evidence operations through a stable command interface.
_Avoid_: Middleware service, agent script collection, universal productctl

**Product Adapter**:
The product-owned definitions that connect the Product Control Package to a product's paths, processes, health checks, workflow, and artifacts.
_Avoid_: Platform backend, generated application

**Candidate Core Package**:
The pre-1.0, versioned collection of product-neutral control atoms proven by both lab products before any claim of stable generality.
_Avoid_: Universal framework, copied productctl, stable Core

**Component Spike**:
A bounded evaluation of one third-party component against the Conformance Suite, packaging constraints, and historical failure fixtures before it may enter the Candidate Core Package.
_Avoid_: Dependency adoption, library trial, tool preference

**Control Envelope**:
The shared, versioned result shape through which every control command reports its run, stage tree, outcome, error, evidence, and ownership.
_Avoid_: Command log, platform-specific receipt, free-form JSON

**Protected Prompt Asset**:
High-value Public Image business prompt content that remains exclusively in the original product repository and is excluded from derived lab or integration repositories.
_Avoid_: Sample prompt, fixture prompt, configuration

**Synthetic Prompt Fixture**:
A deliberately minimal, non-proprietary prompt that preserves the protected workflow's input slots, stage transition, and output shape without preserving its business method or quality.
_Avoid_: Redacted production prompt, simplified production prompt

**Public Image Integration Lab**:
A public, isolated repository based on one exact Public Image revision after the Compatibility Lab passes, with Protected Prompt Assets excluded and Synthetic Prompt Fixtures substituted at their contracts.
_Avoid_: Public Image Integration Copy, original repository, public fork, synchronized mirror

**Sanitized Source Export**:
An allowlisted source snapshot derived from one immutable revision without inheriting repository history, protected assets, operational evidence, or local working-tree changes.
_Avoid_: Repository copy, cleaned fork, current checkout

**Public-Source Lab Repository**:
A public GitHub repository with no software license, used here for transparent compatibility evidence and public-runner eligibility while its copyright remains reserved.
_Avoid_: Open-source project, Private repository

**Hosted CI Gate**:
The disposable, credential-free operating-system matrix that proves deterministic code and process behavior without claiming a real Codex Desktop result.
_Avoid_: Desktop acceptance, real model canary

**Real Lab Canary**:
A bounded run on the dedicated Windows or macOS lab that proves behavior against the actual platform, installed runtime, user state, and product environment.
_Avoid_: Hosted CI, GUI acceptance

**Desktop E2E**:
The final user-facing flow initiated through Codex Desktop and evaluated through the real Skill, product result, and visible artifacts.
_Avoid_: CLI smoke test, Lab Canary

**Conformance Suite**:
The shared behavioral contract used to determine whether two product implementations exhibit the same control semantics and evidence shape.
_Avoid_: Unit-test count, copied test folder

**Adapter Scaffolding Skill**:
A Coding Agent workflow that derives a Product Contract and generates only a Product Adapter, its conformance tests, CI skeleton, and thin product Skill while referencing the Candidate Core Package.
_Avoid_: Core generator, universal productctl Skill, free-form code generator

**Product Contract**:
A confirmed, versioned declaration of one product's identity, lifecycle, success semantics, ownership boundaries, and acceptance surface; it is the authority from which an adapter is generated and tested.
_Avoid_: Repository scan result, prompt, generic configuration file, guessed metadata

**Historical Failure Registry**:
A traceable inventory that maps each known incident class to its responsible layer, control command and stage, expected structured failure, applicable platforms, and required proof lane.
_Avoid_: Test list, issue archive, retrospective narrative

**Run Artifact Set**:
The bounded input snapshots, branch outputs, final result, manifest, receipts, and sanitized failure evidence that together establish what happened in one workflow run.
_Avoid_: Logs directory, output folder, raw Codex transcript

**Partial Success**:
A run outcome where at least one parallel business branch fails but a valid final result is produced from the surviving branch while the failure evidence remains visible.
_Avoid_: Success, retried success, ignored failure
