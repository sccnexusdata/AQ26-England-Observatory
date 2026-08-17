# AQ26 Scientific Assurance Standard

## Status

This is an internal publication-control standard. It does not claim external academic, regulatory or professional endorsement.

## SCC/VVIP operating model

AQ26 applies **Search, Corroborate, Communicate** through four mandatory assurance dimensions: validation, verification, integrity and provenance. A source being reachable or a record being downloaded is never equivalent to scientific validation.

## Claim ladder

1. **Acquired** — bytes retrieved and checksummed.
2. **Parsed** — schema and units recorded.
3. **Quality assessed** — completeness, freshness, flags and method metadata assessed.
4. **Corroborated** — independent dimensions joined reproducibly.
5. **Scientifically reviewed** — method, uncertainty and counterevidence reviewed by a named competent reviewer.
6. **Publication approved** — exact wording, geography, time period and evidence IDs approved.
7. **Superseded or withdrawn** — retained with reason and replacement link.

No public statement may skip a stage. Automated source attribution, causation, legal compliance, personal exposure and health-effect conclusions remain prohibited.

## Mandatory release fields

Every public release must record: release ID; Git commit; workflow run; build inputs; source URLs and licence; retrieval time; source timestamp; ETag/Last-Modified when available; raw and transformed hashes; transformation version; units and averaging periods; geography; missingness; uncertainty; reviewer identity/role; decision; and deployment verification.

## Screening terminology

AQ26's current robust-z/BH process is a transparent **heuristic review-workload screen**. It is not described as formal false-discovery-rate control until p-values are empirically calibrated and spatial/temporal dependence is evaluated. A 24-hour health guideline is compared only with a sufficiently complete rolling 24-hour mean, never a single hourly observation.

## Human review

External endorsement may be stated only when a reviewer has approved the exact release wording and the signed/dated review record is retained. Naming a potential audience or expert does not imply review or approval.
