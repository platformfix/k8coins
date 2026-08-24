# Helm chart

A chart at [`chart/k8coins`](../chart/k8coins) deploys all five services to a
Kubernetes cluster, published two ways on every release - pick whichever
suits your environment:

```bash
# OCI (no `helm repo add` needed)
helm install k8coins oci://ghcr.io/platformfix/k8coins --version <version>

# Traditional Helm repo, hosted on GitHub Pages
helm repo add k8coins https://platformfix.github.io/k8coins
helm repo update
helm install k8coins k8coins/k8coins --version <version>
```

Omit `--version` to get the latest chart. Each service's image tag
defaults to the chart's own `appVersion` (the same version as the images
built in the same release), so a plain install with no overrides pulls a
matched set. See [`chart/k8coins/values.yaml`](../chart/k8coins/values.yaml)
for what's configurable - per-service resource requests/limits,
autoscaling (disabled by default), and an optional Ingress for `webui`
(also disabled by default; `docker compose`-style access is `kubectl
port-forward svc/webui 8000:80`).

`rng`, `hasher`, `worker`, and `webui` reach each other and `redis` by a
fixed Kubernetes Service name hardcoded in each service's own source code
(there's no environment variable to override it), so this chart's Service
names are fixed too, not release-name-prefixed like a typical chart. Only
one release can run per namespace - install a second copy in its own
namespace rather than trying to run two side by side in one.
