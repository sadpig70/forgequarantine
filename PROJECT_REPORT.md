# ForgeQuarantine Project Report

## Concept

Qualified printed components can remain in service long after their embedded cryptography becomes obsolete. A generic PQC backlog misses the physical reality: some components cannot be reflashed in the field, cannot be replaced quickly, and carry qualification evidence that must survive depot, flight, or defense acceptance.

ForgeQuarantine links those dimensions into a deterministic exposure ledger.

## Input Contract

- `component_manifest.json`: part number, platform, criticality, qualification level, print process, material, deployment environment, evidence references
- `crypto_dependencies.json`: algorithm, use case, key length, update path, crypto agility, evidence references
- `service_life.json`: current year, quantum horizon year, retirement year, replacement lead time, inspection interval

## Output Contract

The compiler emits:

- exposure class
- quarantine priority
- migration deadline year
- evidence gaps
- rationale
- hash-linked ledger entry

## SA Boundary

- `source_round=SA-EVX-20260611-001`
- `source_candidate=ForgeQuarantine`
- `cross_model_certified=false`
- `production_promotion_required=true`

This is standalone exploratory materialization evidence, not production certification.

## P0 Derivative Check

Checked against the current ledger and nearby implementations:

- `pqcmesh`: generic PQC migration compatibility for long-lived devices
- `gencert`: generator birth certificate and inherited trust
- `certmesh`: robot behavior certification drift
- `lazarettostage`: bio/ecological staged release
- `contextcreep`: persistent-agent accumulated-context attack paths

ForgeQuarantine stays distinct by anchoring cryptographic exposure to printed physical components, qualification evidence, and service-life deadlines.

## Verification

Expected local checks:

```bash
python -m pytest -q
python -m forgequarantine sample -c examples/component_manifest.json -d examples/crypto_dependencies.json -s examples/service_life.json
python -m forgequarantine run -c examples/component_manifest.json -d examples/crypto_dependencies.json -s examples/service_life.json --full -o examples/forgequarantine_report.json
python -m forgequarantine run -c examples/component_manifest.json -d examples/crypto_dependencies.json -s examples/service_life.json --markdown -o examples/forgequarantine_report.md
```

