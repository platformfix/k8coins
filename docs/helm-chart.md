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

Two independent settings control redis:

- `redis.kind` (`Deployment`, the default, or `StatefulSet`) picks the
  workload. The chart has one template per kind,
  [`redis-deployment.yaml`](../chart/k8coins/templates/redis-deployment.yaml)
  and [`redis-statefulset.yaml`](../chart/k8coins/templates/redis-statefulset.yaml),
  and renders only the one you pick, so you can read them side by side.
- `redis.persistence.enabled` (off by default) gives redis a
  PersistentVolumeClaim and turns on append-only persistence, so coins
  survive a redis pod restart. With it off, they reset to zero.

| | `persistence.enabled: false` (default) | `persistence.enabled: true` |
|---|---|---|
| **`kind: Deployment`** (default) | No storage; `/data` is an emptyDir that goes with the pod. | The chart creates one claim, `redis-data` ([`redis-pvc.yaml`](../chart/k8coins/templates/redis-pvc.yaml)), and the Deployment mounts it. Rolling updates use `maxSurge: 0`, so the old pod releases the volume before the new one starts. |
| **`kind: StatefulSet`** | No storage; `/data` is an emptyDir. Only the workload kind and its headless Service change. | The StatefulSet creates its own claim, `data-redis-0`, from `volumeClaimTemplates`, and reattaches it to the pod whenever the pod is recreated. |

```bash
helm install k8coins oci://ghcr.io/platformfix/k8coins \
  --set redis.kind=StatefulSet \
  --set redis.persistence.enabled=true \
  --set redis.persistence.size=1Gi \
  --set redis.persistence.storageClass=standard  # omit to use the cluster default
```

Either way, the app reaches redis at the same `redis` Service. StatefulSet
mode adds a headless `redis-headless` Service as the StatefulSet's
`serviceName`.

In every combination the redis pod follows the Kubernetes
[restricted Pod Security Standard](https://kubernetes.io/docs/concepts/security/pod-security-standards/#restricted):
it runs as the image's unprivileged `redis` user, can't escalate privileges,
drops all Linux capabilities, uses the default seccomp profile, and has a
read-only root filesystem, so `/data` is the only place it can write. It also
has readiness and liveness probes, no service-account token, and a pinned
redis version.

To see the difference, delete the redis pod and watch the `coins` count in
`webui`'s `/json`. Without persistence it drops back to zero; with
persistence it carries on.

Three things to know before changing these settings on a running release:

- **Switching `redis.kind` does not carry data across.** A `helm upgrade`
  that changes the kind deletes one workload and creates the other. The two
  kinds use different claims (`redis-data` and `data-redis-0`), so the new
  redis starts empty.
- **The Deployment's claim belongs to the release, but the StatefulSet's
  doesn't.** The chart creates `redis-data` itself, so `helm uninstall`,
  switching persistence off, or switching to StatefulSet deletes it and its
  data. A StatefulSet's claim is created by Kubernetes rather than by Helm,
  and it's left behind when the StatefulSet goes. Delete it yourself when
  you're done with the data (`kubectl delete pvc data-redis-0`). If you
  switch back to StatefulSet with persistence while it still exists, redis
  picks up the old data.
- **A Deployment shares one claim across all its pods.** That's fine for
  this chart's single redis replica, but it's the main reason stateful
  software that runs more than one replica uses a StatefulSet, which gives
  each pod a claim of its own.
