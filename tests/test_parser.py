from __future__ import annotations

import unittest
from pathlib import Path

from delivery_system.parser import InputValidationError, load_input, normalize_data


ROOT = Path(__file__).resolve().parents[1]


class ParserTests(unittest.TestCase):
    def test_loads_list_schema(self) -> None:
        data = load_input(ROOT / "base_case (2).json")
        self.assertEqual([item.id for item in data.warehouses], ["W1", "W2", "W3"])
        self.assertEqual(data.packages[0].warehouse_id, "W1")

    def test_loads_mapping_schema(self) -> None:
        data = load_input(ROOT / "test_case_1.json")
        self.assertEqual(len(data.warehouses), 5)
        self.assertEqual(data.packages[0].warehouse_id, "W5")

    def test_rejects_unknown_warehouse(self) -> None:
        raw = {
            "warehouses": {"W1": [0, 0]},
            "agents": {"A1": [1, 1]},
            "packages": [
                {"id": "P1", "warehouse": "missing", "destination": [2, 2]}
            ],
        }
        with self.assertRaisesRegex(InputValidationError, "unknown warehouse"):
            normalize_data(raw)

    def test_rejects_bad_coordinate(self) -> None:
        raw = {"warehouses": {"W1": [0]}, "agents": {}, "packages": []}
        with self.assertRaisesRegex(InputValidationError, "exactly two"):
            normalize_data(raw)

    def test_rejects_packages_without_agents(self) -> None:
        raw = {
            "warehouses": {"W1": [0, 0]},
            "agents": {},
            "packages": [
                {"id": "P1", "warehouse": "W1", "destination": [1, 1]}
            ],
        }
        with self.assertRaisesRegex(InputValidationError, "At least one agent"):
            normalize_data(raw)


if __name__ == "__main__":
    unittest.main()
