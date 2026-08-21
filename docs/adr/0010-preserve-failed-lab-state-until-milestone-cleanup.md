---
status: accepted
---

# Preserve failed Lab state until milestone cleanup

Retain the current installation and run state after an ordinary product failure so diagnosis, repair, retest, and observation use the same evidence-bearing environment. Restore a checkpoint only for contamination, invalid test conditions, unclear causality, an explicit clean-install proof, or platform milestone completion. At each platform completion gate, restore the exact recorded baseline once, re-prove machine identity and readiness, repeat the acceptance flow, then perform ownership-bounded cleanup.
