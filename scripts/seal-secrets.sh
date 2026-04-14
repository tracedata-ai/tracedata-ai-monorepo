#!/usr/bin/env bash
# =============================================================================
# seal-secrets.sh
# Encrypts plaintext secret.yaml files into SealedSecret CRDs using kubeseal.
#
# Prerequisites:
#   - kubeseal CLI installed and connected to the target cluster
#   - secret.yaml filled in from secret.yaml.example in each k8s service folder
#
# Usage:
#   1. cp k8s/tracedata-db/secret.yaml.example k8s/tracedata-db/secret.yaml
#      cp k8s/tracedata-api/secret.yaml.example k8s/tracedata-api/secret.yaml
#   2. Fill in real values in those files
#   3. ./scripts/seal-secrets.sh
#   4. git add k8s/**/sealed-secret.yaml && git commit
#
# The sealed-secret.yaml files are encrypted and safe to commit.
# The secret.yaml files are gitignored and must NEVER be committed.
# =============================================================================

set -euo pipefail

K8S_DIR="$(dirname "$0")/../k8s"

seal() {
  local dir="$1"
  local name
  name="$(basename "$dir")"

  if [ ! -f "$dir/secret.yaml" ]; then
    echo "  SKIP $name — no secret.yaml found"
    echo "       Copy from: $dir/secret.yaml.example"
    echo "       Fill in real values, then re-run this script."
    return
  fi

  echo "  Sealing $name..."
  kubeseal --format yaml < "$dir/secret.yaml" > "$dir/sealed-secret.yaml"
  echo "  OK: $dir/sealed-secret.yaml"
}

echo "==> Sealing secrets (requires kubeseal connected to target cluster)..."
echo ""

seal "$K8S_DIR/tracedata-db"
seal "$K8S_DIR/tracedata-api"

echo ""
echo "==> Done."
echo ""
echo "Next steps:"
echo "  1. Review the generated sealed-secret.yaml files"
echo "  2. Commit them — they are encrypted and safe to push:"
echo "       git add k8s/tracedata-db/sealed-secret.yaml k8s/tracedata-api/sealed-secret.yaml"
echo "  3. Delete the plaintext secret.yaml files from disk:"
echo "       rm k8s/tracedata-db/secret.yaml k8s/tracedata-api/secret.yaml"
