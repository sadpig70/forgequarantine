"""Domain models."""

from __future__ import annotations

from dataclasses import dataclass


CRITICALITY_WEIGHT = {
    "low": 0.20,
    "standard": 0.35,
    "mission": 0.62,
    "mission_critical": 0.72,
    "flight_critical": 0.90,
    "safety_critical": 1.00,
}

QUALIFICATION_WEIGHT = {
    "prototype": 0.20,
    "qualified": 0.45,
    "flight_qualified": 0.75,
    "safety_certified": 0.90,
    "defense_certified": 1.00,
}

ALGORITHM_RISK = {
    "rsa": ("quantum_broken", 1.00),
    "ecdsa": ("quantum_broken", 1.00),
    "ecdh": ("quantum_broken", 1.00),
    "dh": ("quantum_broken", 0.95),
    "dsa": ("quantum_broken", 0.95),
    "sha1": ("classically_broken", 0.95),
    "md5": ("classically_broken", 1.00),
    "aes-128": ("quantum_weakened", 0.52),
    "aes128": ("quantum_weakened", 0.52),
    "aes-256": ("symmetric_resilient", 0.20),
    "aes256": ("symmetric_resilient", 0.20),
    "sha256": ("symmetric_resilient", 0.18),
    "sha384": ("symmetric_resilient", 0.16),
    "sha512": ("symmetric_resilient", 0.16),
    "ml-kem": ("pqc_ready", 0.04),
    "ml-dsa": ("pqc_ready", 0.04),
    "slh-dsa": ("pqc_ready", 0.04),
}


@dataclass(frozen=True)
class Component:
    component_id: str
    part_number: str
    platform: str
    criticality: str
    qualification_level: str
    print_process: str
    material: str
    deployment_environment: str
    evidence_refs: tuple[str, ...]

    def criticality_weight(self) -> float:
        return CRITICALITY_WEIGHT.get(self.criticality, 0.45)

    def qualification_weight(self) -> float:
        return QUALIFICATION_WEIGHT.get(self.qualification_level, 0.45)


@dataclass(frozen=True)
class CryptoDependency:
    dependency_id: str
    component_id: str
    algorithm: str
    use_case: str
    key_length: int
    firmware_update_path: str
    crypto_agility: bool
    evidence_refs: tuple[str, ...]

    def risk_label(self) -> str:
        return ALGORITHM_RISK.get(self.algorithm.lower(), ("unknown_crypto", 0.65))[0]

    def crypto_risk(self) -> float:
        return ALGORITHM_RISK.get(self.algorithm.lower(), ("unknown_crypto", 0.65))[1]

    def update_friction(self) -> float:
        if self.crypto_agility and self.firmware_update_path in {"field_update", "ota"}:
            return 0.15
        if self.firmware_update_path == "depot_update":
            return 0.42 if self.crypto_agility else 0.58
        if self.firmware_update_path == "vendor_return":
            return 0.72
        if self.firmware_update_path == "no_update":
            return 1.0
        return 0.55


@dataclass(frozen=True)
class ServiceLife:
    component_id: str
    in_service_year: int
    planned_retirement_year: int
    replacement_lead_months: int
    inspection_interval_months: int
    evidence_refs: tuple[str, ...]

    def remaining_years(self, current_year: int) -> int:
        return max(0, self.planned_retirement_year - current_year)


@dataclass(frozen=True)
class ServicePolicy:
    current_year: int
    quantum_horizon_year: int
    default_lead_months: int
    service_lives: tuple[ServiceLife, ...]

    def service_map(self) -> dict[str, ServiceLife]:
        return {item.component_id: item for item in self.service_lives}


@dataclass(frozen=True)
class ExposureRecord:
    component_id: str
    dependency_id: str
    part_number: str
    platform: str
    algorithm: str
    risk_label: str
    exposure_class: str
    quarantine_priority: str
    migration_deadline_year: int
    exposure_score: float
    evidence_gaps: tuple[str, ...]
    rationale: tuple[str, ...]
    entry_hash: str

    def to_dict(self) -> dict:
        return {
            "component_id": self.component_id,
            "dependency_id": self.dependency_id,
            "part_number": self.part_number,
            "platform": self.platform,
            "algorithm": self.algorithm,
            "risk_label": self.risk_label,
            "exposure_class": self.exposure_class,
            "quarantine_priority": self.quarantine_priority,
            "migration_deadline_year": self.migration_deadline_year,
            "exposure_score": round(self.exposure_score, 4),
            "evidence_gaps": list(self.evidence_gaps),
            "rationale": list(self.rationale),
            "entry_hash": self.entry_hash,
        }


@dataclass(frozen=True)
class ExposureReport:
    batch_id: str
    records: tuple[ExposureRecord, ...]
    ledger_head: str
    boundary: dict

    def summary_dict(self) -> dict:
        return {
            "batch_id": self.batch_id,
            "record_count": len(self.records),
            "urgent_count": sum(1 for record in self.records if record.quarantine_priority == "urgent"),
            "ledger_head": self.ledger_head,
            "top_records": [record.to_dict() for record in self.records[:5]],
            "cross_model_certified": self.boundary["cross_model_certified"],
        }

    def to_dict(self) -> dict:
        data = self.summary_dict()
        data["boundary"] = dict(self.boundary)
        data["records"] = [record.to_dict() for record in self.records]
        return data

