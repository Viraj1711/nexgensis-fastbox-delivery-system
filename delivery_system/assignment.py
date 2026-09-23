"""Package-to-agent assignment logic."""

from __future__ import annotations

import math

from .models import InputData, Package, Point


def euclidean_distance(first: Point, second: Point) -> float:
    """Return straight-line distance between two Cartesian coordinates."""
    return math.hypot(first[0] - second[0], first[1] - second[1])


def assign_packages(data: InputData) -> dict[str, list[Package]]:
    """Assign each package to the nearest agent using original locations.

    Packages remain in input order. Equal-distance ties are resolved by agent ID.
    """
    assignments = {agent.id: [] for agent in data.agents}
    warehouses = data.warehouses_by_id

    for package in data.packages:
        warehouse_location = warehouses[package.warehouse_id].location
        nearest_agent = min(
            data.agents,
            key=lambda agent: (
                euclidean_distance(agent.location, warehouse_location),
                agent.id,
            ),
        )
        assignments[nearest_agent.id].append(package)

    return assignments
