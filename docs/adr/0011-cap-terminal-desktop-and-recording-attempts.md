---
status: accepted
---

# Cap terminal Desktop and recording attempts

For the final Windows Desktop, macOS Desktop, Windows recording, macOS recording, and bounded-verdict work, allow at most five attempts for the same unresolved failure category. A sixth attempt is prohibited. If a Desktop E2E ticket reaches the cap without passing, its downstream recording ticket is skipped without execution. If Desktop E2E passes but recording reaches the cap, stop that platform branch at recording. Preserve the terminal evidence and let the final verdict report `PASS`, `BLOCKED`, and `SKIPPED` independently rather than weakening acceptance or continuing open-ended GUI work.
