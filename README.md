# k8coins

[![PR checks](https://github.com/platformfix/k8coins/actions/workflows/pr-check.yml/badge.svg)](https://github.com/platformfix/k8coins/actions/workflows/pr-check.yml)
[![e2e](https://github.com/platformfix/k8coins/actions/workflows/e2e.yml/badge.svg)](https://github.com/platformfix/k8coins/actions/workflows/e2e.yml)
[![commit-lint](https://github.com/platformfix/k8coins/actions/workflows/commit-lint.yaml/badge.svg)](https://github.com/platformfix/k8coins/actions/workflows/commit-lint.yaml)
[![pr-lint](https://github.com/platformfix/k8coins/actions/workflows/pr-lint.yml/badge.svg)](https://github.com/platformfix/k8coins/actions/workflows/pr-lint.yml)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/platformfix/k8coins/badge)](https://scorecard.dev/viewer/?uri=github.com/platformfix/k8coins)
[![Latest Release](https://img.shields.io/github/v/release/platformfix/k8coins)](https://github.com/platformfix/k8coins/releases)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

A small polyglot microservices app used as the throughline demo in Platform
Fix's Kubernetes workshops. Five services, four languages, one mining
loop: `rng` generates data, `hasher` hashes it, `worker` drives the loop
and checks for a coin, `redis` holds the state, `webui` shows the rate.
An orchestrator doesn't care what runtime a service is written in - it
cares whether the container starts, holds a port open, and reports its
own health.

## Running locally

```bash
docker compose up -d
```

Give it 10-15 seconds, then check `http://localhost:8000/json` for a
non-zero `hashes` count. What each service does and how the mining loop
fits together: [docs/architecture.md](docs/architecture.md).

## Endpoints

Every service listens on port 80 inside its container. Each one carries
the same three operational routes - `/healthz`, `/live`, `/metrics` - on
top of whatever business routes it has, if any. Under `docker compose`,
`webui` is on `localhost:8000`, `rng` on `localhost:8001`, and `hasher` on
`localhost:8002`; `worker` publishes no host port, so reach it with
`docker compose exec worker` or a Kubernetes port-forward.

| Service | Method | Path | Purpose |
|---|---|---|---|
| `rng` | GET | `/` | Plain-text identity check: `RNG running on <hostname>` |
| `rng` | GET | `/<n>` | Returns `n` random bytes from `/dev/urandom` |
| `rng` | GET | `/healthz` | Always `ok`; `rng` has no external dependencies |
| `rng` | GET | `/live` | Always `ok` |
| `rng` | GET | `/metrics` | Prometheus text: `k8coins_rng_bytes_served_total`, `k8coins_rng_requests_served_total` |
| `hasher` | GET | `/` | Plain-text identity check: `HASHER running on <hostname>` |
| `hasher` | POST | `/` | Hashes the request body (SHA-2), returns the hex digest |
| `hasher` | GET | `/healthz` | Always `ok`; `hasher` has no external dependencies |
| `hasher` | GET | `/live` | Always `ok` |
| `hasher` | GET | `/metrics` | Prometheus text: `k8coins_hasher_hashes_total` |
| `worker` | GET | `/healthz` | `ok`, or `503` if no successful `rng`+`hasher` round trip in the last 30s. `worker` has no other HTTP surface - this is the only way to see it directly |
| `worker` | GET | `/live` | Always `ok` |
| `worker` | GET | `/metrics` | Prometheus text: `k8coins_hashes_total`, `k8coins_coins_total` - the real, authoritative counters |
| `webui` | GET | `/` | Redirects to `/index.html` |
| `webui` | GET | `/index.html` | The mining-rate dashboard (static, served from `files/`) |
| `webui` | GET | `/json` | `{coins, hashes, now}`, polled by the dashboard once a second, read from redis |
| `webui` | GET | `/healthz` | Always `ok` - deliberately does not check redis connectivity, since `webui` is designed to keep serving its last-known counts when a dependency is down |
| `webui` | GET | `/live` | Always `ok` |
| `webui` | GET | `/metrics` | Prometheus text: Node process defaults, `k8coins_webui_json_requests_total`, and `k8coins_wallet_coins` (the redis `wallet` size - the same number as `/json`'s `coins`, and unlike `worker`'s counter it survives restarts). Read from redis at scrape time with a 1s timeout; while redis is unreadable the coin sample is omitted and `k8coins_wallet_up` reads `0`, so the scrape itself never fails or hangs |

`redis` exposes no HTTP surface; it's the off-the-shelf `redis:7-alpine`
image, probed and administered as redis, not as a web service. It requires
a password (`--requirepass`), which `worker` and `webui` - the only two
services that talk to it - read from a `REDIS_PASSWORD` environment
variable sourced from a Secret (Helm-generated on first install and
preserved across upgrades; a fixed local-only value in `compose.yml`).

## Running on Kubernetes

```bash
helm install k8coins oci://ghcr.io/platformfix/k8coins
```

Full install options (including a traditional `helm repo add` path) and
configurable values: [docs/helm-chart.md](docs/helm-chart.md).

## Releases

Every merge to `main` cuts a new version, publishes all four images to
GHCR, and republishes the Helm chart - see [docs/releases.md](docs/releases.md).

## Supply chain security

Every image and chart release is signed and attested (build provenance and
an SBOM), and the repo runs a weekly OpenSSF Scorecard check (badge above).
See [docs/supply-chain.md](docs/supply-chain.md) for verification commands,
and [SECURITY.md](SECURITY.md) to report a vulnerability.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Commits and pull request titles
must follow [Conventional Commits](https://www.conventionalcommits.org/);
this is enforced by CI.

## License

[Apache 2.0](LICENSE)
