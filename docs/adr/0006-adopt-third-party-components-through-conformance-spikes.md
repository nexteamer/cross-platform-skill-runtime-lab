---
status: accepted
---

# Adopt third-party components through Conformance Spikes

Do not bulk-adopt the researched tool list and do not impose a standard-library-only rule. Evaluate one component at a time against the historical failure fixtures, supported platform/Python matrix, packaging and offline constraints, fail-closed ownership semantics, and Control Envelope observability. Version 1 admits only permissively licensed dependencies (MIT, BSD, or Apache-2.0), pins exact versions and hashes, and publishes the applicable dependency inventory and third-party notices even though the lab repositories themselves initially carry no software license. A component enters the Candidate Core only when it removes meaningful platform code without weakening these contracts; otherwise retain the proven implementation behind the same interface and record the rejection.
