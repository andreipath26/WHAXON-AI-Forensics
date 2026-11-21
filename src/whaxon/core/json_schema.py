"""Fail-closed validation for the JSON Schema subset used by capabilities.

Capability schemas are execution contracts, not documentation. This module
implements the assertion keywords used by bundled providers without adding a
runtime dependency or silently accepting unsupported constraints.
"""
from __future__ import annotations

import math
import re
from collections.abc import Mapping
from typing import Any

_TYPES = {"array", "boolean", "integer", "null", "number", "object", "string"}
_SCHEMA_KEYS = {
    "additionalProperties", "const", "description", "enum", "items", "maximum",
    "maxItems", "maxLength", "minimum", "minItems", "minLength", "oneOf",
    "pattern", "properties", "required", "title", "type",
}


class SchemaContractError(ValueError):
    """A capability schema or value violates its declared JSON contract."""


def _is_mapping(value: Any) -> bool:
    return isinstance(value, Mapping)


def validate_schema(schema: Any, *, path: str = "$", depth: int = 0) -> None:
    """Check schema structure before it can be persisted or used for dispatch."""
    if depth > 64:
        raise SchemaContractError(f"{path}: schema nesting exceeds 64 levels")
    if not _is_mapping(schema):
        raise SchemaContractError(f"{path}: schema must be an object")
    unknown = set(schema) - _SCHEMA_KEYS
    if unknown:
        raise SchemaContractError(
            f"{path}: unsupported schema keyword(s): {', '.join(sorted(unknown))}",
        )
    if "type" in schema:
        types = schema["type"]
        if isinstance(types, str):
            types = (types,)
        if (not isinstance(types, (list, tuple)) or not types
                or any(item not in _TYPES for item in types)
                or len(set(types)) != len(types)):
            raise SchemaContractError(f"{path}.type: invalid JSON type declaration")
    if "required" in schema:
        required = schema["required"]
        if (not isinstance(required, (list, tuple))
                or any(not isinstance(item, str) or not item for item in required)
                or len(set(required)) != len(required)):
            raise SchemaContractError(f"{path}.required: expected unique property names")
    if "properties" in schema:
        properties = schema["properties"]
        if not _is_mapping(properties) or any(not isinstance(key, str) for key in properties):
            raise SchemaContractError(f"{path}.properties: expected an object")
        for key, child in properties.items():
            validate_schema(child, path=f"{path}.properties.{key}", depth=depth + 1)
    for key in ("items", "additionalProperties"):
        if key in schema and not isinstance(schema[key], bool):
            validate_schema(schema[key], path=f"{path}.{key}", depth=depth + 1)
    if "oneOf" in schema:
        branches = schema["oneOf"]
        if not isinstance(branches, (list, tuple)) or not branches:
            raise SchemaContractError(f"{path}.oneOf: expected a non-empty array")
        for index, child in enumerate(branches):
            validate_schema(child, path=f"{path}.oneOf[{index}]", depth=depth + 1)
    for key in ("minLength", "maxLength", "minItems", "maxItems"):
        if key in schema and (type(schema[key]) is not int or schema[key] < 0):
            raise SchemaContractError(f"{path}.{key}: expected a nonnegative integer")
    for key in ("minimum", "maximum"):
        if key in schema and (
            isinstance(schema[key], bool)
            or not isinstance(schema[key], (int, float))
            or not math.isfinite(schema[key])
        ):
            raise SchemaContractError(f"{path}.{key}: expected a finite number")
    if "pattern" in schema:
        if not isinstance(schema["pattern"], str):
            raise SchemaContractError(f"{path}.pattern: expected a string")
        try:
            re.compile(schema["pattern"])
        except re.error as exc:
            raise SchemaContractError(f"{path}.pattern: invalid regular expression") from exc
    if "enum" in schema and (
        not isinstance(schema["enum"], (list, tuple)) or not schema["enum"]
    ):
        raise SchemaContractError(f"{path}.enum: expected a non-empty array")


def _matches_type(value: Any, declared: str) -> bool:
    if declared == "object":
        return _is_mapping(value)
    if declared == "array":
        return isinstance(value, (list, tuple))
    if declared == "integer":
        return type(value) is int
    if declared == "number":
        return not isinstance(value, bool) and isinstance(value, (int, float))
    if declared == "boolean":
        return type(value) is bool
    if declared == "string":
        return isinstance(value, str)
    return value is None


def _validate(schema: Mapping[str, Any], value: Any, path: str, depth: int) -> None:
    if depth > 64:
        raise SchemaContractError(f"{path}: value nesting exceeds 64 levels")
    declared = schema.get("type")
    if declared is not None:
        types = (declared,) if isinstance(declared, str) else declared
        if not any(_matches_type(value, item) for item in types):
            raise SchemaContractError(f"{path}: value has the wrong type")
    if "const" in schema and value != schema["const"]:
        raise SchemaContractError(f"{path}: value does not match const")
    if "enum" in schema and value not in schema["enum"]:
        raise SchemaContractError(f"{path}: value is outside enum")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            raise SchemaContractError(f"{path}: string is shorter than minLength")
        if len(value) > schema.get("maxLength", math.inf):
            raise SchemaContractError(f"{path}: string exceeds maxLength")
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            raise SchemaContractError(f"{path}: string does not match pattern")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if not math.isfinite(value):
            raise SchemaContractError(f"{path}: number must be finite")
        if "minimum" in schema and value < schema["minimum"]:
            raise SchemaContractError(f"{path}: number is below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            raise SchemaContractError(f"{path}: number exceeds maximum")
    if isinstance(value, (list, tuple)):
        if len(value) < schema.get("minItems", 0):
            raise SchemaContractError(f"{path}: array is shorter than minItems")
        if len(value) > schema.get("maxItems", math.inf):
            raise SchemaContractError(f"{path}: array exceeds maxItems")
        child = schema.get("items")
        if isinstance(child, Mapping):
            for index, item in enumerate(value):
                _validate(child, item, f"{path}[{index}]", depth + 1)
    if _is_mapping(value):
        for key in schema.get("required", ()):
            if key not in value:
                raise SchemaContractError(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, item in value.items():
            child = properties.get(key)
            if child is not None:
                _validate(child, item, f"{path}.{key}", depth + 1)
            elif additional is False:
                raise SchemaContractError(f"{path}: unexpected property {key!r}")
            elif isinstance(additional, Mapping):
                _validate(additional, item, f"{path}.{key}", depth + 1)
    if "oneOf" in schema:
        matches = 0
        for branch in schema["oneOf"]:
            try:
                _validate(branch, value, path, depth + 1)
            except SchemaContractError:
                continue
            matches += 1
        if matches != 1:
            raise SchemaContractError(f"{path}: value must match exactly one oneOf branch")


def validate_instance(schema: Mapping[str, Any], value: Any, *, path: str = "$") -> None:
    """Raise when a JSON-compatible value violates its declared schema."""
    validate_schema(schema)
    _validate(schema, value, path, 0)
