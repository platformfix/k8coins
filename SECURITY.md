# Security Policy

## Supported versions

k8coins ships one rolling `latest` release across all four images; there's no long-term-support branch to track. Security fixes land on `main` and are published as the next release, automatically, on merge.

## Reporting a vulnerability

Please report security issues privately rather than opening a public GitHub issue: use [GitHub's private vulnerability reporting](https://github.com/platformfix/k8coins/security/advisories/new) for this repository (Security tab → Report a vulnerability).

Include what you'd include in any good bug report: the affected version or commit, what you found, and how to reproduce it. We'll acknowledge new reports within 5 business days and aim to have a fix or mitigation plan within 30 days, depending on severity.

## Scope

k8coins runs with no elevated cluster permissions - it's four plain Deployments and Services with a deliberately trivial mining loop, not a system that needs `cluster-admin` or any other elevated capability to function. There's no equivalent carve-out to make here: a privilege-escalation report, a container escape, or an exposed secret is in scope, the same as it would be for any other workload.

Reports that the mining/hashing logic has no real cryptographic value, or that a "coin" is trivially easy to find, aren't security issues - that's the deliberately weak, deliberately visible business logic the whole app exists to demonstrate a system's behavior around, not a vulnerability to fix.
