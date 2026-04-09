# DigitalOcean Infra (ArgoCD + Helm)

This folder is the deployment scaffold for running TraceData on DOKS with ArgoCD and Helm.

## Structure

- `argocd/root-app.yaml`: app-of-apps root.
- `argocd/apps/`: ArgoCD applications managed by the root app.
- `charts/tracedata/`: umbrella Helm chart (frontend, api, workers, ingress, hpa).
- `secrets/`: examples only; never store plaintext secrets in git.
- `SECRETS.md`: canonical secrets handling policy.

## Intended flow

1. CI builds and pushes images:
   - `tracedata-frontend`
   - `tracedata-backend-agent-api`
2. Update image tags in Helm values (or automate via image updater).
3. ArgoCD syncs chart to DOKS.

## Notes

- This is a clean starting point for your colleague to extend.
- Current chart templates are intentionally minimal and safe defaults.
- Keep production secrets out of this repo.

