# ForgeQuarantine

ForgeQuarantine compiles an additive-manufacturing PQC exposure ledger for qualified physical components.

It is not a generic PQC migration scanner. It ties cryptographic dependency risk to:

- printed component qualification evidence,
- physical criticality,
- firmware update path,
- service-life overlap with the quantum horizon,
- evidence gaps that can block acceptance or deployment.

## Status

- Source round: `SA-EVX-20260611-001`
- Source artifact: `.sa-evx/rounds/SA-EVX-20260611-001/final_integrated_idea.md`
- Source candidate: `ForgeQuarantine`
- `cross_model_certified=false`
- `production_promotion_required=true`

This repository is a standalone single-runtime materialization. It must not be presented as production-certified AOX/CIX/EVX output.

## Install

```bash
python -m pip install -e .
```

## Quick Start

```bash
python -m forgequarantine sample \
  -c examples/component_manifest.json \
  -d examples/crypto_dependencies.json \
  -s examples/service_life.json

python -m forgequarantine run \
  -c examples/component_manifest.json \
  -d examples/crypto_dependencies.json \
  -s examples/service_life.json \
  --full \
  -o examples/forgequarantine_report.json

python -m forgequarantine run \
  -c examples/component_manifest.json \
  -d examples/crypto_dependencies.json \
  -s examples/service_life.json \
  --markdown \
  -o examples/forgequarantine_report.md
```

## Output Shape

Each exposure record contains:

- `component_id`
- `dependency_id`
- `algorithm`
- `risk_label`
- `exposure_class`
- `quarantine_priority`
- `migration_deadline_year`
- `exposure_score`
- `evidence_gaps`
- `entry_hash`

## Differentiation

ForgeQuarantine differs from `pqcmesh` by using a physical component qualification and service-life frame, not broad device inventory migration. It differs from `certmesh` because it does not evaluate learned behavior drift. It differs from `gencert` because it does not issue generator birth certificates. It differs from `lazarettostage` because the quarantine target is a printed aerospace/defense component's cryptographic exposure, not ecological release.

## Verify

```bash
python -m pytest -q
python -m forgequarantine sample -c examples/component_manifest.json -d examples/crypto_dependencies.json -s examples/service_life.json
python -m forgequarantine run -c examples/component_manifest.json -d examples/crypto_dependencies.json -s examples/service_life.json --full -o examples/forgequarantine_report.json
python -m forgequarantine run -c examples/component_manifest.json -d examples/crypto_dependencies.json -s examples/service_life.json --markdown -o examples/forgequarantine_report.md
```

