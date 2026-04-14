#!/usr/bin/env bash
# =============================================================================
# port-forward.sh
# Forwards local ports to services running in the cluster.
#
# Frontend:  http://localhost:3000
# API:       http://localhost:8000  (Swagger: http://localhost:8000/docs)
# ArgoCD UI: https://localhost:8080
# =============================================================================

set -euo pipefail

echo "==> Starting port forwards (Ctrl+C to stop all)..."

# Forward in background
kubectl port-forward svc/tracedata-frontend-service 3000:3000 -n tracedata &
PID_FRONTEND=$!

kubectl port-forward svc/tracedata-api-service 8000:8000 -n tracedata &
PID_API=$!

kubectl port-forward svc/argocd-server 8080:443 -n argocd &
PID_ARGOCD=$!

echo ""
echo "  Frontend:  http://localhost:3000"
echo "  API:       http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo "  ArgoCD UI: https://localhost:8080"
echo ""
echo "Press Ctrl+C to stop all port forwards."

# Wait and clean up on exit
trap "kill $PID_FRONTEND $PID_API $PID_ARGOCD 2>/dev/null; echo 'Port forwards stopped.'" EXIT
wait
