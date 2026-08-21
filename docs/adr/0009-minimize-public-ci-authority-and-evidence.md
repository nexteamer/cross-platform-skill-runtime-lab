---
status: accepted
---

# Minimize public CI authority and evidence

Run public pull-request and push workflows without product credentials, protected prompts, or real Codex login state. Default workflow permissions to `contents: read`, pin third-party Actions to full commit SHAs, prohibit secrets in pull-request jobs, and isolate release authority in a tag/manual workflow with only the write permissions it needs. Apply job timeouts, cancel superseded runs, and do not schedule the expensive matrix. Public artifacts contain only sanitized fixtures, summaries, and bounded diagnostic receipts; full Real Lab evidence stays local unless separately reviewed and sanitized.
