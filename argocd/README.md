# ArgoCD GitOps Configuration

This directory contains the ArgoCD App-of-Apps configuration for TraceData AI.

## App-of-Apps Pattern

The root application (`applications/root-app.yaml`) watches this directory and
bootstraps all child applications automatically.

## Deployment Waves

| Wave | Services |
|---|---|
| 0 | tracedata-db, tracedata-redis |
| 10 | tracedata-api, tracedata-ingestion, tracedata-orchestrator |
| 20 | tracedata-safety-worker, tracedata-scoring-worker, tracedata-support-worker, tracedata-sentiment-worker |
| 30 | tracedata-frontend |

## Bootstrap

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Bootstrap the root app
kubectl apply -f argocd/applications/root-app.yaml

# Get the initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Access the ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Open: https://localhost:8080
```

## Sync Policy

All applications are configured with:
- **Automated sync**: ArgoCD polls Git every 3 minutes and applies changes
- **Self-healing**: Reverts manual kubectl changes to match Git
- **Pruning**: Deletes resources removed from Git
- **Retry**: 5 attempts with exponential backoff (5s → 3min max)
