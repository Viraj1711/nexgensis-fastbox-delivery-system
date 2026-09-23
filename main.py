"""Command-line entry point for the FastBox delivery simulator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from delivery_system import (
    InputValidationError,
    assign_packages,
    build_report,
    load_input,
    simulate_day,
    write_report,
    write_top_performer_csv,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Assign and simulate FastBox package deliveries."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="data.json",
        help="Input JSON path (default: data.json)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="report.json",
        help="Report JSON path (default: report.json)",
    )
    parser.add_argument(
        "--top-performer-csv",
        metavar="PATH",
        help="Optionally export the best agent to CSV",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = load_input(args.input)
        assignments = assign_packages(data)
        results = simulate_day(data, assignments)
        report = build_report(data, results)
        write_report(report, args.output)
        if args.top_performer_csv:
            write_top_performer_csv(report, args.top_performer_csv)
    except (InputValidationError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(
        f"Delivered {len(data.packages)} package(s). "
        f"Best agent: {report['best_agent'] or 'N/A'}. "
        f"Report: {Path(args.output)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
