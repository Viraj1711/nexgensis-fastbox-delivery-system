from __future__ import annotations

import unittest
from pathlib import Path

from delivery_system.assignment import assign_packages, euclidean_distance
from delivery_system.parser import load_input, normalize_data


ROOT = Path(__file__).resolve().parents[1]


class AssignmentTests(unittest.TestCase):
    def test_euclidean_distance(self) -> None:
        self.assertEqual(euclidean_distance((0.0, 0.0), (3.0, 4.0)), 5.0)

    def test_base_case_assignments(self) -> None:
        data = load_input(ROOT / "data" / "base_case.json")
        assignments = assign_packages(data)
        actual = {
            agent_id: [package.id for package in packages]
            for agent_id, packages in assignments.items()
        }
        self.assertEqual(
            actual,
            {"A1": ["P1", "P4"], "A2": ["P2", "P5"], "A3": ["P3"]},
        )

    def test_tie_uses_lexicographically_smallest_agent_id(self) -> None:
        data = normalize_data(
            {
                "warehouses": {"W1": [0, 0]},
                "agents": {"A2": [1, 0], "A1": [-1, 0]},
                "packages": [
                    {"id": "P1", "warehouse": "W1", "destination": [0, 1]}
                ],
            }
        )
        assignments = assign_packages(data)
        self.assertEqual([package.id for package in assignments["A1"]], ["P1"])
        self.assertEqual(assignments["A2"], [])


if __name__ == "__main__":
    unittest.main()
