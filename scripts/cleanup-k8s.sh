#!/usr/bin/env bash
# =============================================================================
# cleanup-k8s.sh
# Removes all TraceData resources from the cluster.
# WARNING: This deletes PVCs and all data — use with caution.
# =============================================================================

set -euo pipefail

echo "WARNING: This will delete all tracedata resources including persistent volumes."
read -rp "Are you sure? (yes/no): " CONFIRM

if [[ "$CONFIRM" != "yes" ]]; then
  echo "Aborted."
  exit 0
fi

K8S_DIR="$(dirname "$0")/../k8s"

echo "==> Deleting application workloads..."
kubectl delete -f "$K8S_DIR/tracedata-frontend/" --ignore-not-found
kubectl delete -f "$K8S_DIR/tracedata-safety-worker/" --ignore-not-found
kubectl delete -f "$K8S_DIR/tracedata-scoring-worker/" --ignore-not-found
kubectl delete -f "$K8S_DIR/tracedata-support-worker/" --ignore-not-found
kubectl delete -f "$K8S_DIR/tracedata-sentiment-worker/" --ignore-not-found
kubectl delete -f "$K8S_DIR/tracedata-ingestion/" --ignore-not-found
kubectl delete -f "$K8S_DIR/tracedata-orchestrator/" --ignore-not-found
kubectl delete -f "$K8S_DIR/tracedata-api/" --ignore-not-found

echo "==> Deleting infrastructure (db + redis)..."
kubectl delete -f "$K8S_DIR/tracedata-redis/" --ignore-not-found
kubectl delete -f "$K8S_DIR/tracedata-db/" --ignore-not-found

echo "==> Deleting namespace..."
kubectl delete -f "$K8S_DIR/namespace.yaml" --ignore-not-found

echo ""
echo "==> Cleanup complete."
