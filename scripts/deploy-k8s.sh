#!/usr/bin/env bash
# =============================================================================
# deploy-k8s.sh
# Applies all k8s manifests directly (without ArgoCD).
# Use this for Minikube or manual deployments.
# =============================================================================

set -euo pipefail

K8S_DIR="$(dirname "$0")/../k8s"

echo "==> Applying namespace..."
kubectl apply -f "$K8S_DIR/namespace.yaml"

echo "==> Deploying infrastructure (db + redis)..."
kubectl apply -f "$K8S_DIR/tracedata-db/"
kubectl apply -f "$K8S_DIR/tracedata-redis/"

echo "==> Waiting for db to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/tracedata-db -n tracedata
kubectl wait --for=condition=available --timeout=60s deployment/tracedata-redis -n tracedata

echo "==> Deploying backend services..."
kubectl apply -f "$K8S_DIR/tracedata-api/"
kubectl apply -f "$K8S_DIR/tracedata-ingestion/"
kubectl apply -f "$K8S_DIR/tracedata-orchestrator/"

echo "==> Deploying Celery workers..."
kubectl apply -f "$K8S_DIR/tracedata-safety-worker/"
kubectl apply -f "$K8S_DIR/tracedata-scoring-worker/"
kubectl apply -f "$K8S_DIR/tracedata-support-worker/"
kubectl apply -f "$K8S_DIR/tracedata-sentiment-worker/"

echo "==> Deploying frontend..."
kubectl apply -f "$K8S_DIR/tracedata-frontend/"

echo ""
echo "==> All resources applied. Checking pod status..."
kubectl get pods -n tracedata

echo ""
echo "Run scripts/port-forward.sh to access services locally."
