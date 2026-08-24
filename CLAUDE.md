# k8coins

Operating guidance for AI agents working in this repository.

## What this is

k8coins is a small polyglot microservices app (five services, four languages) used as the throughline demo in Platform Fix's Kubernetes workshops - the same way [podium](https://github.com/platformfix/podium) is. It's public: workshop attendees get pointed at this repo, so its code, CI, and docs are a visible part of the Platform Fix brand. Treat polish and correctness here as reputation-bearing, not optional. See the [README](README.md) for a quick start and [docs/architecture.md](docs/architecture.md) for what the app actually does (mining loop, architecture diagram, Dockerfile practices) - this file doesn't duplicate either.

## Repository layout

- `rng/`, `hasher/`, `worker/`, `webui/` - the four built services, one directory each, each with its own `Dockerfile`.
- `compose.yml` - local dev stack (all five services, including the off-the-shelf `redis`).
- `chart/k8coins/` - the Helm chart, published two ways on every release; see [docs/helm-chart.md](docs/helm-chart.md).
- `.github/workflows/` - PR checks (hadolint + build, one per service), release (auto-versioning + GHCR push + chart publish), commit-lint, pr-lint, e2e, scorecard.
- `.pre-commit-config.yaml` - local hooks, installed per [CONTRIBUTING.md](CONTRIBUTING.md).
- `docs/` - architecture, Helm chart, releases, and supply-chain detail, kept out of the README to keep it scannable; `docs/superpowers/` specifically is implementation plans from past sessions, kept for provenance rather than as a living doc.

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:6cd5cc61 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md for details and anti-patterns.

## Agent Context Profiles

The managed Beads block is task-tracking guidance, not permission to override repository, user, or orchestrator instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a Beads implementation workflow. It is subordinate to explicit user, repository, and orchestrator instructions.

1. **File issues for remaining work** - Create beads for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Handle git/sync by active profile**:
   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git pull --rebase
   git push
   git status
   ```
5. **Hand off** - Summarize changes, validation, issue status, and any blocked sync/commit/push step

**Critical rules:**
- Explicit user or orchestrator instructions override this Beads block.
- Do not commit or push without clear authority from the active profile or the current user request.
- If a required sync or push is blocked, stop and report the exact command and error.
<!-- END BEADS INTEGRATION -->


## Building and testing locally

```bash
docker compose up
```

Builds and starts all five services. Give it 10-15 seconds, then check
`http://localhost:8000/json` for a non-zero `hashes` count - that confirms
the whole loop (`worker` → `rng` → `hasher` → `redis` → `webui`) is actually
working, not just that containers started. To test one service in
isolation, build and run just its directory:

```bash
docker build -t k8coins-rng:dev rng
docker run --rm -p 8001:80 k8coins-rng:dev
curl localhost:8001/healthz
```

`hasher` and `worker` need `rng` (and `worker` needs `hasher` too) to
exercise their real logic beyond a bare health check - `docker compose up`
is the faster path for anything past a single-service smoke test.

## Architecture

See [docs/architecture.md](docs/architecture.md) for the service table and
mining-loop diagram - this file doesn't duplicate it.
The dependency graph is deliberately narrow (`worker` is the only service
that calls more than one neighbour); that's a teaching property of the app,
not an implementation detail, so don't "simplify" it away if refactoring
any of the four services.

## Conventions

- **Conventional Commits**, enforced on both commit messages (`commit-lint`)
  and PR titles (`pr-lint`) - a squash merge takes its message from the PR
  title, so a sloppy title becomes permanent history. Direct pushes to
  `main` are blocked by the branch ruleset; open a PR. Full detail in
  [CONTRIBUTING.md](CONTRIBUTING.md).
- **Dockerfile practices** (multi-stage builds, numeric UID, pinned
  dependencies, exec-form healthchecks) are documented once, in
  [docs/architecture.md](docs/architecture.md#dockerfile-practices) - that's
  the canonical home, follow it rather than re-deriving conventions
  per-service.

## Constraints that matter

This section is deliberately thin - k8coins doesn't have podium's years of
incident history yet. Add to it as real incidents happen; don't pad it with
theoretical "good practice" bullets that never actually bit anyone here.

- **`release.yml` auto-versions and releases on every push to `main`.** It
  infers a semver bump from commit messages since the last tag reachable
  from `HEAD`, then builds and pushes all four images and cuts a GitHub
  Release - unconditionally, with no manual gate. This is usually invisible
  because normal work lands via PR with a clean, ff-only history. It
  becomes a real hazard the moment `main`'s history or tags get rewritten
  directly (as happened once, deliberately, for the 2026-08-24 baseline
  squash): push any tag you want the workflow to see as "the last release"
  *before* pushing the rewritten `main`, or the workflow will read zero
  prior tags, infer a bump from the wrong base, and fire off an unintended
  image build and release. Check the workflow's own version-bump logic in
  `.github/workflows/release.yml` before touching `main` outside a normal PR
  merge. A `concurrency: group: release-main` block (added 2026-08-24, after
  this bit for real) queues overlapping runs rather than letting them race -
  before that fix, merging several PRs back to back (5 merged ~15s apart)
  caused all 5 runs to read the same last tag before any had pushed a new
  one, so all 5 computed the same next version and only the first to push
  won; the other 4 failed with "tag already exists," and the git tag/release
  for that version ended up pointing at an older commit than what actually
  got published under that image tag. If you're merging multiple PRs in a
  row, prefer spacing them out slightly even with the concurrency fix in
  place, since each queued run still produces its own separate release.
- **Required review on the `main` branch ruleset is 0, by design, not
  oversight** - same reasoning as [podium's](https://github.com/platformfix/podium):
  every PR here is authored under Steve's own GitHub identity, and GitHub
  hard-blocks a PR author from approving their own PR, so a review
  requirement wouldn't catch anything - it would just deadlock every PR.
  Verify the live setting with
  `gh api repos/platformfix/k8coins/rulesets/21280688 --jq '.rules[] | select(.type=="pull_request").parameters | {required_approving_review_count, require_code_owner_review}'`
  rather than assuming. The `pull_request`-required rule and the required
  status checks (`commit-lint`, `pr-lint`) stay on regardless - revisit the
  review requirement if this repo ever gets a second real contributor, not
  before.
- **GHCR package visibility is independent of repo visibility, and
  changing it needs a `write:packages` OAuth scope the standard `gh` CLI
  token doesn't carry.** Flipping the repo public does nothing to the four
  images. The reliable path is the org's package settings UI (Packages →
  each package → Danger Zone → Change visibility), and that flow has a
  confirm-the-package-name dialog that's easy to dismiss without noticing -
  if a visibility change doesn't seem to have stuck, check that the dialog
  was actually completed before assuming a caching issue - this happened
  live on 2026-08-24: a first attempt at the UI flow reported success but
  `gh api orgs/platformfix/packages/container/<name> --jq .visibility`
  still read `private` afterwards, and a second, more careful pass through
  the same dialog is what actually flipped it. Verify with that API call,
  or better, an anonymous pull (`docker pull
  ghcr.io/platformfix/k8coins-<service>:latest` from a machine with no GHCR
  credentials configured) - don't trust the settings page alone.
