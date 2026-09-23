# FastBox Mystery Delivery System

A deterministic Python delivery simulator built for the Nexgensis Technologies
Python Developer assignment. It loads warehouse, agent, and package data,
assigns every package to its nearest agent, simulates the delivery routes, and
writes an efficiency report.

The production application uses only the Python standard library.

## Run the simulator

Python 3.10 or newer is required.

```bash
python main.py test_case_1.json
```

The default output is `report.json`. Custom output and the optional top
performer CSV export are supported:

```bash
python main.py test_case_1.json --output output/report.json \
  --top-performer-csv output/top_performer.csv
```

The committed `report.json` was generated from `base_case (2).json` using the
default deterministic simulation rules documented below.

Run the automated test suite with:

```bash
python -m unittest discover -s tests -v
```

## Report format

Each input agent appears in the report, including agents with no deliveries.
Package IDs are included because the assignment asks the report to show which
packages were delivered.

```json
{
  "A1": {
    "packages_delivered": 2,
    "delivered_package_ids": ["P1", "P4"],
    "total_distance": 121.21,
    "efficiency": 60.61
  },
  "best_agent": "A1"
}
```

Efficiency is the average distance travelled per delivered package, so a lower
value is better.

## Supported input formats

The supplied files contain two different schemas. Both are accepted.

Dictionary format used by `test_case_*.json`:

```json
{
  "warehouses": {"W1": [0, 0]},
  "agents": {"A1": [5, 5]},
  "packages": [
    {"id": "P1", "warehouse": "W1", "destination": [30, 40]}
  ]
}
```

List format used by `base_case (2).json`:

```json
{
  "warehouses": [{"id": "W1", "location": [0, 0]}],
  "agents": [{"id": "A1", "location": [5, 5]}],
  "packages": [
    {"id": "P1", "warehouse_id": "W1", "destination": [30, 40]}
  ]
}
```

## Explicit assumptions

The brief leaves routing order, ties, and some edge cases undefined. The sample
report numbers also do not correspond to the sample coordinates. The following
deterministic assumptions are therefore used:

1. `json` from the Python standard library performs JSON decoding. "Parse
   manually" is interpreted as reading and validating the file directly rather
   than using a dataframe or external data framework.
2. Package assignment uses Euclidean distance from each agent's original
   location to the package's warehouse.
3. All packages are assigned before route simulation begins. Delivery movement
   does not retroactively change assignments.
4. Equal assignment distances are resolved by lexicographically smallest agent
   ID.
5. Each agent delivers assigned packages in their original JSON order.
6. An agent travels from its current location to the warehouse and then to the
   package destination. The destination becomes its current location for the
   next delivery.
7. No return trip is added after an agent's final delivery because the brief
   does not require agents to return to a warehouse or depot.
8. Distances and efficiency are calculated at full precision. Values are
   rounded to two decimal places only when the report is serialized.
9. Agents with zero deliveries have `efficiency: null` and are excluded from
   best-agent selection. If there are no deliveries, `best_agent` is `null`.
10. Equal efficiency is resolved by lexicographically smallest agent ID.

## Validation

The loader rejects malformed inputs with a concise error, including duplicate
IDs or JSON keys, missing fields, invalid coordinates, packages referencing an
unknown warehouse, and packages supplied without an agent.

## Project structure

```text
main.py                       Command-line interface
delivery_system/models.py     Immutable domain models
delivery_system/parser.py     Dual-schema normalization and validation
delivery_system/assignment.py Euclidean assignment logic
delivery_system/simulation.py Stateful route simulation
delivery_system/reporting.py  JSON report and optional CSV export
tests/                        Unit and integration tests
```

## Complexity

For `P` packages and `A` agents, assignment is `O(P * A)`. Simulation and
report generation are `O(P + A)`. The in-memory representation uses
`O(P + A + W)` space for packages, agents, and warehouses.
