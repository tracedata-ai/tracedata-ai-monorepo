# Scripts

Helper scripts for deploying TraceData AI to Kubernetes.

## Scripts

| Script | Purpose |
|---|---|
| `setup-digital-ocean.sh` | Create DOKS cluster, install ArgoCD + Sealed Secrets, bootstrap GitOps |
| `seal-secrets.sh` | Encrypt plaintext secret.yaml files into SealedSecrets (safe to commit) |
| `deploy-k8s.sh` | Apply all manifests directly (Minikube / manual, no ArgoCD) |
| `port-forward.sh` | Forward frontend (3000), API (8000), ArgoCD UI (8080) |
| `cleanup-k8s.sh` | Delete all TraceData resources and PVCs |

---

## Secret Management (Sealed Secrets)

Secrets follow a two-file pattern per service:

```
k8s/tracedata-api/
  secret.yaml.example   ← tracked in Git (template with placeholder values)
  secret.yaml           ← gitignored (plaintext — fill in real values locally)
  sealed-secret.yaml    ← tracked in Git (encrypted by kubeseal — safe to commit)
```

### One-time setup

Install `kubeseal` locally:
```bash
# macOS
brew install kubeseal

# Linux
KUBESEAL_VERSION=$(curl -s https://api.github.com/repos/bitnami-labs/sealed-secrets/releases/latest | jq -r '.tag_name')
curl -OL "https://github.com/bitnami-labs/sealed-secrets/releases/download/${KUBESEAL_VERSION}/kubeseal-${KUBESEAL_VERSION#v}-linux-amd64.tar.gz"
tar -xvzf kubeseal-*.tar.gz kubeseal
sudo install -m 755 kubeseal /usr/local/bin/kubeseal
```

### Sealing secrets workflow

```bash
# 1. Copy templates
cp k8s/tracedata-db/secret.yaml.example k8s/tracedata-db/secret.yaml
cp k8s/tracedata-api/secret.yaml.example k8s/tracedata-api/secret.yaml

# 2. Fill in real values in both files

# 3. Seal (requires kubeseal connected to the target cluster)
./scripts/seal-secrets.sh

# 4. Commit the sealed files
git add k8s/tracedata-db/sealed-secret.yaml k8s/tracedata-api/sealed-secret.yaml

# 5. Delete the plaintext files from disk
rm k8s/tracedata-db/secret.yaml k8s/tracedata-api/secret.yaml
```

ArgoCD will deploy the `sealed-secret.yaml` files. The Sealed Secrets controller
decrypts them inside the cluster into native Kubernetes Secrets — your pods never
see anything but a normal `Secret`.

---

## Quick Start: DigitalOcean (production)

```bash
# 1. Authenticate
doctl auth init

# 2. Fill in plaintext secrets (see above)
cp k8s/tracedata-db/secret.yaml.example k8s/tracedata-db/secret.yaml
cp k8s/tracedata-api/secret.yaml.example k8s/tracedata-api/secret.yaml
# ... fill in values ...

# 3. Create cluster + install ArgoCD + Sealed Secrets + bootstrap GitOps
#    (automatically runs seal-secrets.sh as part of setup)
chmod +x scripts/setup-digital-ocean.sh
./scripts/setup-digital-ocean.sh

# 4. Commit the generated sealed-secret.yaml files
git add k8s/tracedata-db/sealed-secret.yaml k8s/tracedata-api/sealed-secret.yaml
git commit -m "TDATA-XX-FEAT(k8s): Add sealed secrets"
git push
```

## Quick Start: Minikube (local)

```bash
# 1. Start Minikube
minikube start

# 2. Edit storage class to 'standard' in:
#    k8s/tracedata-db/pvc.yaml
#    k8s/tracedata-redis/pvc.yaml

# 3. Install Sealed Secrets controller in Minikube
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/latest/download/controller.yaml

# 4. Seal secrets
cp k8s/tracedata-db/secret.yaml.example k8s/tracedata-db/secret.yaml
cp k8s/tracedata-api/secret.yaml.example k8s/tracedata-api/secret.yaml
# ... fill in values ...
./scripts/seal-secrets.sh

# 5. Apply all manifests
chmod +x scripts/deploy-k8s.sh
./scripts/deploy-k8s.sh

# 6. Forward ports
chmod +x scripts/port-forward.sh
./scripts/port-forward.sh
```

---

## Image Names

Update `DOCKERHUB_USERNAME` in all `k8s/**/deployment.yaml` files to your Docker Hub username.
CI workflows push images as:
- `DOCKERHUB_USERNAME/tracedata-backend-agent-api:sha-<commit>`
- `DOCKERHUB_USERNAME/tracedata-frontend:sha-<commit>`
