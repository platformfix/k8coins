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
autoscaling (disabled by default), whether redis runs as a Deployment or a
StatefulSet (see [below](#running-redis-as-a-deployment-or-a-statefulset)),
and an optional Ingress for `webui` (also disabled by default; `docker
compose`-style access is `kubectl port-forward svc/webui 8000:80`).

`rng`, `hasher`, `worker`, and `webui` reach each other and `redis` by a
fixed Kubernetes Service name hardcoded in each service's own source code
(there's no environment variable to override it), so this chart's Service
names are fixed too, not release-name-prefixed like a typical chart. Only
one release can run per namespace - install a second copy in its own
namespace rather than trying to run two side by side in one.

## Running redis as a Deployment or a StatefulSet

`redis.kind` chooses how redis runs. The chart has one template per kind,
[`redis-deployment.yaml`](../chart/k8coins/templates/redis-deployment.yaml)
and [`redis-statefulset.yaml`](../chart/k8coins/templates/redis-statefulset.yaml),
and renders only the one you pick, so you can read the two side by side to
see exactly what changes.

| `redis.kind` | Storage | What happens when the redis pod restarts |
|---|---|---|
| `Deployment` (default) | None | Coins and hashes reset to zero |
| `StatefulSet` | A PersistentVolumeClaim (`data-redis-0`), with redis append-only persistence turned on | Coins and hashes carry on from where they were |

```bash
helm install k8coins oci://ghcr.io/platformfix/k8coins \
  --set redis.kind=StatefulSet \
  --set redis.persistence.size=1Gi \
  --set redis.persistence.storageClass=standard  # omit to use the cluster default
```

`redis.persistence.*` only applies in StatefulSet mode. Either way, the app
reaches redis at the same `redis` Service; StatefulSet mode adds a headless
`redis-headless` Service as the StatefulSet's `serviceName`.

To see the difference, delete the redis pod and watch the `coins` count in
`webui`'s `/json`: in Deployment mode it drops back to zero, in StatefulSet
mode it doesn't.

Two things to know before switching:

- **Switching kinds on an existing release does not carry data across.** A
  `helm upgrade` that changes `redis.kind` deletes one workload and creates
  the other, and the new redis starts empty. Moving from StatefulSet to
  Deployment drops the data; moving from Deployment to StatefulSet has none
  to bring.
- **The PersistentVolumeClaim outlives the release.** Kubernetes keeps
  StatefulSet claims when the StatefulSet is deleted, and `helm uninstall`
  doesn't remove them either. Delete it yourself when you're done with the
  data: `kubectl delete pvc data-redis-0`. If you switch back to
  StatefulSet while the claim still exists, redis picks up the old data.
