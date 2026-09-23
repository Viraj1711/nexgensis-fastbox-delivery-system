from __future__ import annotations

import json
import unittest
from pathlib import Path

from delivery_system.assignment import assign_packages
from delivery_system.parser import load_input
from delivery_system.reporting import build_report
from delivery_system.simulation import simulate_day
from main import main


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = [
    ROOT / "data" / "base_case.json",
    *sorted((ROOT / "data" / "test_cases").glob("test_case_*.json")),
]
EXPECTED_ASSIGNMENT_COUNTS = {
    "base_case.json": {"A1": 2, "A2": 2, "A3": 1},
    "test_case_1.json": {"A1": 4, "A2": 1, "A3": 7, "A4": 0},
    "test_case_2.json": {"A1": 10, "A2": 0, "A3": 0},
    "test_case_3.json": {"A1": 0, "A2": 2, "A3": 3, "A4": 1},
    "test_case_4.json": {"A1": 3, "A2": 4, "A3": 5, "A4": 0, "A5": 0},
    "test_case_5.json": {"A1": 0, "A2": 0, "A3": 7, "A4": 3, "A5": 0},
    "test_case_6.json": {"A1": 1, "A2": 0, "A3": 4, "A4": 4},
    "test_case_7.json": {"A1": 0, "A2": 1, "A3": 6, "A4": 3},
    "test_case_8.json": {"A1": 1, "A2": 10, "A3": 0, "A4": 0},
    "test_case_9.json": {"A1": 6, "A2": 0, "A3": 2, "A4": 0},
    "test_case_10.json": {"A1": 0, "A2": 2, "A3": 3, "A4": 6},
}


class IntegrationTests(unittest.TestCase):
    def test_every_supplied_fixture_delivers_every_package_once(self) -> None:
        for path in FIXTURES:
            with self.subTest(path=path.name):
                data = load_input(path)
                report = build_report(data, simulate_day(data, assign_packages(data)))
                agent_rows = [report[agent.id] for agent in data.agents]
                delivered_ids = [
                    package_id
                    for row in agent_rows
                    for package_id in row["delivered_package_ids"]
                ]
                self.assertCountEqual(delivered_ids, [package.id for package in data.packages])
                self.assertEqual(
                    sum(row["packages_delivered"] for row in agent_rows),
                    len(data.packages),
                )
                self.assertTrue(
                    all(row["total_distance"] >= 0 for row in agent_rows)
                )
                self.assertEqual(
                    {
                        agent.id: report[agent.id]["packages_delivered"]
                        for agent in data.agents
                    },
                    EXPECTED_ASSIGNMENT_COUNTS[path.name],
                )

    def test_cli_writes_parseable_report_and_bonus_csv(self) -> None:
        report_path = ROOT / "tests" / "_integration_report.json"
        csv_path = ROOT / "tests" / "_integration_best.csv"
        try:
            exit_code = main(
                [
                    str(ROOT / "data" / "test_cases" / "test_case_1.json"),
                    "--output",
                    str(report_path),
                    "--top-performer-csv",
                    str(csv_path),
                ]
            )
            self.assertEqual(exit_code, 0)
            parsed = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(
                sum(parsed[agent]["packages_delivered"] for agent in ("A1", "A2", "A3", "A4")),
                12,
            )
            self.assertIn("agent_id,packages_delivered,total_distance,efficiency", csv_path.read_text(encoding="utf-8"))
        finally:
            report_path.unlink(missing_ok=True)
            csv_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
