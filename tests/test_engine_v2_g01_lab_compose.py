from pathlib import Path


def test_g01_compose_is_fixed_private_lab_without_published_ports():
    root = Path(__file__).resolve().parents[1]
    compose = (root / "docker-compose.g01-lab.yml").read_text(encoding="utf-8")
    runner = (root / "Dockerfile.g01-lab-runner").read_text(encoding="utf-8")
    entrypoint = (root / "scripts/g01-lab-runner-entrypoint.sh").read_text(encoding="utf-8")
    workflow = (root / ".github/workflows/ci.yml").read_text(encoding="utf-8")

    for address in ("172.28.0.10", "172.28.0.11"):
        assert address in compose
    assert 'network_mode: "service:msf-target"' in compose
    assert "internal: true" in compose
    assert "ports:" not in compose
    assert "WHAXON_ENABLE_V2_LAB_INITIAL_ACCESS: \"1\"" in compose
    assert "WHAXON_MSF_HOST: 127.0.0.1" in compose
    assert "metasploitframework/metasploit-framework:6.5.4@sha256:5ede8e5bccb4be4461754326ae2096e3a6bc2e0227aae4fa6b569f4ae442e548" in runner
    assert "git -C /opt/sqlmap checkout 5a12bd290d16992d0b46837b17b2694c8b64c746" in runner
    assert "gobuster_Linux_x86_64.tar.gz" in runner
    assert "c8a8c6a966eeb011d682a0ef2305a3e3a86b8b3fabe744350c00a766cc0f8021" in runner
    assert "tleemcjr/metasploitable2@sha256:e559450b37dccc1909eafa2df5b20bb052e1bd801246f4539a3ef183d5f7288a" in compose
    assert "-a 127.0.0.1" in entrypoint
    assert "engine-v2-g01-controlled-lab:" in workflow
    assert "scripts/g01-lab-chain.py" in workflow
    assert "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02" in workflow
    assert workflow.index("Generate ephemeral Metasploit RPC credential") < workflow.index(
        "Validate isolated fixed-address lab topology"
    )
    assert "sha256sum -c g01-mission-report.json.sha256" in workflow
    assert 'SQLI_URL = "http://172.28.0.10:8080/search?id=1"' in (
        root / "scripts/g01-lab-chain.py"
    ).read_text(encoding="utf-8")
    assert workflow.index("Generate ephemeral Metasploit RPC credential") < workflow.index(
        "Validate isolated fixed-address lab topology"
    )
