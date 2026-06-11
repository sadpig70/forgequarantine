"""Markdown report renderer."""

from __future__ import annotations

from .models import ExposureReport


def render_markdown(report: ExposureReport) -> str:
    lines = [
        f"# ForgeQuarantine Report: {report.batch_id}",
        "",
        f"- Records: `{len(report.records)}`",
        f"- Urgent: `{sum(1 for item in report.records if item.quarantine_priority == 'urgent')}`",
        f"- Ledger head: `{report.ledger_head}`",
        f"- Cross-model certified: `{str(report.boundary['cross_model_certified']).lower()}`",
        f"- Source round: `{report.boundary['source_round']}`",
        "",
        "## Exposure Ledger",
        "",
    ]
    for record in report.records:
        lines.extend(
            [
                f"### {record.component_id} / {record.dependency_id}",
                "",
                f"- Part: `{record.part_number}`",
                f"- Platform: `{record.platform}`",
                f"- Algorithm: `{record.algorithm}` (`{record.risk_label}`)",
                f"- Exposure class: `{record.exposure_class}`",
                f"- Quarantine priority: `{record.quarantine_priority}`",
                f"- Migration deadline year: `{record.migration_deadline_year}`",
                f"- Score: `{record.exposure_score:.3f}`",
                f"- Entry hash: `{record.entry_hash}`",
            ]
        )
        if record.evidence_gaps:
            lines.append("- Evidence gaps:")
            lines.extend(f"  - {gap}" for gap in record.evidence_gaps)
        lines.append("- Rationale:")
        lines.extend(f"  - {reason}" for reason in record.rationale)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"

