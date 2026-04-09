# Secrets Strategy (Do not commit plaintext)

For this repo, never commit real credentials in `.env`, `secret.yaml`, or Helm values.

## Recommended options

1. **Best (GitOps-friendly): External Secrets Operator**
   - Keep secrets in a secret manager (1Password, Doppler, Vault, AWS/GCP/Azure manager).
   - Sync into Kubernetes via `ExternalSecret` resources.
   - ArgoCD can deploy the manifests safely without embedding credentials.

2. **Good fallback: SOPS + age**
   - Keep encrypted secret manifests in git.
   - Decrypt only in CI/CD or cluster-side controller.

3. **Temporary dev only**
   - `kubectl create secret generic ...` manually.
   - Do not use this for shared or production environments.

## Practical mapping for TraceData

- `DATABASE_URL`
- `REDIS_URL`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `SLACK_WEBHOOK_URL`

## Immediate guardrails

- Add secret scanning in CI (gitleaks/trufflehog).
- Rotate any credential if it was ever committed.
- Use separate credentials per environment (`dev`, `staging`, `prod`).
