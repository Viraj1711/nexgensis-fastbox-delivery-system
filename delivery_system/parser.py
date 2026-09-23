"""Read, normalize, and validate FastBox JSON input."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .models import Agent, InputData, Package, Point, Warehouse


class InputValidationError(ValueError):
    """Raised when an input file is valid JSON but invalid FastBox data."""


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InputValidationError(f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _require_id(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputValidationError(f"{context} must be a non-empty string")
    return value


def _parse_point(value: Any, context: str) -> Point:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise InputValidationError(f"{context} must contain exactly two coordinates")

    coordinates: list[float] = []
    for coordinate in value:
        if isinstance(coordinate, bool) or not isinstance(coordinate, (int, float)):
            raise InputValidationError(f"{context} coordinates must be numbers")
        number = float(coordinate)
        if not math.isfinite(number):
            raise InputValidationError(f"{context} coordinates must be finite")
        coordinates.append(number)
    return coordinates[0], coordinates[1]


def _normalize_locations(
    value: Any,
    collection_name: str,
    model_type: type[Warehouse] | type[Agent],
) -> tuple[Warehouse, ...] | tuple[Agent, ...]:
    normalized: list[Warehouse | Agent] = []

    if isinstance(value, dict):
        entries = value.items()
    elif isinstance(value, list):
        converted_entries: list[tuple[Any, Any]] = []
        for index, item in enumerate(value):
            if not isinstance(item, dict):
                raise InputValidationError(
                    f"{collection_name}[{index}] must be an object"
                )
            if "id" not in item or "location" not in item:
                raise InputValidationError(
                    f"{collection_name}[{index}] requires 'id' and 'location'"
                )
            converted_entries.append((item["id"], item["location"]))
        entries = converted_entries
    else:
        raise InputValidationError(
            f"'{collection_name}' must be either an object or a list"
        )

    seen_ids: set[str] = set()
    for raw_id, raw_location in entries:
        entity_id = _require_id(raw_id, f"{collection_name} ID")
        if entity_id in seen_ids:
            raise InputValidationError(
                f"Duplicate {collection_name} ID: {entity_id!r}"
            )
        seen_ids.add(entity_id)
        location = _parse_point(raw_location, f"{collection_name} {entity_id!r} location")
        normalized.append(model_type(entity_id, location))

    return tuple(normalized)


def _normalize_packages(value: Any, warehouse_ids: set[str]) -> tuple[Package, ...]:
    if not isinstance(value, list):
        raise InputValidationError("'packages' must be a list")

    packages: list[Package] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(value):
        context = f"packages[{index}]"
        if not isinstance(item, dict):
            raise InputValidationError(f"{context} must be an object")

        package_id = _require_id(item.get("id"), f"{context}.id")
        if package_id in seen_ids:
            raise InputValidationError(f"Duplicate package ID: {package_id!r}")
        seen_ids.add(package_id)

        warehouse = item.get("warehouse")
        warehouse_id = item.get("warehouse_id")
        if warehouse is not None and warehouse_id is not None and warehouse != warehouse_id:
            raise InputValidationError(
                f"{context} has conflicting 'warehouse' and 'warehouse_id' values"
            )
        raw_warehouse_id = warehouse if warehouse is not None else warehouse_id
        parsed_warehouse_id = _require_id(
            raw_warehouse_id, f"{context}.warehouse"
        )
        if parsed_warehouse_id not in warehouse_ids:
            raise InputValidationError(
                f"Package {package_id!r} references unknown warehouse "
                f"{parsed_warehouse_id!r}"
            )

        if "destination" not in item:
            raise InputValidationError(f"{context} requires 'destination'")
        destination = _parse_point(item["destination"], f"{context}.destination")
        packages.append(Package(package_id, parsed_warehouse_id, destination))

    return tuple(packages)


def normalize_data(raw: Any) -> InputData:
    """Normalize either supplied input schema into the internal domain model."""
    if not isinstance(raw, dict):
        raise InputValidationError("The JSON root must be an object")

    missing = [key for key in ("warehouses", "agents", "packages") if key not in raw]
    if missing:
        raise InputValidationError(
            "Missing required top-level field(s): " + ", ".join(missing)
        )

    warehouses = _normalize_locations(raw["warehouses"], "warehouses", Warehouse)
    agents = _normalize_locations(raw["agents"], "agents", Agent)
    packages = _normalize_packages(raw["packages"], {item.id for item in warehouses})

    if packages and not agents:
        raise InputValidationError("At least one agent is required when packages exist")

    return InputData(
        warehouses=tuple(warehouses),
        agents=tuple(agents),
        packages=packages,
    )


def load_input(path: str | Path) -> InputData:
    """Load and validate a UTF-8 JSON input file."""
    input_path = Path(path)
    try:
        raw = json.loads(
            input_path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_json_keys,
        )
    except json.JSONDecodeError as error:
        raise InputValidationError(
            f"Invalid JSON in {input_path}: line {error.lineno}, column {error.colno}"
        ) from error
    return normalize_data(raw)
