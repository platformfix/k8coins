{{/*
Chart name, honoring nameOverride.
*/}}
{{- define "k8coins.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels applied to every resource this chart creates. Deliberately
excludes app.kubernetes.io/part-of - that's already in selectorLabels
below, and every resource this chart creates also gets selectorLabels, so
adding it here too would just duplicate the same key.
*/}}
{{- define "k8coins.labels" -}}
helm.sh/chart: {{ printf "%s-%s" (include "k8coins.name" .) .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Selector labels for one of the four built services - kept separate from
the common labels above since selectors must never change across upgrades,
while the common labels (e.g. helm.sh/chart) do. Expects a dict with
"name" (the service name, e.g. "rng") and "root" (the top-level template
context, $) - called as: include "k8coins.selectorLabels" (dict "name" $name "root" $)
*/}}
{{- define "k8coins.selectorLabels" -}}
app.kubernetes.io/name: {{ .name }}
app.kubernetes.io/part-of: {{ include "k8coins.name" .root }}
{{- end -}}

{{/*
Image tag: explicit .Values.image.tag if set, else the chart's own
appVersion (kept in step with the app's release version by the release
workflow).
*/}}
{{- define "k8coins.tag" -}}
{{- .Values.image.tag | default .Chart.AppVersion -}}
{{- end -}}
