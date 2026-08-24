# Contributing

Thanks for considering a contribution to k8coins.

## Before you start

Open an issue for anything beyond a small fix, so we can agree on the approach before you put time into it.

## Commits and pull requests

- Commit messages must follow [Conventional Commits](https://www.conventionalcommits.org/). This is enforced by CI (`commit-lint`).
- Pull request titles must also follow Conventional Commits. CI (`pr-lint`) checks this too, since a squash merge takes its message from the PR title.
- Keep commits small and focused; a pull request with five commits that each do one thing is easier to review than one commit that does five things.
- Direct pushes to `main` are blocked by the branch ruleset - open a PR.

Install the local pre-commit hooks so a malformed commit message is caught before it ever reaches CI:

```bash
pip install pre-commit
pre-commit install --install-hooks
```

## Testing changes locally

```bash
docker compose up
```

Builds and starts all five services. Give it 10-15 seconds, then check `http://localhost:8000/json` - a non-zero and increasing `hashes` count means the whole loop (`worker` → `rng` → `hasher` → `redis` → `webui`) is actually working, not just that containers started.

To test a single service in isolation:

```bash
docker build -t k8coins-rng:dev rng
docker run --rm -p 8001:80 k8coins-rng:dev
curl localhost:8001/healthz
```

`hasher` and `worker` need `rng` (and `worker` needs `hasher` too) to exercise their real logic beyond a bare health check - `docker compose up` is the faster path for anything past a single-service smoke test.

## Reporting issues

Open an issue on GitHub with what you expected, what happened instead, and how to reproduce it.
