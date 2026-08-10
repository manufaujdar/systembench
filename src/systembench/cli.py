"""Command-line entry point."""

from __future__ import annotations

import argparse
from pathlib import Path

from .comparison import RegressionPolicy, compare_reports
from .demo import DemoSystem
from .evaluators import default_evaluators
from .integrity import strict_json_dumps
from .io import load_json_object, load_report, load_suite, write_report
from .runner import BenchmarkRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="systembench", description="Benchmark an AI system")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", help="run a benchmark suite")
    run.add_argument("suite", help="path to a suite JSON file")
    run.add_argument("--trials", type=int, default=1, help="repeat each scenario N times")
    run.add_argument("--seed", type=int, default=0)
    run.add_argument("--bootstrap-samples", type=int, default=2000)
    run.add_argument("--bootstrap-seed", type=int)
    run.add_argument("--confidence-level", type=float, default=0.95)
    run.add_argument("--system-manifest", help="strict JSON declaration of the system release")
    run.add_argument("--budget-manifest", help="strict JSON declaration of additional budgets")
    run.add_argument("--accounting-manifest", help="strict JSON declaration of accounting rules")
    run.add_argument("--output", default="runs", help="report output directory")
    run.add_argument("--json", action="store_true", help="print the summary as JSON")

    compare = subparsers.add_parser("compare", help="compare matched baseline and candidate reports")
    compare.add_argument("baseline", help="path to the pinned baseline report")
    compare.add_argument("candidate", help="path to the candidate report")
    compare.add_argument("--max-pass-rate-drop", type=float, default=0.0)
    compare.add_argument("--max-error-rate-increase", type=float, default=0.0)
    compare.add_argument("--max-mean-latency-increase-ms", type=float)
    compare.add_argument("--max-mean-cost-increase-usd", type=float)
    compare.add_argument("--bootstrap-samples", type=int, default=2000)
    compare.add_argument("--bootstrap-seed", type=int, default=0)
    compare.add_argument("--confidence-level", type=float, default=0.95)
    compare.add_argument("--output", help="optional path for the comparison JSON")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "run":
        suite = load_suite(args.suite)
        report = BenchmarkRunner(DemoSystem(), default_evaluators()).run(
            suite,
            trials=args.trials,
            seed=args.seed,
            bootstrap_samples=args.bootstrap_samples,
            confidence_level=args.confidence_level,
            bootstrap_seed=args.bootstrap_seed,
            system_manifest=(
                load_json_object(args.system_manifest, "system manifest")
                if args.system_manifest
                else None
            ),
            budget_manifest=(
                load_json_object(args.budget_manifest, "budget manifest")
                if args.budget_manifest
                else None
            ),
            accounting_manifest=(
                load_json_object(args.accounting_manifest, "accounting manifest")
                if args.accounting_manifest
                else None
            ),
        )
        path = write_report(report, args.output)
        summary = report["summary"]
        if args.json:
            print(strict_json_dumps(summary, indent=2))
        else:
            print(f"Run: {report['run_id']}")
            print(f"Pass rate: {summary['pass_rate']:.1%}")
            print(f"Mean latency: {summary['mean_latency_ms']:.2f} ms")
            print(f"Report: {path}")
    elif args.command == "compare":
        comparison = compare_reports(
            load_report(args.baseline),
            load_report(args.candidate),
            policy=RegressionPolicy(
                max_pass_rate_drop=args.max_pass_rate_drop,
                max_error_rate_increase=args.max_error_rate_increase,
                max_mean_latency_increase_ms=args.max_mean_latency_increase_ms,
                max_mean_cost_increase_usd=args.max_mean_cost_increase_usd,
            ),
            bootstrap_samples=args.bootstrap_samples,
            confidence_level=args.confidence_level,
            bootstrap_seed=args.bootstrap_seed,
        )
        rendered = strict_json_dumps(comparison, indent=2)
        if args.output:
            Path(args.output).write_text(rendered + "\n", encoding="utf-8")
        print(rendered)
        if not comparison["passed"]:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
