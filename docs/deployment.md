# Deploying WHAXON

WHAXON web interface can run headless and be accessed from any browser.

## Foreground

    whaxon web

Dev mode: reload on change, verbose logs.

## Daemon

    whaxon serve --daemon --log data/whaxon.log

Double-forks, writes data/whaxon.pid, redirects stdout/stderr. Rejects startup if a live pid already occupies data/whaxon.pid.

Stop:

    kill $(cat data/whaxon.pid)
    rm -f data/whaxon.pid

## Environment

- WHAXON_HOST       default 127.0.0.1   bind address
- WHAXON_PORT       default 5001        port
- WHAXON_DATA       default data        data directory
- WHAXON_AUTH_USER  default whaxon      basic auth user
- WHAXON_AUTH_PASS  default whaxon      basic auth password
- WHAXON_TRUST_PROXY default off         trust one configured reverse proxy for forwarded client IP / HTTPS scheme
- WHAXON_ALLOWED_HOSTS comma-separated additional Host values accepted by the local Host-header guard

Loopback development defaults are accepted only on loopback. For a non-loopback listener, set an explicit non-default username and either a strong `WHAXON_AUTH_PASS` or a precomputed `WHAXON_AUTH_PASS_HASH`. Never use the demo credentials in a network deployment.

## systemd

whaxon.service is included in the repo root. Install:

    sudo cp whaxon.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable --now whaxon

Adjust User, WorkingDirectory, and paths to your layout.

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