"""Domain models used by the delivery simulator."""

from __future__ import annotations

from dataclasses import dataclass

Point = tuple[float, float]


@dataclass(frozen=True, slots=True)
class Warehouse:
    id: str
    location: Point


@dataclass(frozen=True, slots=True)
class Agent:
    id: str
    location: Point


@dataclass(frozen=True, slots=True)
class Package:
    id: str
    warehouse_id: str
    destination: Point


@dataclass(frozen=True, slots=True)
class InputData:
    warehouses: tuple[Warehouse, ...]
    agents: tuple[Agent, ...]
    packages: tuple[Package, ...]

    @property
    def warehouses_by_id(self) -> dict[str, Warehouse]:
        return {warehouse.id: warehouse for warehouse in self.warehouses}


@dataclass(frozen=True, slots=True)
class Delivery:
    package_id: str
    warehouse_id: str
    start: Point
    warehouse: Point
    destination: Point
    pickup_distance: float
    delivery_distance: float

    @property
    def distance(self) -> float:
        return self.pickup_distance + self.delivery_distance


@dataclass(frozen=True, slots=True)
class AgentResult:
    agent_id: str
    deliveries: tuple[Delivery, ...]
    total_distance: float

    @property
    def packages_delivered(self) -> int:
        return len(self.deliveries)

    @property
    def efficiency(self) -> float | None:
        if not self.deliveries:
            return None
        return self.total_distance / len(self.deliveries)
