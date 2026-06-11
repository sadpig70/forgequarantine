"""JSON adapters and bundled sample data."""

from __future__ import annotations

import json
from pathlib import Path

from .models import Component, CryptoDependency, ServiceLife, ServicePolicy
from .validate import require_list, require_mapping, require_text


def _text_tuple(value: object, name: str) -> tuple[str, ...]:
    return tuple(require_text(item, f"{name}[]") for item in require_list(value, name))


def parse_components(data: object) -> tuple[str, tuple[Component, ...]]:
    root = require_mapping(data, "component_manifest")
    batch_id = require_text(root.get("batch_id"), "batch_id")
    components = []
    for row in require_list(root.get("components"), "components"):
        item = require_mapping(row, "component")
        components.append(
            Component(
                component_id=require_text(item.get("component_id"), "component_id"),
                part_number=require_text(item.get("part_number"), "part_number"),
                platform=require_text(item.get("platform"), "platform"),
                criticality=str(item.get("criticality", "standard")).strip() or "standard",
                qualification_level=str(item.get("qualification_level", "qualified")).strip() or "qualified",
                print_process=str(item.get("print_process", "unknown")).strip() or "unknown",
                material=str(item.get("material", "unknown")).strip() or "unknown",
                deployment_environment=str(item.get("deployment_environment", "unknown")).strip() or "unknown",
                evidence_refs=_text_tuple(item.get("evidence_refs", []), "evidence_refs"),
            )
        )
    return batch_id, tuple(components)


def parse_dependencies(data: object) -> tuple[CryptoDependency, ...]:
    root = require_mapping(data, "crypto_dependencies")
    dependencies = []
    for row in require_list(root.get("dependencies"), "dependencies"):
        item = require_mapping(row, "dependency")
        dependencies.append(
            CryptoDependency(
                dependency_id=require_text(item.get("dependency_id"), "dependency_id"),
                component_id=require_text(item.get("component_id"), "component_id"),
                algorithm=require_text(item.get("algorithm"), "algorithm"),
                use_case=str(item.get("use_case", "unknown")).strip() or "unknown",
                key_length=int(item.get("key_length", 0)),
                firmware_update_path=str(item.get("firmware_update_path", "unknown")).strip() or "unknown",
                crypto_agility=bool(item.get("crypto_agility", False)),
                evidence_refs=_text_tuple(item.get("evidence_refs", []), "evidence_refs"),
            )
        )
    return tuple(dependencies)


def parse_service_policy(data: object) -> ServicePolicy:
    root = require_mapping(data, "service_life")
    profiles = []
    for row in require_list(root.get("service_profiles"), "service_profiles"):
        item = require_mapping(row, "service_profile")
        profiles.append(
            ServiceLife(
                component_id=require_text(item.get("component_id"), "component_id"),
                in_service_year=int(item.get("in_service_year", 0)),
                planned_retirement_year=int(item.get("planned_retirement_year", 0)),
                replacement_lead_months=int(item.get("replacement_lead_months", root.get("default_lead_months", 18))),
                inspection_interval_months=int(item.get("inspection_interval_months", 12)),
                evidence_refs=_text_tuple(item.get("evidence_refs", []), "evidence_refs"),
            )
        )
    return ServicePolicy(
        current_year=int(root.get("current_year", 2026)),
        quantum_horizon_year=int(root.get("quantum_horizon_year", 2032)),
        default_lead_months=int(root.get("default_lead_months", 18)),
        service_lives=tuple(profiles),
    )


def load_json(path: str | Path) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_case(
    component_path: str | Path, dependency_path: str | Path, service_path: str | Path
) -> tuple[str, tuple[Component, ...], tuple[CryptoDependency, ...], ServicePolicy]:
    batch_id, components = parse_components(load_json(component_path))
    return batch_id, components, parse_dependencies(load_json(dependency_path)), parse_service_policy(load_json(service_path))


def write_json(path: str | Path, data: object) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def sample_case() -> tuple[dict, dict, dict]:
    components = {
        "batch_id": "FQ-AM-2026-06",
        "components": [
            {
                "component_id": "CMP-AX9",
                "part_number": "AM-TVC-AX9",
                "platform": "orbital transfer vehicle",
                "criticality": "flight_critical",
                "qualification_level": "flight_qualified",
                "print_process": "laser_powder_bed_fusion",
                "material": "titanium-alloy",
                "deployment_environment": "radiation_vacuum",
                "evidence_refs": ["qual-report-AX9", "ndt-scan-AX9"],
            },
            {
                "component_id": "CMP-MR2",
                "part_number": "AM-MOUNT-MR2",
                "platform": "defense radar pod",
                "criticality": "mission_critical",
                "qualification_level": "defense_certified",
                "print_process": "directed_energy_deposition",
                "material": "inconel",
                "deployment_environment": "salt_fog_vibration",
                "evidence_refs": ["qual-report-MR2"],
            },
            {
                "component_id": "CMP-LAB",
                "part_number": "AM-LAB-BRACKET",
                "platform": "ground test rig",
                "criticality": "standard",
                "qualification_level": "prototype",
                "print_process": "binder_jet",
                "material": "steel",
                "deployment_environment": "lab",
                "evidence_refs": [],
            },
        ],
    }
    dependencies = {
        "dependencies": [
            {
                "dependency_id": "CRY-AX9-BOOT",
                "component_id": "CMP-AX9",
                "algorithm": "ECDSA",
                "use_case": "secure_boot_signature",
                "key_length": 256,
                "firmware_update_path": "no_update",
                "crypto_agility": False,
                "evidence_refs": ["sbom-AX9", "boot-chain-AX9"],
            },
            {
                "dependency_id": "CRY-MR2-LINK",
                "component_id": "CMP-MR2",
                "algorithm": "RSA",
                "use_case": "maintenance_channel",
                "key_length": 2048,
                "firmware_update_path": "depot_update",
                "crypto_agility": True,
                "evidence_refs": ["crypto-sbom-MR2"],
            },
            {
                "dependency_id": "CRY-LAB-DATA",
                "component_id": "CMP-LAB",
                "algorithm": "AES-256",
                "use_case": "test_data_at_rest",
                "key_length": 256,
                "firmware_update_path": "field_update",
                "crypto_agility": True,
                "evidence_refs": [],
            },
        ]
    }
    service_life = {
        "current_year": 2026,
        "quantum_horizon_year": 2032,
        "default_lead_months": 18,
        "service_profiles": [
            {
                "component_id": "CMP-AX9",
                "in_service_year": 2028,
                "planned_retirement_year": 2042,
                "replacement_lead_months": 36,
                "inspection_interval_months": 6,
                "evidence_refs": ["fleet-plan-AX9"],
            },
            {
                "component_id": "CMP-MR2",
                "in_service_year": 2027,
                "planned_retirement_year": 2036,
                "replacement_lead_months": 24,
                "inspection_interval_months": 12,
                "evidence_refs": ["depot-plan-MR2"],
            },
            {
                "component_id": "CMP-LAB",
                "in_service_year": 2026,
                "planned_retirement_year": 2029,
                "replacement_lead_months": 6,
                "inspection_interval_months": 18,
                "evidence_refs": [],
            },
        ],
    }
    return components, dependencies, service_life

