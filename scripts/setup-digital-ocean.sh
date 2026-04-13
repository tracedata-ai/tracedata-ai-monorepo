#!/usr/bin/env bash
# =============================================================================
# setup-digital-ocean.sh
# Full TraceData AI cluster bootstrap on DigitalOcean Kubernetes (DOKS).
#
# What this script does (in order):
#   1.  Create DOKS cluster
#   2.  Install nginx-ingress  → provisions the DO Load Balancer (gets public IP)
#   3.  Install cert-manager   → automatic Let's Encrypt TLS
#   4.  Apply ClusterIssuers   → staging + prod Let's Encrypt
#   5.  Install kube-prometheus-stack  → Prometheus + Grafana + AlertManager
#   6.  Install Loki           → log aggregation
#   7.  Install Promtail       → log shipper (DaemonSet on every node)
#   8.  Apply monitoring Ingress
#   9.  Install ArgoCD
#   10. Apply ArgoCD Ingress
#   11. Install Sealed Secrets controller
#   12. Seal secrets (requires plaintext secret.yaml files to be filled in)
#   13. Bootstrap ArgoCD root application
#   14. Apply main app Ingress (www + api)
#   15. Print load balancer IP  → update Namecheap A records to this IP
#
# Prerequisites:
#   - doctl CLI authenticated (doctl auth init)
#   - kubectl installed
#   - helm installed
#   - kubeseal installed (brew install kubeseal)
#   - Plaintext secret.yaml files filled in:
#       k8s/tracedata-db/secret.yaml  (from secret.yaml.example)
#       k8s/tracedata-api/secret.yaml (from secret.yaml.example)
#   - CHANGE_ME_EMAIL replaced in k8s/cert-manager/cluster-issuer.yaml
#   - CHANGE_ME_GRAFANA_PASSWORD replaced in k8s/monitoring/prometheus-values.yaml
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ── Config (edit these) ───────────────────────────────────────────────────────
CLUSTER_NAME="tracedata-cluster"
REGION="sgp1"
NODE_SIZE="s-2vcpu-4gb"
NODE_COUNT=3
K8S_VERSION=""  # Leave empty to auto-pick latest, or set e.g. "1.31.6-do.1"
                # Run: doctl kubernetes options versions

# =============================================================================
# 1. Create DOKS cluster
# =============================================================================
echo ""
echo "━━━ [1/15] Creating DOKS cluster: $CLUSTER_NAME in $REGION ━━━"

# Resolve version slug — use provided value or auto-pick latest stable
if [ -z "$K8S_VERSION" ]; then
  K8S_VERSION=$(doctl kubernetes options versions | awk 'NR==2{print $1}')
  echo "==> Auto-selected Kubernetes version: $K8S_VERSION"
fi

doctl kubernetes cluster create "$CLUSTER_NAME" \
  --region "$REGION" \
  --node-pool "name=worker;size=$NODE_SIZE;count=$NODE_COUNT" \
  --version "$K8S_VERSION" \
  --wait

echo "==> Saving kubeconfig..."
doctl kubernetes cluster kubeconfig save "$CLUSTER_NAME"
kubectl get nodes

# =============================================================================
# 2. Install nginx-ingress  (provisions the DigitalOcean Load Balancer)
# =============================================================================
echo ""
echo "━━━ [2/15] Installing nginx-ingress ━━━"
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer \
  --wait

echo "==> nginx-ingress installed. DO Load Balancer is being provisioned..."

# =============================================================================
# 3. Install cert-manager
# =============================================================================
echo ""
echo "━━━ [3/15] Installing cert-manager ━━━"
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true \
  --wait

# =============================================================================
# 4. Apply ClusterIssuers (Let's Encrypt staging + prod)
# =============================================================================
echo ""
echo "━━━ [4/15] Applying ClusterIssuers ━━━"
kubectl apply -f "$REPO_ROOT/k8s/cert-manager/cluster-issuer.yaml"

# =============================================================================
# 5. Install kube-prometheus-stack (Prometheus + Grafana + AlertManager)
# =============================================================================
echo ""
echo "━━━ [5/15] Installing kube-prometheus-stack ━━━"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  -f "$REPO_ROOT/k8s/monitoring/prometheus-values.yaml" \
  --wait

# =============================================================================
# 6. Install Loki
# =============================================================================
echo ""
echo "━━━ [6/15] Installing Loki ━━━"
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm install loki grafana/loki \
  --namespace monitoring \
  -f "$REPO_ROOT/k8s/monitoring/loki-values.yaml" \
  --wait

# =============================================================================
# 7. Install Promtail (log shipper DaemonSet)
# =============================================================================
echo ""
echo "━━━ [7/15] Installing Promtail ━━━"
helm install promtail grafana/promtail \
  --namespace monitoring \
  -f "$REPO_ROOT/k8s/monitoring/promtail-values.yaml" \
  --wait

# =============================================================================
# 8. Apply monitoring Ingress
# =============================================================================
echo ""
echo "━━━ [8/15] Applying monitoring Ingress ━━━"
kubectl apply -f "$REPO_ROOT/k8s/monitoring/ingress.yaml"

# =============================================================================
# 9. Install ArgoCD
# =============================================================================
echo ""
echo "━━━ [9/15] Installing ArgoCD ━━━"
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd

# =============================================================================
# 10. Apply ArgoCD Ingress
# =============================================================================
echo ""
echo "━━━ [10/15] Applying ArgoCD Ingress ━━━"
kubectl apply -f "$REPO_ROOT/argocd/ingress.yaml"

# =============================================================================
# 11. Install Sealed Secrets controller
# =============================================================================
echo ""
echo "━━━ [11/15] Installing Sealed Secrets controller ━━━"
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/latest/download/controller.yaml
kubectl wait --for=condition=available --timeout=120s deployment/sealed-secrets-controller -n kube-system

# =============================================================================
# 12. Seal secrets
# =============================================================================
echo ""
echo "━━━ [12/15] Sealing secrets ━━━"
chmod +x "$SCRIPT_DIR/seal-secrets.sh"
"$SCRIPT_DIR/seal-secrets.sh"

# =============================================================================
# 13. Bootstrap ArgoCD root application
# =============================================================================
echo ""
echo "━━━ [13/15] Bootstrapping ArgoCD root application ━━━"
kubectl apply -f "$REPO_ROOT/argocd/applications/root-app.yaml"

# =============================================================================
# 14. Apply main app Ingress
# =============================================================================
echo ""
echo "━━━ [14/15] Applying main app Ingress ━━━"
kubectl apply -f "$REPO_ROOT/k8s/namespace.yaml"
kubectl apply -f "$REPO_ROOT/k8s/ingress.yaml"

# =============================================================================
# 15. Print load balancer IP + next steps
# =============================================================================
echo ""
echo "━━━ [15/15] Getting Load Balancer IP ━━━"
echo "Waiting for Load Balancer IP to be assigned..."
sleep 10
LB_IP=$(kubectl get svc ingress-nginx-controller -n ingress-nginx \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  CLUSTER READY"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "  Load Balancer IP: $LB_IP"
echo ""
echo "  Update ALL Namecheap A records to point to: $LB_IP"
echo "    api           → $LB_IP"
echo "    argo.tools    → $LB_IP"
echo "    grafana.tools → $LB_IP"
echo "    loki.tools    → $LB_IP"
echo "    prom.tools    → $LB_IP"
echo "    www           → $LB_IP"
echo "    dev           → $LB_IP"
echo "    staging       → $LB_IP"
echo ""
echo "  Once DNS propagates:"
echo "    Frontend:  https://www.xplore.town"
echo "    API:       https://api.xplore.town/docs"
echo "    ArgoCD:    https://argo.tools.xplore.town"
echo "    Grafana:   https://grafana.tools.xplore.town"
echo "    Prometheus:https://prom.tools.xplore.town"
echo "    Loki:      https://loki.tools.xplore.town"
echo ""
echo "  ArgoCD admin password:"
echo "    kubectl -n argocd get secret argocd-initial-admin-secret \\"
echo "      -o jsonpath='{.data.password}' | base64 -d"
echo ""
echo "  Commit the generated sealed-secret.yaml files:"
echo "    git add k8s/tracedata-db/sealed-secret.yaml \\"
echo "            k8s/tracedata-api/sealed-secret.yaml"
echo "════════════════════════════════════════════════════════════════"
