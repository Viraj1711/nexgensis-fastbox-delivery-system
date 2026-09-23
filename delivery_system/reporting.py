"""Build and persist simulator reports."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .models import AgentResult, InputData


def build_report(
    data: InputData,
    results: dict[str, AgentResult],
) -> dict[str, Any]:
    """Create the JSON-compatible report shape requested in the assignment."""
    report: dict[str, Any] = {}

    for agent in data.agents:
        result = results[agent.id]
        report[agent.id] = {
            "packages_delivered": result.packages_delivered,
            "delivered_package_ids": [
                delivery.package_id for delivery in result.deliveries
            ],
            "total_distance": round(result.total_distance, 2),
            "efficiency": (
                round(result.efficiency, 2)
                if result.efficiency is not None
                else None
            ),
        }

    eligible = [result for result in results.values() if result.efficiency is not None]
    best = min(
        eligible,
        key=lambda result: (result.efficiency, result.agent_id),
        default=None,
    )
    report["best_agent"] = best.agent_id if best else None
    return report


def write_report(report: dict[str, Any], path: str | Path) -> None:
    """Write a human-readable, standards-compliant JSON report."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def write_top_performer_csv(report: dict[str, Any], path: str | Path) -> None:
    """Export the best agent as the assignment's optional CSV bonus."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    best_agent = report.get("best_agent")

    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=(
                "agent_id",
                "packages_delivered",
                "total_distance",
                "efficiency",
            ),
        )
        writer.writeheader()
        if best_agent is not None:
            details = report[best_agent]
            writer.writerow(
                {
                    "agent_id": best_agent,
                    "packages_delivered": details["packages_delivered"],
                    "total_distance": details["total_distance"],
                    "efficiency": details["efficiency"],
                }
            )
