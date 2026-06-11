"""Exposure ledger compiler."""

from __future__ import annotations

import hashlib
import json

from .models import Component, CryptoDependency, ExposureRecord, ExposureReport, ServiceLife, ServicePolicy
from .validate import clamp


BOUNDARY = {
    "source_round": "SA-EVX-20260611-001",
    "source_artifact": ".sa-evx/rounds/SA-EVX-20260611-001/final_integrated_idea.md",
    "source_candidate": "ForgeQuarantine",
    "cross_model_certified": False,
    "production_promotion_required": True,
    "validation_level": "standalone_single_runtime_materialization",
}


def _classify(score: float, dep: CryptoDependency, component: Component, service: ServiceLife | None, policy: ServicePolicy) -> str:
    if dep.risk_label() == "pqc_ready":
        return "pqc_aligned"
    if service is None:
        return "unmapped_service_life"
    if dep.risk_label() in {"quantum_broken", "classically_broken"} and service.planned_retirement_year >= policy.quantum_horizon_year:
        return "service_life_crypto_quarantine"
    if dep.risk_label() in {"quantum_broken", "classically_broken"}:
        return "legacy_crypto_containment"
    if score >= 0.58 and component.criticality_weight() >= 0.70:
        return "qualification_watch"
    return "managed_exposure"


def _priority(score: float) -> str:
    if score >= 0.76:
        return "urgent"
    if score >= 0.58:
        return "high"
    if score >= 0.35:
        return "monitor"
    return "archive"


def _deadline(policy: ServicePolicy, dep: CryptoDependency, service: ServiceLife | None, priority: str) -> int:
    if dep.risk_label() in {"pqc_ready", "symmetric_resilient"}:
        return service.planned_retirement_year if service else policy.quantum_horizon_year
    lead_months = service.replacement_lead_months if service else policy.default_lead_months
    lead_years = max(1, round(lead_months / 12))
    if priority == "urgent":
        lead_years += 1
    if service is None:
        return max(policy.current_year, policy.quantum_horizon_year - lead_years)
    return max(policy.current_year, min(policy.quantum_horizon_year - lead_years, service.planned_retirement_year - 1))


def _evidence_gaps(component: Component, dep: CryptoDependency, service: ServiceLife | None) -> tuple[str, ...]:
    gaps: list[str] = []
    if not component.evidence_refs:
        gaps.append("missing component qualification evidence")
    if not dep.evidence_refs:
        gaps.append("missing crypto dependency evidence")
    if service is None:
        gaps.append("missing service-life profile")
    elif not service.evidence_refs:
        gaps.append("missing service-life evidence")
    if dep.key_length <= 0:
        gaps.append("missing key length")
    if dep.firmware_update_path == "unknown":
        gaps.append("missing firmware update path")
    return tuple(gaps)


def _hash_entry(prev_hash: str, payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256((prev_hash + canonical).encode("utf-8")).hexdigest()


def compile_records(
    batch_id: str,
    components: tuple[Component, ...],
    dependencies: tuple[CryptoDependency, ...],
    policy: ServicePolicy,
) -> tuple[ExposureRecord, ...]:
    component_by_id = {item.component_id: item for item in components}
    service_by_id = policy.service_map()
    records: list[ExposureRecord] = []
    prev_hash = hashlib.sha256(batch_id.encode("utf-8")).hexdigest()
    for dep in dependencies:
        component = component_by_id.get(dep.component_id)
        if component is None:
            component = Component(dep.component_id, "unknown", "unknown", "mission", "prototype", "unknown", "unknown", "unknown", ())
        service = service_by_id.get(dep.component_id)
        service_overlap = 0.0
        if service is not None:
            remaining = service.remaining_years(policy.current_year)
            if service.planned_retirement_year >= policy.quantum_horizon_year:
                service_overlap = clamp((service.planned_retirement_year - policy.quantum_horizon_year + 1) / max(1, remaining))
        gaps = _evidence_gaps(component, dep, service)
        gap_pressure = min(1.0, len(gaps) / 4.0)
        score = clamp(
            0.30 * dep.crypto_risk()
            + 0.20 * component.criticality_weight()
            + 0.16 * service_overlap
            + 0.14 * dep.update_friction()
            + 0.10 * component.qualification_weight()
            + 0.10 * gap_pressure
        )
        priority = _priority(score)
        exposure_class = _classify(score, dep, component, service, policy)
        rationale = [
            f"{dep.algorithm} is classified as {dep.risk_label()}",
            f"{component.criticality} component on {component.platform}",
            f"firmware update path is {dep.firmware_update_path}",
        ]
        if service is not None:
            rationale.append(f"service life runs through {service.planned_retirement_year}")
        if gaps:
            rationale.append(f"{len(gaps)} evidence gap(s) increase quarantine pressure")
        payload = {
            "component_id": component.component_id,
            "dependency_id": dep.dependency_id,
            "exposure_class": exposure_class,
            "priority": priority,
            "score": round(score, 4),
        }
        entry_hash = _hash_entry(prev_hash, payload)
        prev_hash = entry_hash
        records.append(
            ExposureRecord(
                component_id=component.component_id,
                dependency_id=dep.dependency_id,
                part_number=component.part_number,
                platform=component.platform,
                algorithm=dep.algorithm,
                risk_label=dep.risk_label(),
                exposure_class=exposure_class,
                quarantine_priority=priority,
                migration_deadline_year=_deadline(policy, dep, service, priority),
                exposure_score=score,
                evidence_gaps=gaps,
                rationale=tuple(rationale),
                entry_hash=entry_hash,
            )
        )
    return tuple(sorted(records, key=lambda item: (-item.exposure_score, item.component_id, item.dependency_id)))


def build_report(
    batch_id: str,
    components: tuple[Component, ...],
    dependencies: tuple[CryptoDependency, ...],
    policy: ServicePolicy,
) -> ExposureReport:
    records = compile_records(batch_id, components, dependencies, policy)
    ledger_head = records[-1].entry_hash if records else hashlib.sha256(batch_id.encode("utf-8")).hexdigest()
    return ExposureReport(batch_id=batch_id, records=records, ledger_head=ledger_head, boundary=dict(BOUNDARY))
