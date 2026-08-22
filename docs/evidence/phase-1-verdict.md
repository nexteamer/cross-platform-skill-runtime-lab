# Phase 1 gate verdict

Candidate Core `0.1.0` at commit `a398888`, wheel SHA-256 `298eba45df62db9a825e229fbff0209fa7791cd346022db3ec41b5acd8cd30ae`. Hosted CI is not Real Lab. Real Lab is not Desktop E2E. This gate is **blocked** and is not an immutable Phase 1 release.

## Hosted CI

Fast matrix passed: https://github.com/nexteamer/cross-platform-skill-runtime-lab/actions/runs/32477471025

## macOS Real Lab — passed including restore + repeat

Guest `agent-mac-lab.shared`, VM `{3b204f34-395b-4ee9-8688-64964eb687db}`. Logged-in Codex is `/Applications/ChatGPT.app/Contents/Resources/codex`, model `gpt-5.6-terra`, transport `chatgpt`.

- First canary run `a890fd1c-4ce3-47d8-b447-c43bd6ca95e0`
- Restored baseline `配置好 Mac mini 以及 Codex` `{b37d9657-28a5-4d16-af09-934182b4491d}`
- Repeat run `60d572d3-3f71-45ae-905c-95eaff87ef74` passed probe, workflow, artifacts, diagnostics

Controller route was Mac-host shared SSH `agent@10.211.55.3`; guest bridged `192.168.5.x` was absent.

## Windows Real Lab — first canary passed; restore+repeat blocked

Guest `DESKTOP-2FJ6P9F`, VM `4805266a-64a5-4f85-b205-11b0c1cd76e7`. The live logged-in Codex is the ChatGPT app identity under `CODEX_HOME=C:\Users\Admin\.codex` (not the `agentops` profile), model `gpt-5.6-luna`.

- First canary run `5cb59864-9e04-4403-8d09-1fcc63cf4563` passed install, doctor, real probe, real workflow, artifacts, diagnostics
- Restored checkpoint `mini-pc-recovered-baseline-v2-20260818-2030` (`2dad06ab-3dec-4f25-a914-4eeb7c77de35`); identity probe passed
- Repeat install/doctor passed; real probe and workflow `1f5c30f3-122d-4975-8312-4eedf5daaefb` failed with `codex_auth_missing` because the baseline refresh token is expired (`invalid_refresh_token`)

No new login was performed after restore.

## Not claimed

Codex Desktop E2E, recording, Phase 2 Public Image export, and an immutable Phase 1 GitHub Release remain unpublished because ticket 14 requires both platforms' restore+repeat.
