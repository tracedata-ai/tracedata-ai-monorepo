# DigitalOcean Infra (ArgoCD + Helm)

This folder is the deployment scaffold for running TraceData on DOKS with ArgoCD and Helm.

## Structure

- `argocd/root-app.yaml`: app-of-apps root.
- `argocd/apps/`: ArgoCD applications managed by the root app.
- `charts/tracedata/`: umbrella Helm chart (frontend, api, workers, ingress, hpa).
- `secrets/`: example manifests only; never store plaintext secrets in git.
- `SECRETS.md`: canonical secrets handling policy.

## Intended flow

1. CI builds and pushes images:
   - `tracedata-frontend`
   - `tracedata-backend-agent-api`
2. Update image tags in Helm values (or automate via image updater).
3. ArgoCD syncs chart to DOKS.

## ArgoCD apps in this scaffold

Apps are intentionally split to match production dependencies and sync wave order:

- `external-secrets.yaml` (wave 0)
- `monitoring-kube-prometheus-stack.yaml` (wave 1)
- `monitoring-loki.yaml` (wave 1)
- `monitoring-promtail.yaml` (wave 2)
- `tracedata-postgres.yaml` (wave 1)
- `tracedata-redis.yaml` (wave 1)
- `tracedata-platform.yaml` (wave 3)

## DOKS Architecture (self-explanatory)

### 1) Platform overview

```mermaid
flowchart TB
  subgraph GitHub["GitHub"]
    APP["tracedata-ai-monorepo\n(app code + CI)"]
    INFRA["infra/do\n(Helm + ArgoCD manifests)"]
  end

  REG["Docker Registry\n(Docker Hub / DOCR)"]

  subgraph DOKS["DigitalOcean Kubernetes (DOKS)"]
    ARGO["ArgoCD\n(app-of-apps)"]
    subgraph NS["namespace: tracedata"]
      FE["frontend Deployment + Service"]
      API["api Deployment + Service"]
      ING["ingestion Deployment"]
      ORC["orchestrator Deployment"]
      SAF["safety-worker Deployment"]
      SCO["scoring-worker Deployment"]
      SUP["support-worker Deployment"]
      SEN["sentiment-worker Deployment"]
      INGR["NGINX Ingress + TLS"]
    end
  end

  APP -->|"build/push images"| REG
  INFRA -->|"desired state"| ARGO
  ARGO -->|"sync chart"| NS
  REG --> FE
  REG --> API
  REG --> ING
  REG --> ORC
  REG --> SAF
  REG --> SCO
  REG --> SUP
  REG --> SEN
  INGR --> FE
  INGR --> API
```

### 2) Runtime request and processing flow

```mermaid
flowchart LR
  U["User / Browser"] -->|"HTTPS"| INGR["Ingress"]
  INGR --> FE["Frontend"]
  FE -->|"REST/WebSocket"| API["API"]
  API --> PG["PostgreSQL"]
  API --> RD["Redis"]

  DEV["Vehicle telemetry"] --> RD
  RD --> ING["Ingestion"]
  ING --> PG
  ING --> ORC["Orchestrator"]
  ORC --> SAF["Safety worker"]
  ORC --> SCO["Scoring worker"]
  ORC --> SUP["Support worker"]
  ORC --> SEN["Sentiment worker"]
  SAF --> RD
  SCO --> PG
  SUP --> RD
  SEN --> RD
```

### 3) GitOps deployment flow (ArgoCD)

```mermaid
sequenceDiagram
  participant Dev as Developer
  participant Repo as GitHub (infra/do)
  participant Argo as ArgoCD
  participant K8s as DOKS Cluster
  participant Reg as Docker Registry

  Dev->>Repo: Commit Helm/Argo changes
  Dev->>Reg: Push new images (sha/latest)
  Argo->>Repo: Poll targetRevision
  Argo->>K8s: Apply synced manifests
  K8s->>Reg: Pull image tags
  K8s-->>Argo: Health + sync status
```

### 4) Observability / PLG-ready flow

```mermaid
flowchart TB
  API["API /metrics"] --> PROM["Prometheus"]
  FE["Frontend /api/metrics"] --> PROM
  ORC["Workers + orchestrator metrics"] --> PROM

  API -. stdout logs .-> LOKI["Loki"]
  FE -. stdout logs .-> LOKI
  ORC -. stdout logs .-> LOKI

  PROM --> GRAF["Grafana"]
  LOKI --> GRAF
  GRAF --> OPS["Ops / Team dashboards"]
```

## Why this layout

- **App and infra are separated**: app repo builds images; infra folder defines runtime state.
- **ArgoCD is source-of-truth sync**: cluster converges to Git state, reducing drift.
- **Workers are independently scalable**: tune replicas by agent role, not one monolith.
- **Observability is first-class**: metrics endpoints and log streams are ready for PLG in DOKS.

## Quick bootstrap checklist

1. Install ArgoCD in cluster.
2. Apply `infra/do/argocd/root-app.yaml`.
3. Apply one real `ClusterSecretStore` (template in `infra/do/secrets`).
4. Create data-chart auth secrets (`tracedata-postgres-auth`, `tracedata-redis-auth`).
5. Set real ingress DNS names in `charts/tracedata/values.yaml`.
6. Set real image repositories/tags in `charts/tracedata/values.yaml`.
7. Verify:
   - backend metrics: `/metrics`
   - frontend metrics: `/api/metrics`
   - ServiceMonitors discovered by Prometheus
   - logs visible in Loki/Grafana

## Notes

- Current chart templates are intentionally minimal and safe defaults.
- Keep production secrets out of this repo.

