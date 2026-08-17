# Air Quality England Observatory traceability

| Public/output surface | Canonical inputs | Transformation | Principal guard |
|---|---|---|---|
| England 30-day review | official monitoring records, station registry and provenance | quality control, daily aggregation, station and regional eligibility | station/region denominators, completeness and claim-boundary checks |
| Current measurements | official current-monitoring responses and provenance | current collector and freshness screening | freshness, station identity, units and provenance checks |
| Source status | canonical source catalogue and collector results | source-status normalisation | no silent omissions, unique source IDs and maturity-state separation |
| Cross-reference status | configured joins and executed convergence outputs | cross-reference audit | configured/executed/validated/blocked distinctions |
| Weekly report | audited outputs and release status | report and site builder | claim boundary, coverage denominators and non-empty checks |
| Public evidence | promoted, public-safe evidence only | forensic hardening and review-workload triage | quarantine reconciliation and leak guard |
| Map | official station registry plus separately labelled supplementary context | site builder and presentation policy | layer separation and non-attribution wording |
| Protected review | reviewed public/protected build data | PHP authentication conversion | unauthenticated denial and authenticated content reconciliation |
| Social package | exact successful reviewed artifact | social renderer and public-language normalisation | stale-metric reconciliation, evidence matching and explicit confirmation |
| Engineering-assurance display | tests, receipts and release states | external-review hardening | explicit statement that software assurance is not peer review or endorsement |

Every review artifact must identify repository, commit, workflow/run context and file hashes. A technical linkage validates only the stated identity, temporal or geographic rule; it does not establish causation or source contribution.

A reviewer checking scientific accuracy should reconcile sampled published records to the official source rather than relying only on successful automated tests.
