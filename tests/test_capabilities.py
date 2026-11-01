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
