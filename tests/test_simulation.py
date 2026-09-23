from __future__ import annotations

import math
import unittest
from pathlib import Path

from delivery_system.assignment import assign_packages
from delivery_system.parser import load_input, normalize_data
from delivery_system.reporting import build_report
from delivery_system.simulation import simulate_day


ROOT = Path(__file__).resolve().parents[1]


class SimulationTests(unittest.TestCase):
    def test_agent_position_updates_between_deliveries(self) -> None:
        data = normalize_data(
            {
                "warehouses": {"W1": [0, 0]},
                "agents": {"A1": [3, 4]},
                "packages": [
                    {"id": "P1", "warehouse": "W1", "destination": [0, 4]},
                    {"id": "P2", "warehouse": "W1", "destination": [3, 0]},
                ],
            }
        )
        results = simulate_day(data, assign_packages(data))
        self.assertEqual(results["A1"].total_distance, 16.0)
        self.assertEqual(results["A1"].deliveries[1].start, (0.0, 4.0))

    def test_base_case_distances(self) -> None:
        data = load_input(ROOT / "data" / "base_case.json")
        results = simulate_day(data, assign_packages(data))
        self.assertTrue(math.isclose(results["A1"].total_distance, 121.2132034356))
        self.assertTrue(math.isclose(results["A2"].total_distance, 79.2080962648))
        self.assertTrue(math.isclose(results["A3"].total_distance, 14.1421356237))

    def test_zero_delivery_agent_and_best_agent(self) -> None:
        data = normalize_data(
            {
                "warehouses": {"W1": [0, 0]},
                "agents": {"A1": [0, 0], "A2": [100, 100]},
                "packages": [
                    {"id": "P1", "warehouse": "W1", "destination": [3, 4]}
                ],
            }
        )
        results = simulate_day(data, assign_packages(data))
        report = build_report(data, results)
        self.assertEqual(report["A2"]["packages_delivered"], 0)
        self.assertIsNone(report["A2"]["efficiency"])
        self.assertEqual(report["best_agent"], "A1")

    def test_no_packages_has_no_best_agent(self) -> None:
        data = normalize_data(
            {"warehouses": {}, "agents": {"A1": [0, 0]}, "packages": []}
        )
        report = build_report(data, simulate_day(data, assign_packages(data)))
        self.assertIsNone(report["best_agent"])


if __name__ == "__main__":
    unittest.main()
