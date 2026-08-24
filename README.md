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

Adapted from [jpetazzo/container.training](https://github.com/jpetazzo/container.training)'s
DockerCoins - see [`NOTICE`](NOTICE) for what changed.

## Running locally

```bash
docker compose up
```

Give it 10-15 seconds, then check `http://localhost:8000/json` for a
non-zero `hashes` count. Full service list, ports, and endpoints:
[docs/architecture.md](docs/architecture.md).

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
