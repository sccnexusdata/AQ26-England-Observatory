# AQ26 research roadmap

This roadmap describes scientific-development priorities for the public AQ26 Observatory. It does not imply that every listed source is already operational, redistributable or suitable for evidential use.

## Scientific objective

AQ26 is being developed as a reproducible England environmental evidence-fusion observatory that can:

1. describe official air-quality observations and their coverage accurately;
2. detect unusual temporal or spatial behaviour without pre-selecting a source or facility;
3. quantify missingness, freshness, quality state and uncertainty;
4. test competing environmental explanations using independent or explicitly dependency-labelled evidence; and
5. record when the available evidence is insufficient for attribution.

The project must not infer source attribution, causation, individual exposure, health effect, permit breach or legal non-compliance from proximity, timing or a single evidence stream.

## Priority evidence layers

### P1 — strengthen the observational and physical evidence base

- **Specialist UK air-quality networks:** particle composition/speciation, black carbon, ammonia, rural-background and particle-number evidence where licensing and stable access permit.
- **NAEI spatial emissions:** sector-specific gridded emissions and point-source context, retained as emissions evidence rather than proof of contribution at a receptor.
- **Defra PCM/modelled background:** annual contextual concentration and source-apportionment products, with dependency on monitoring calibration explicitly recorded.
- **Sentinel-5P Level-2 products:** actual QA-filtered atmospheric retrievals rather than metadata-only discovery. Satellite columns must never be represented as surface measurements.
- **Vertical aerosol evidence:** CEDA/E-PROFILE or equivalent ceilometer/lidar profiles where available.
- **Atmospheric transport:** trajectory and ensemble transport modelling, such as HYSPLIT, for hypothesis testing rather than deterministic source assignment.
- **Regional atmospheric modelling:** CAMS European ensemble/reanalysis, preserving ensemble spread and monitoring-assimilation dependencies.

### P2 — uncertainty, additional remote sensing and independent model comparison

- MAIAC aerosol optical depth with QA and aerosol-model metadata;
- IASI atmospheric-composition products where data-use conditions permit;
- EarthCARE vertical aerosol/cloud profiles for event-specific overpasses;
- a second atmospheric-composition model family such as GEOS-CF for model-disagreement analysis;
- formal change-point detection for event onset and termination;
- conformal or probabilistic prediction intervals;
- hierarchical spatial/background models with out-of-sample validation.

### Watch / research-only

- Sentinel-4 geostationary European atmospheric-composition products once operational Level-2 access and QA behaviour are sufficiently mature;
- AI foundation models for atmospheric forecasting as shadow research products only until their evidential dependencies and calibration are independently understood;
- receptor modelling such as PMF only when suitable chemical-speciation evidence, diagnostics, uncertainty analysis and expert review are available.

## Validation programme

New methods should not move directly from prototype to public interpretation. Promotion requires a documented sequence:

`registered → acquired → parsed → quality checked → scientifically validated → shadow evaluated → release eligible`

At minimum, validation should assess:

- temporal and spatial coverage;
- units and averaging periods;
- measurement/model/satellite evidence class;
- provisional versus ratified or provider quality status;
- missingness and exclusion rules;
- source dependencies and non-independence;
- sensitivity to method parameters;
- performance on known event and quiet control periods;
- false-alert behaviour and stability across repeated runs;
- reproducibility from a clean environment.

## First forensic case study

A broad PM2.5 episode observed across many English monitoring locations in July 2026 is a suitable retrospective test case because its spatial coherence allows competing explanations to be tested without beginning from a single local-source hypothesis.

The detector configuration should be frozen before explanatory datasets are inspected. The case study should then compare ground observations with, where available and appropriate, chemical composition, rural-background measurements, meteorology, emissions context, trajectories, regional models and satellite/vertical-profile evidence. An inconclusive result is scientifically acceptable.

## Public-release rule

A new source or analytical method is not valuable merely because it increases source count. It should be promoted only when it answers a defined scientific question, improves uncertainty or coverage, discriminates between competing hypotheses, or materially strengthens reproducibility.

Public releases remain governed by the repository's publication policy and `PUBLIC_RELEASE_MANIFEST.json`. Third-party data remain subject to their own licensing and reuse conditions.
