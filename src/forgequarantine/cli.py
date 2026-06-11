"""Command line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from .adapters import load_case, sample_case, write_json
from .compiler import build_report
from .report import render_markdown


def _cmd_sample(args: argparse.Namespace) -> int:
    components, dependencies, service_life = sample_case()
    write_json(args.component_output, components)
    write_json(args.dependencies_output, dependencies)
    write_json(args.service_output, service_life)
    print(f"wrote {args.component_output}")
    print(f"wrote {args.dependencies_output}")
    print(f"wrote {args.service_output}")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    batch_id, components, dependencies, policy = load_case(args.components, args.dependencies, args.service_life)
    report = build_report(batch_id, components, dependencies, policy)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if args.markdown:
        output.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    else:
        write_json(output, report.to_dict() if args.full else report.summary_dict())
    print(f"wrote {output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="forgequarantine")
    sub = parser.add_subparsers(dest="command", required=True)

    sample = sub.add_parser("sample", help="write sample component, crypto, and service-life inputs")
    sample.add_argument("-c", "--component-output", default="examples/component_manifest.json")
    sample.add_argument("-d", "--dependencies-output", default="examples/crypto_dependencies.json")
    sample.add_argument("-s", "--service-output", default="examples/service_life.json")
    sample.set_defaults(func=_cmd_sample)

    run = sub.add_parser("run", help="compile an additive-manufacturing PQC exposure ledger")
    run.add_argument("-c", "--components", required=True, help="component manifest JSON")
    run.add_argument("-d", "--dependencies", required=True, help="crypto dependencies JSON")
    run.add_argument("-s", "--service-life", required=True, help="service life JSON")
    run.add_argument("-o", "--output", required=True)
    run.add_argument("--full", action="store_true", help="write full JSON")
    run.add_argument("--markdown", action="store_true", help="write Markdown")
    run.set_defaults(func=_cmd_run)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))

