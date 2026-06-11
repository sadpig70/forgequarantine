from forgequarantine.adapters import parse_components, parse_dependencies, parse_service_policy, sample_case
from forgequarantine.compiler import build_report, compile_records


def _sample_models():
    components_data, dependencies_data, service_data = sample_case()
    batch_id, components = parse_components(components_data)
    return batch_id, components, parse_dependencies(dependencies_data), parse_service_policy(service_data)


def test_flight_critical_ecdsa_no_update_is_top_urgent():
    batch_id, components, dependencies, policy = _sample_models()
    records = compile_records(batch_id, components, dependencies, policy)

    assert records[0].component_id == "CMP-AX9"
    assert records[0].risk_label == "quantum_broken"
    assert records[0].quarantine_priority == "urgent"
    assert records[0].exposure_class == "service_life_crypto_quarantine"


def test_pqc_ready_or_strong_symmetric_is_not_urgent():
    batch_id, components, dependencies, policy = _sample_models()
    records = {item.dependency_id: item for item in compile_records(batch_id, components, dependencies, policy)}

    assert records["CRY-LAB-DATA"].quarantine_priority in {"archive", "monitor"}
    assert records["CRY-LAB-DATA"].migration_deadline_year >= 2029


def test_missing_evidence_creates_gaps():
    batch_id, components, dependencies, policy = _sample_models()
    records = {item.dependency_id: item for item in compile_records(batch_id, components, dependencies, policy)}

    assert "missing component qualification evidence" in records["CRY-LAB-DATA"].evidence_gaps
    assert "missing crypto dependency evidence" in records["CRY-LAB-DATA"].evidence_gaps


def test_report_boundary_marks_sa_not_certified():
    batch_id, components, dependencies, policy = _sample_models()
    report = build_report(batch_id, components, dependencies, policy)

    assert report.boundary["source_round"] == "SA-EVX-20260611-001"
    assert report.boundary["source_candidate"] == "ForgeQuarantine"
    assert report.summary_dict()["cross_model_certified"] is False


def test_ledger_head_is_hash_like():
    batch_id, components, dependencies, policy = _sample_models()
    report = build_report(batch_id, components, dependencies, policy)

    assert len(report.ledger_head) == 64
    assert all(len(item.entry_hash) == 64 for item in report.records)

