"""Deterministic delivery route simulation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from .assignment import euclidean_distance
from .models import AgentResult, Delivery, InputData, Package


def simulate_day(
    data: InputData,
    assignments: Mapping[str, Sequence[Package]],
) -> dict[str, AgentResult]:
    """Simulate assigned deliveries in package input order.

    An agent's current position changes to the destination after each delivery.
    """
    warehouses = data.warehouses_by_id
    results: dict[str, AgentResult] = {}

    for agent in data.agents:
        current_location = agent.location
        deliveries: list[Delivery] = []
        total_distance = 0.0

        for package in assignments.get(agent.id, ()):
            warehouse_location = warehouses[package.warehouse_id].location
            pickup_distance = euclidean_distance(current_location, warehouse_location)
            delivery_distance = euclidean_distance(
                warehouse_location, package.destination
            )
            delivery = Delivery(
                package_id=package.id,
                warehouse_id=package.warehouse_id,
                start=current_location,
                warehouse=warehouse_location,
                destination=package.destination,
                pickup_distance=pickup_distance,
                delivery_distance=delivery_distance,
            )
            deliveries.append(delivery)
            total_distance += delivery.distance
            current_location = package.destination

        results[agent.id] = AgentResult(
            agent_id=agent.id,
            deliveries=tuple(deliveries),
            total_distance=total_distance,
        )

    return results
