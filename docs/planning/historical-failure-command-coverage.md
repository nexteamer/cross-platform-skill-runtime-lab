# Historical failure to command coverage

Source authority: `cross-platform-acceptance-retrospective.md` from the Public Image desktop-compatibility checkout. This is the planning coverage map; M0 converts it into individual machine-readable fixtures and external proof references.

The map intentionally does not force every platform problem into `productctl`. A row is covered only when it has both an owning layer and a deterministic entrypoint.

| Historical failure class | Owner | Deterministic entrypoint | Required proof |
|---|---|---|---|
| Hyper-V vTPM / Key Protector mismatch | Windows Lab | existing `labctl restore-and-verify` capability | Real Windows Lab |
| VM identity, checkpoint, network, SSH, proxy, capacity preflight | Windows/Mac Lab | existing `labctl verify` / capacity capability | Real Lab |
| SSH connect succeeds but command/output stalls | Windows Lab transport runner | staged SSH transaction receipt | Real Windows Lab |
| CP311/CP312 native wheels absent | Product payload | `productctl payload verify` | Hosted CI packaging fixture + Real Lab install |
| Windows-only environment marker omitted | Product payload | `productctl payload verify` | Windows Hosted CI fixture |
| usable Python rejected because base `pip` is absent | Candidate Core runtime | `productctl runtime discover` | 3-OS Hosted CI capability fixtures |
| fallback archive executable path guessed incorrectly | Product payload/runtime | `payload verify` + `runtime discover` | Hosted CI archive fixture |
| native stderr treated as process failure or truncated | Candidate Core process | `productctl process probe` and every stage receipt | 3-OS Hosted CI fake-process fixtures |
| empty native argument dropped | Candidate Core process | `productctl process probe` | Windows Hosted CI argument-vector fixture |
| embedded Python `-c` quoting corrupted | Candidate Core process policy | `process probe`; product-critical code uses argument arrays/files | Windows Hosted CI negative fixture |
| UTF-8 JSON written with BOM | Candidate Core receipt | every JSON-producing command | Windows Hosted CI encoding fixture |
| diagnostic receipt deleted with temporary staging | Candidate Core evidence ownership | `install` + `diagnostics collect` | failure-injection Hosted CI fixture |
| PowerShell/.NET API unavailable on PS5.1 | fixed read-only platform probe | `runtime discover` / `process probe` wrapper | Real Windows PS5.1 Lab + static fixture |
| Windows file fsync uses invalid access mode | Candidate Core filesystem atom | `install` and `doctor` | Windows Hosted CI durability fixture |
| POSIX directory fsync attempted on Windows | Candidate Core filesystem atom | `install` and `doctor` | Windows Hosted CI durability fixture |
| another subsystem reimplements the same bad fsync | Conformance Suite | `acceptance core` | cross-module static/conformance check |
| parent and child resolve different data roots | Product Contract + Candidate Core paths | `doctor` | 3-OS Hosted CI child-inheritance fixture |
| promoted venv launcher still points to staging | Candidate Core install transaction | `install` final-path smoke | Windows Hosted CI + Real Lab reinstall |
| AppX resource and managed cache incorrectly require equal hashes | Product Codex adapter | `codex resolve` | Windows Real Lab candidate fixture |
| quoted/unquoted Authenticode Publisher mismatch | Product Codex adapter | `codex resolve` | Windows Hosted CI certificate-data fixture + Real Lab |
| multiple valid Codex cache generations | Product Codex adapter | `codex resolve` | Windows Real Lab active-process selection receipt |
| child startup/transport has no persistent receipt | Candidate Core process/workflow | `codex probe` + `workflow run` | fake Codex Hosted CI + Real Lab |
| old or foreign process owns port 3130 | Product service adapter | `service preflight` | Hosted CI fake-listener fixture + Real Lab |
| route/DNS/proxy are green but TLS/CRL/SOCKS semantics fail | Product network adapter | `network probe` | synthetic Hosted CI layer fixtures + Real Lab endpoint probe |
| Desktop UI selector/observer/helper fails | Desktop operation layer | later `desktop-bridge probe` | actual Windows/macOS Desktop E2E |
| Mac capacity gate is too low | Mac Lab | existing Lab capacity capability | Real Mac Lab |
| provider/model transport times out while another path succeeds | Product Codex/workflow adapter | `codex probe` + `network probe` + `workflow run` | fake timeout matrix + Real Mac Lab |
| proxy environment hypothesis is unobservable or false | Candidate Core process evidence | `codex probe` with redacted child-environment presence | Hosted CI fake child + Real Lab |
| trusted executable path rejects active Mac Desktop executable | Product Codex adapter | `codex resolve` | Real Mac Lab signature/process receipt |
| installed dispatcher lacks executable bit | Product payload/install | `payload verify` + `install` final-path smoke | macOS Hosted CI + Real Lab |
| client/server deadline mismatch leaves DB state `running` | Candidate Core workflow | `workflow run` | Hosted CI timeout/cancel fixture + Real Lab |
| Desktop sandbox cannot register persistent user service | Product service adapter | `service preflight` selects supported lifecycle | Real Mac Desktop E2E |
| permission error is flattened into `busy` | Candidate Core lease/error taxonomy | `lease status` | macOS Hosted CI permission fixture + Desktop E2E |
| same-title pages overwrite PNGs | Product artifact adapter | `artifacts verify` | Hosted CI duplicate-title fixture |
| Preview dies when held service exits | Product artifact/service contract | `artifacts inventory|verify` + `lease status|release` | Hosted CI lifecycle fixture + Desktop E2E |
| historical artifact cannot later be located or attributed | Candidate Core artifact receipt | `artifacts inventory` | Hosted CI move/cleanup fixture + Real Lab receipt |
| recording creates no file or a 0.5-second artifact | Recording layer | `recording probe` then recording acceptance | real recording shakedown; never a product PASS/FAIL |
| cloud publication/upload/readback fails | publication lane | existing Cloudflare publication workflow | deployment evidence; outside Candidate Core |
| unsafe cleanup guesses by prefix or glob | Candidate Core mutation ownership | `cleanup exact --run-id` | 3-OS negative ownership fixtures |

## Coverage verdict

The current atomic CLI list covers every product-owned failure class in the retrospective. The remaining classes are deliberately assigned to Lab, Desktop, recording, or publication entrypoints rather than hidden inside a general-purpose `productctl`. M0 is not complete until every High/Extreme product-owned row has a fixture in `tests/fixtures/historical_failures/index.json`, and every externally owned row names its real proof gate.
