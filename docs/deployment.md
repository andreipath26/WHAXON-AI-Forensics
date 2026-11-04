# Deploying WHAXON

WHAXON web interface can run headless and be accessed from any browser.

## Local browser server

    whaxon web

Starts the Flask development-server entry point in the foreground. Debug mode and the automatic reloader are disabled; it does not provide production WSGI serving or automatic reload-on-change. Keep it on loopback for local use.

## Production WSGI server

    whaxon serve
    whaxon serve --threads 8

Runs the application through Waitress in the foreground. This is the production-oriented WSGI command; the web extra includes Waitress.

## Daemon

    whaxon serve --daemon --log data/whaxon.log

On supported POSIX hosts, daemon mode double-forks, writes the PID to `<WHAXON_DATA>/whaxon.pid` (default `data/whaxon.pid`) and redirects stdout/stderr to the selected log. Startup rejects a live PID already occupying the PID file.

Stop the daemon with SIGTERM:

    kill -TERM "$(cat data/whaxon.pid)"

The daemon's signal handler removes its PID file. If a stale PID file remains, first verify that the recorded process is no longer running before removing it. For managed deployments, prefer the included systemd unit or a process supervisor.

## Environment

- WHAXON_HOST       default 127.0.0.1   bind address
- WHAXON_PORT       default 5001        port
- WHAXON_DATA       default data        data directory
- WHAXON_AUTH_USER  default whaxon      basic auth user
- WHAXON_AUTH_PASS  default whaxon      basic auth password
- WHAXON_TRUST_PROXY default off         trust one configured reverse proxy for forwarded client IP / HTTPS scheme
- WHAXON_ALLOWED_HOSTS comma-separated additional Host values accepted by the local Host-header guard

Loopback development defaults are accepted only on loopback. For a non-loopback listener, install the `web` extra and set an explicit non-default username plus either a strong, unique `WHAXON_AUTH_PASS` or a precomputed bcrypt `WHAXON_AUTH_PASS_HASH` with cost factor 12 or higher. Network-facing startup rejects SHA-256 password hashes and refuses to fall back to weak hashing if bcrypt is unavailable. Never use the demo credentials in a network deployment.

## systemd

whaxon.service is included in the repo root. Install:

    sudo cp whaxon.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable --now whaxon

Adjust User, WorkingDirectory, and paths to your layout.

## Engine V2 durable worker alongside the web service (systemd)

Engine V2 run requests are stored in SQLite and require a **separate supervised
worker**. Running only `whaxon.service` exposes the web interface but does
not guarantee that queued V2 work is being processed. Installing a service
unit is configuration, not proof that a process is healthy.

Use the two repository-provided units from the **same installed WHAXON
release**: `whaxon.service` and `whaxon-workflow-worker.service`. Both
specify `User=whaxon`, `WorkingDirectory=/opt/whaxon`,
`WHAXON_DATA=/var/lib/whaxon/data`, and `StateDirectory=whaxon`.
Provision the virtual environment and the protected `/etc/whaxon.env`
before enabling services. Never use default/demo network credentials;
restrict the environment file to administrators, and ensure the service
identity can access only its intended persistent state. Review and adjust
paths for the host instead of blindly copying a unit from another installation.

On a supported systemd host, after reviewing units and provisioning the
service user, application, environment and state:

```sh
sudo install -m 0644 whaxon.service whaxon-workflow-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now whaxon.service whaxon-workflow-worker.service
sudo systemctl status whaxon.service whaxon-workflow-worker.service
sudo journalctl -u whaxon-workflow-worker.service --no-pager -n 100
```

The web and worker services use a shared store, **not separate SQLite
databases**. Do not start an additional ad-hoc drain worker against the same
installation without first evaluating worker ownership and resource limits.
The worker runs `whaxon workflow plan serve-requests` in the foreground;
SIGTERM stops admission of additional claims. An external effect already in
flight may remain uncertain, not automatically cancelled or replayed.

For a local operational check, inspect the web's Core readiness at
`http://127.0.0.1:5001/api/health` using the configured authentication
when required. Core readiness does **not** prove worker liveness. Check the
worker's systemd status/journal and, as the service account with the
production data path, inspect `whaxon workflow plan queue-summary`.
Verify a permitted, explicitly approved synthetic/controlled workflow
through submission, persisted run-request inspection, restart, reconnect
and cancellation without unauthorized external activity.

### Backup, recovery and release evidence

Protect the **entire** operator state: the consistent SQLite database
transactional snapshot, protected configuration and scope/approvals,
evidence/artifacts and installed-provider inventory. The automated
`test_engine_v2_e5_backup_restore.py` covers a SQLite-only snapshot, not
this full recovery. Never claim success from copying a live database file
without a consistent backup. Before a restore, stop **both** services,
retain the old state for investigation, restore files with service ownership
and restrictive permissions, then bring the services back under supervision.
Treat recovered in-flight/expired work as **uncertain** pending manual
reconciliation; never silently requeue potentially effectful operations.

Deployment acceptance requires a dated record of host OS, exact commit and
package version, chosen systemd paths, credentials/proxy/TLS safeguards,
start/stop/restart behavior, worker claims, approved test target, request
IDs, queue/audit evidence, complete backup/restore, failure injection,
known limitations, and reviewer sign-off. Until a real supported-host
rehearsal succeeds, E5 deployment readiness remains **NOT VERIFIED**.

## Docker

Hardened container:

    docker build -t whaxon:secure .
    docker run --rm -d --name whaxon --read-only --tmpfs /tmp:rw,noexec,nosuid,size=64m --cap-drop=ALL --security-opt=no-new-privileges:true -p 127.0.0.1:5001:5001 -v data:/data -e HOME=/tmp -e WHAXON_AUTH_USER=whaxon-admin -e WHAXON_AUTH_PASS=replace-with-a-long-unique-password -e WHAXON_DATA=/data whaxon:secure

Notes:

- --read-only filesystem; /tmp is a tmpfs.
- -v data:/data is the persistent volume.
- WHAXON_DATA points at the mounted volume.
- Tools installed inside the container are not persisted. Bake them into the image.
- The Dockerfile binds gunicorn to 0.0.0.0:5001 inside the container. This is required for the container to be reachable from the host. The example above publishes the port to 127.0.0.1 only via -p 127.0.0.1:5001:5001, so the container is not exposed to the host network. Do not remove the -p 127.0.0.1: prefix unless you intend to expose WHAXON on the host network.

## HTTPS

Recommended: reverse-proxy. Terminate TLS at nginx/caddy/traefik in front of 127.0.0.1:5001. Keep the WHAXON bind on loopback and let the proxy handle certificates, HSTS, and rate limiting. For the nginx pattern below, set `WHAXON_TRUST_PROXY=1` and add the public hostname to `WHAXON_ALLOWED_HOSTS` (for example, `whaxon.example.com`). Only enable proxy trust when the app is reachable exclusively through that trusted proxy; otherwise clients could spoof forwarded headers.

nginx example:

    server {
      listen 443 ssl http2;
      server_name whaxon.example.com;
      ssl_certificate     /etc/letsencrypt/live/whaxon.example.com/fullchain.pem;
      ssl_certificate_key /etc/letsencrypt/live/whaxon.example.com/privkey.pem;
      location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_buffering off;
      }
    }

### Opt-in Engine V2 Docker deployment

The root `docker-compose.yml` defines an intentionally separate target lab;
**do not** use it as a WHAXON production deployment. The new
`docker-compose.e5.yml` runs two non-root services from the same built image:
`web` and the persistent `workflow-worker`. They share the named
`e5-state` volume at `/data`, while only the web service publishes
`127.0.0.1:5001`. Both containers use read-only root filesystems, a
restricted tmpfs and dropped Linux capabilities.

Provide strong non-default `WHAXON_AUTH_USER` and `WHAXON_AUTH_PASS`
values via a private operator environment (or a protected Compose env file)
without committing credentials. Inspect the fully resolved configuration
before starting; do not post its output because it can contain secrets.

```sh
docker compose -f docker-compose.e5.yml config --quiet
docker compose -f docker-compose.e5.yml up -d --build
docker compose -f docker-compose.e5.yml ps
docker compose -f docker-compose.e5.yml logs --tail 100 workflow-worker
```

A started container does not certify worker liveness or external-effect
recovery. Verify the shared queue and one explicitly approved controlled
workflow before accepting the deployment. Persist and back up the named
volume together with independently protected operational configuration and
evidence. This Compose configuration is an **engineering candidate**;
real Docker service, restart, recovery, secrets and backup/restore acceptance
are still outstanding.

### Offline E5 operator-state snapshot and restoration

Stop **both** web and workflow-worker services before taking an offline backup;
the utility cannot determine whether another process is modifying the state.
The standalone tool includes the complete operator-state file tree (such as
scope, configuration and evidence), makes a consistent SQLite backup,
rejects symbolic links/nonregular files and generates per-file SHA-256 checks.
It does not back up secrets or host configuration outside `WHAXON_DATA`.

```sh
python -m whaxon.core.state_snapshot backup /var/lib/whaxon/data /secure/whaxon-e5-snapshot
python -m whaxon.core.state_snapshot verify /secure/whaxon-e5-snapshot --expected-manifest-sha256 "<independently-retained-64-character-sha256>"
python -m whaxon.core.state_snapshot restore /secure/whaxon-e5-snapshot /secure/whaxon-restored --expected-manifest-sha256 "<independently-retained-64-character-sha256>"
```

The destination must **not exist**. Restore into a separate location, inspect
its integrity and ownership, and only then coordinate a deliberate cutover
while both services remain stopped. The snapshot's internal checksums detect
accidental changes but are **not independently trusted**: retain its manifest
hash or copy in protected external storage with operator-controlled identity.
Use restrictive permissions and encrypted off-host retention for sensitive
evidence. This is an offline engineering recovery mechanism; real supervised
host restoration and sign-off remain mandatory E5 deployment gates.

The backup command outputs `manifest_sha256`; retain that value outside
WHAXON storage using an operator-protected witness before allowing a later
restore. Verification without `--expected-manifest-sha256` detects file drift
against the internal manifest but **does not** protect against an attacker who
changes the manifest itself. The external expected digest provides comparison
only; its authenticity depends on how the operator retained it.

### E5 dedicated-worker mode

The systemd web unit and opt-in paired Docker web container set
`WHAXON_V2_EXTERNAL_WORKER=1`. In this mode the web API durably enqueues V2
run requests but **does not create an additional process-local queue drainer**.
Only the separately supervised `workflow-worker` executes V2 queue work.
When it is down, accepted requests remain queued, never falsely completed.
Existing web-only users without this flag retain the prior wakeup behavior.
This flag does not disable unrelated legacy tool/AI execution endpoints;
those remain a separate authorization and migration obligation.
