from whaxon.core.capabilities import (
    CapabilityManifest,
    CapabilityRegistry,
    CapabilityRequirements,
    CapabilityUnavailable,
)


def _manifest(provider, *, readiness="registered", **kwargs):
    return CapabilityManifest(
        capability_id="network.port_scan",
        provider_id=provider,
        provider_version="1.0.0",
        transports=("local_process",),
        target_types=("hostname", "ip"),
        protocols=("tcp",),
        platforms=("linux",),
        readiness=readiness,
        **kwargs,
    )


def test_capability_resolution_is_deterministic_and_prefers_readiness():
    registry = CapabilityRegistry()
    registry.register(_manifest("provider.z", readiness="installed"))
    registry.register(_manifest("provider.b", readiness="lab_validated"))
    registry.register(_manifest("provider.a", readiness="lab_validated"))
    result = registry.resolve(
        "network.port_scan",
        CapabilityRequirements(target_type="ip", protocol="tcp", platform="linux"),
    )
    assert result.manifest.provider_id == "provider.a"
    assert result.considered == 3
    assert result.registry_digest == registry.digest


def test_capability_resolution_reports_constraint_failures():
    registry = CapabilityRegistry()
    registry.register(_manifest("provider.a"))
    try:
        registry.resolve(
            "network.port_scan",
            CapabilityRequirements(
                protocol="udp", transport="remote_agent",
                minimum_readiness="smoke_tested",
            ),
        )
    except CapabilityUnavailable as exc:
        assert exc.capability_id == "network.port_scan"
        assert len(exc.rejected) == 1
    else:
        raise AssertionError("incompatible provider must not resolve")


def test_capability_provider_version_is_immutable():
    import pytest

    registry = CapabilityRegistry()
    registry.register(_manifest("provider.a", readiness="installed"))
    with pytest.raises(ValueError, match="immutable"):
        registry.register(_manifest("provider.a", readiness="lab_validated"))


def test_capability_manifest_does_not_authorize_execution():
    manifest = _manifest("provider.a", permissions=("network.scan",), impact="moderate")
    assert manifest.permissions == ("network.scan",)
    assert manifest.impact == "moderate"
    assert not hasattr(manifest, "authorized")


def test_capability_manifest_nested_schema_is_immutable():
    import pytest

    schema = {"properties": {"ports": {"enum": [80, 443]}}}
    manifest = _manifest("provider.a", input_schema=schema)
    fingerprint = manifest.fingerprint
    schema["properties"]["ports"]["enum"].append(8080)
    assert manifest.fingerprint == fingerprint
    with pytest.raises(TypeError, match="immutable"):
        manifest.input_schema["properties"]["new"] = {}
    assert manifest.input_schema["properties"]["ports"]["enum"] == (80, 443)


def test_capability_registry_persists_and_reloads_manifests(tmp_path):
    from whaxon.core.store import JobStore

    store = JobStore(tmp_path / "capabilities.db")
    registry = CapabilityRegistry(store=store)
    manifest = _manifest("provider.persisted", readiness="smoke_tested")
    registry.register(manifest)
    restored = CapabilityRegistry(store=store)
    result = restored.resolve(
        "network.port_scan",
        CapabilityRequirements(minimum_readiness="smoke_tested"),
    )
    assert result.manifest.fingerprint == manifest.fingerprint
    assert restored.digest == registry.digest


def test_store_rejects_manifest_version_mutation(tmp_path):
    import pytest

    from whaxon.core.store import JobStore

    store = JobStore(tmp_path / "capability-immutable.db")
    registry = CapabilityRegistry(store=store)
    registry.register(_manifest("provider.immutable", readiness="installed"))
    with pytest.raises(ValueError, match="immutable"):
        registry.register(_manifest("provider.immutable", readiness="lab_validated"))


def test_capability_manifest_rejects_non_finite_timeout():
    import math

    import pytest

    with pytest.raises(ValueError, match="finite"):
        _manifest("provider.nan", timeout_s=math.nan)


def test_resolver_enforces_permissions_impact_and_schema_compatibility():
    import pytest
    registry = CapabilityRegistry()
    registry.register(_manifest(
        "provider.a", readiness="smoke_tested", permissions=("network.scan",),
        impact="moderate", input_schema={"type": "object"},
        output_schema={"type": "object"},
    ))
    valid = CapabilityRequirements(
        required_permissions=("network.scan",), maximum_impact="moderate",
        required_input_schema={"type": "object"},
        required_output_schema={"type": "object"},
    )
    assert registry.resolve("network.port_scan", valid).manifest.provider_id == "provider.a"
    for bad in (
        CapabilityRequirements(required_permissions=("credentials.read",)),
        CapabilityRequirements(maximum_impact="low"),
        CapabilityRequirements(required_input_schema={"type": "array"}),
        CapabilityRequirements(required_output_schema={"type": "array"}),
        CapabilityRequirements(maximum_timeout_s=301),
    ):
        with pytest.raises(CapabilityUnavailable):
            registry.resolve("network.port_scan", bad)


def test_resolver_rejects_invalid_resource_constraints():
    import math

    import pytest
    registry = CapabilityRegistry()
    registry.register(_manifest("provider.a"))
    for value in (0, -1, math.nan, math.inf, True):
        with pytest.raises(ValueError):
            registry.resolve("network.port_scan", CapabilityRequirements(maximum_timeout_s=value))
    with pytest.raises(ValueError):
        registry.resolve("network.port_scan", CapabilityRequirements(maximum_impact="unbounded"))
    with pytest.raises(TypeError):
        registry.resolve("network.port_scan", CapabilityRequirements(required_input_schema=[]))
