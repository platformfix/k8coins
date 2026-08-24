# Contributing

## Commit messages

Commit messages and PR titles follow [Conventional Commits](https://www.conventionalcommits.org/),
enforced by the `commit-lint` and `pr-lint` CI checks on every pull request.

Install the local pre-commit hooks so a malformed commit message is caught
before it ever reaches CI:

```bash
pip install pre-commit
pre-commit install --install-hooks
```
