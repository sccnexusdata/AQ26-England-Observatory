# AQ26 public publication governance

## Purpose

This repository is the public scientific publication surface for AQ26. It is not a clone or fork of the private scientific engine.

## One-way release architecture

Publication proceeds only in this direction:

1. Acquire source evidence in the private engine.
2. Preserve retrieval provenance and raw-response hashes where permitted.
3. Apply source-specific parsing, unit, time, coordinate and quality controls.
4. Produce analytical outputs with missingness and uncertainty retained.
5. Pass scientific claim and public-surface reconciliation gates.
6. Build an explicit allowlisted export.
7. Scan the export for protected paths, credential material and unexpected file types.
8. Generate SHA-256 hashes and source-run provenance.
9. Validate the public bundle independently in this repository.
10. Only then publish or deploy the release.

The public repository must never need read access to the private engine.

## Release states

- `withheld_pending_reconciliation` — no scientific release is current because an identified reconciliation or validation issue remains open.
- `candidate` — a bundle has passed the private export boundary but is awaiting public-side validation.
- `published` — the public bundle has passed both private and public release checks.
- `superseded` — retained for provenance but replaced by a later release.
- `withdrawn` — a release has been withdrawn because a material error or publication issue was identified.

A withheld or withdrawn state is a scientific control, not a workflow failure.

## Evidence classes

AQ26 distinguishes evidence by what it can legitimately represent. At minimum:

- ground measurement;
- calibrated or supplementary sensor context;
- meteorological observation or forecast;
- emissions inventory;
- atmospheric model;
- satellite retrieval or catalogue product;
- traffic/activity context;
- regulatory/planning/operational record;
- population or receptor context;
- derived analytical result.

Models and satellite observations are not relabelled as ground measurements. Aggregated health or population data do not establish individual exposure or health effects.

## Claim boundary

A descriptive observation may be published after the relevant measurement quality, denominator and provenance requirements pass.

Any source hypothesis additionally requires appropriate meteorology, comparator/background evidence, explicit competing-source analysis and stated uncertainty. Spatial proximity or temporal coincidence alone is insufficient.

No AQ26 output by itself establishes legal non-compliance, permit breach, individual exposure, health effect or causation.

## Required public metadata

Each public analytical metric should carry or inherit:

- source identifier and authority;
- retrieval or observation period;
- pollutant/variable and averaging period;
- units and count unit;
- geography and site/network role where relevant;
- quality/ratification state;
- expected, valid, excluded and missing denominators where relevant;
- model/satellite processing level and version where relevant;
- transformation lineage;
- uncertainty or limitations;
- source-specific licence/reuse basis.

## Reconciliation principle

Human-visible pages and machine-readable summaries must use the same governed metric definitions. A release must fail closed if a rendered metric changes its denominator, unit, evidence source or scientific meaning relative to the canonical release object.

## Corrections

Material corrections should be visible in repository history and, where a published scientific result changed, documented in a correction note. Releases should not be silently rewritten to conceal an earlier error.

## External scrutiny

Scientific criticism and reproducibility testing are encouraged. Challenges should identify the exact metric, time window, source, unit, quality state and evidence supporting the proposed correction.
