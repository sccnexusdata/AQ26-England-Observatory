# AQ26 England Air Quality Observatory

**Public evidence, methodology and reproducibility surface for an independent England-wide air-quality and environmental evidence observatory.**

AQ26 combines official monitoring observations with meteorological, emissions, satellite, modelled and contextual evidence. This public repository is a governed output of a separate private scientific engine: only material that passes AQ26 public-release and export checks is copied here.

> **Status:** repository scaffold established. The first governed scientific release is intentionally withheld until the current public-metric reconciliation corrections have passed deterministic and release-gate testing.

## Scientific boundary

AQ26 is an evidence-screening and descriptive environmental observatory. A monitoring observation, model output, satellite product, traffic record, permit document or other single source does **not** by itself establish source attribution, causation, individual exposure, health effect, permit breach or legal non-compliance.

A zero screening result means only that no eligible assessment crossed the declared screening criteria for that release. It must not be interpreted as proof of clean air or absence of pollution.

## Publication model

The public repository does **not** mirror the private scientific engine. Publication is one-way:

`private engine → acquisition → QA/QC → analysis → scientific gates → public reconciliation → sanitised export → this repository`

Every automated export is allowlisted and hash-manifested. Protected/test outputs, credentials, deployment configuration and provider-restricted raw material are excluded.

## Repository structure

- `site/` — reviewed public website releases.
- `data/latest/` — selected public-safe machine-readable evidence summaries.
- `reports/latest/` — public scientific appraisal material.
- `provenance/` — approved runtime and reproducibility receipts.
- `docs/` — methodology, governance and publication documentation.
- `PUBLIC_RELEASE_MANIFEST.json` — SHA-256 manifest for the current governed export.

## Data quality and interpretation

Public outputs must be interpreted together with their stated:

- temporal coverage and freshness;
- monitoring-network and site-class coverage;
- pollutant and averaging-period definitions;
- units and count units;
- provisional/ratified or provider quality state;
- exclusions and missingness;
- model/satellite/measurement evidence class;
- provenance and transformation lineage.

AQ26 does not treat models or satellite retrievals as ground measurements and does not infer source from proximity or temporal coincidence alone.

## Data licensing

AQ26 does not claim ownership of third-party observations or datasets. Source-specific licences and reuse conditions continue to apply. Public redistribution is limited to material for which AQ26 has an appropriate publication basis or to derived summaries that preserve source attribution and limitations.

A repository-wide software/data licence has deliberately **not** yet been applied because code and third-party-derived data require separate licensing treatment.

## Independent scrutiny

Evidence-based methodological critique, reproducibility checks and corrections are welcome. Scientific challenges should identify the relevant source, time period, units, quality state and supporting evidence.

---

AQ26 is independent and is not an official Defra, Environment Agency, Met Office, Copernicus, NASA, National Highways, local-authority or university service.
