# AQ26 Public Methods and Coverage Standard

Status: normative public-copy and release-gate standard.

This document defines the minimum scientific wording and evidence fields required when AQ26 publishes station coverage, PM2.5 screening results, statistical adjustments or a zero-candidate result. It is intentionally stricter than general editorial guidance.

## 1. Coverage claims

### Required wording principles

Public copy must distinguish:

- the source inventory denominator;
- stations present in the analytical dataset;
- stations eligible for the live screen;
- stations excluded or not assessed;
- geographic presence from geographic representativeness.

The phrase `142/142 stations` must not be used where a reader could interpret it as complete English-network coverage.

Absence from the analytical dataset must not be described as failure of quality, completeness or freshness criteria unless the station-level exclusion ledger records that reason.

### Approved baseline wording

> The source inventory used for this release listed 171 active AURN monitoring stations in England. The published 30-day analytical dataset contains observations from 142 of those stations and includes at least one station in each of the nine English regions.
>
> This should not be interpreted as complete or spatially representative coverage of the full English monitoring network. The current analytical dataset does not include the 15 stations classified as Rural Background in the wider inventory, and the balance of station types and station numbers differs between regions.
>
> England-level and regional summaries describe the stations represented in this release. They do not estimate conditions at every location or individual exposure across England.

The inventory date, station definition and provenance link must be published with the denominator.

## 2. Provisional-data status

Where observations are provisional, the following statement must appear near the principal result rather than only in a data dictionary:

> Observations used in this review are provisional unless explicitly stated otherwise and may subsequently be revised or invalidated by the original data provider.

A successful software test or successful retrieval must never be described as provider validation.

## 3. Live PM2.5 screening scope

The live screen is an operational early-warning filter for PM2.5 station assessments. It does not confirm an environmental episode and does not identify a source, facility, cause, health effect or regulatory breach.

The screen must not be presented as an all-pollutant air-quality assessment.

## 4. Eligibility wording

A station assessment enters the statistical screen only when all current configured requirements are met. At the time this standard was written, the production logic required:

1. newest usable observation no more than four hours old;
2. at least 18 valid hourly observations in the preceding 24 hours;
3. at least 48 valid hourly observations in the preceding 72 hours; and
4. no unresolved provider or pipeline quality condition designated as exclusionary.

These values must be read from or reconciled with the current production configuration before every release. Public copy must not silently hard-code stale thresholds.

A station that fails eligibility is `not assessed`; it is not treated as having passed the screen.

## 5. Raw operational trigger

For each eligible station, the current 24-hour PM2.5 mean is compared with a short station-specific recent-history window using a robust standardised score.

At the time this standard was written, a raw candidate required both:

- 24-hour PM2.5 mean at least 15 micrograms per cubic metre; and
- robust standardised score at least 3.

The 15 micrograms per cubic metre value is an operational screening floor. Crossing it does not by itself establish a legal exceedance, health finding or confirmed pollution event.

The 72-hour comparison window must be described as a recent operational reference, not a climatological or known-clean baseline.

## 6. Multiplicity adjustment

The production implementation derives an operational one-sided standard-normal tail score from the robust z value and applies a Benjamini-Hochberg adjustment to the defined family of eligible station hypotheses.

Approved wording:

> The operational Benjamini-Hochberg decision parameter is 0.05. This adjustment is intended to reduce multiplicity-related false alarms within an individual screening run. It must not be interpreted as establishing formally calibrated 5% false-discovery-rate control.

The following limitations must be stated:

- tail scores are not calibrated inferential p-values;
- no empirical null has yet been established;
- measurements are dependent across time and space;
- repeated-run error control over days or weeks is not established;
- overlapping assessment and comparison windows, where present, limit independence.

Public copy must not use `5% significance threshold` without the above qualification.

## 7. Meaning of a candidate

A screening candidate means only that a station assessment crossed the current operational criteria and warrants further review.

It does not establish:

- a long-term or seasonal anomaly;
- a confirmed pollution episode;
- a particular source contribution;
- a health impact;
- a legal or regulatory breach.

Any later review must distinguish implemented automated gates from optional analyst review or planned future capability.

## 8. Meaning of zero

Approved wording:

> A result of zero means that no eligible station assessment crossed all current operational screening criteria during that run. It does not mean that pollution was absent, concentrations were harmless, every station was assessed or all pollutants were screened.

The expressions `healthy zero`, `all clear`, `nothing detected` and `no pollution event` are prohibited unless supported by a separate, explicitly bounded assessment.

Every zero result must be accompanied by its denominator and exclusions.

## 9. Mandatory release metrics

Each public screening release must publish, or link directly to, the following machine-readable and human-readable fields:

- inventory stations;
- retrieval successes and failures;
- fresh station assessments;
- insufficient 24-hour-history exclusions;
- insufficient 72-hour-history exclusions;
- provider or pipeline quality exclusions;
- other exclusion reasons;
- eligible station hypotheses entering adjustment;
- raw concentration-floor crossings;
- raw dual-trigger candidates;
- adjusted candidates;
- run timestamp and timezone;
- code commit;
- configuration or threshold version;
- degraded-mode status.

## 10. Station inclusion ledger

The release pack should contain one row per inventory station with:

- station identifier and name;
- region and site classification;
- configured pollutants;
- source inventory status;
- retrieval status;
- newest usable observation time;
- 24-hour and 72-hour valid counts;
- provider and pipeline quality flags;
- inclusion in the 30-day dataset;
- inclusion in the live screen;
- exclusion reason code;
- source URL.

No public statement may assign a reason for absence unless this ledger supports it.

## 11. Distributional context

National and regional summaries should publish more than a maximum. Minimum recommended context is:

- station count;
- median;
- interquartile range;
- 10th and 90th percentiles;
- completeness distribution;
- site-classification breakdown;
- maximum with station identity and completeness.

## 12. Software tests versus live-data verification

Approved wording:

> Automated tests check that pipeline components behave as specified against controlled inputs. They do not independently verify that every live observation supplied during the current reporting period is correct.

Public status surfaces should report software, retrieval, schema, completeness, provider-quality, analytical-eligibility and public-reconciliation states separately.

## 13. Required implementation checks

Before the website wording is treated as complete, automated tests should verify that:

- coverage copy does not imply full-network representativeness;
- excluded Rural Background stations are not assigned an unsupported reason;
- zero-candidate output includes eligible and excluded denominators;
- `formal FDR control not established` appears wherever BH-controlled screening is summarised;
- provisional status is present beside principal 30-day findings;
- PM2.5-only scope is explicit;
- prohibited all-clear language is absent;
- generated methodology text is reconciled with current production thresholds.

## 14. Validation roadmap

The operational detector should be evaluated through historical replay, including seasonal and station-type stratification, sensitivity to missingness and window construction, known-episode comparison, repeated-run multiplicity, empirical-null calibration and dependence-aware alternatives.

Until that work is complete, AQ26 should describe the method as a transparent operational screening rule, not a validated anomaly detector.
