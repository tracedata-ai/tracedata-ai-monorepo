---
name: ci-patterns
description: >
  CI/CD pipeline patterns for the TraceData monorepo. Covers the design decisions,
  job structure, trigger logic, and security scan gates used across all GitHub Actions
  workflows. Read this before creating or modifying any .github/workflows/ file.
---

# TraceData CI Patterns

## HOW TO USE THIS SKILL

When asked to create or modify a CI workflow:
1. Read the relevant service file in this skill (`frontend.md`, etc.)
2. Follow the job structure, naming conventions, and security gates documented there
3. Reference `reference-repos` skill for upstream patterns (llmapp05 CI is the reference baseline)

---

## Core Principles

### 1. Parallel jobs, not sequential steps
Split independent checks into separate jobs so they run concurrently:
```
lint ──────────┐
type-check ────┼──► build ──► docker ──► summary
npm-audit ─────┘         └──► dast-zap
codeql-sast (independent)
```

### 2. Trigger strategy
| Branch type | What runs |
| :--- | :--- |
| `feature/**`, `hotfix/**` push | Lint + type-check + build + SCA only (fast feedback) |
| PR to `main` | + Docker build + Trivy scan + DAST + SAST (full gate, no push) |
| Merge to `main` | Everything above + Docker push to registry |

Enforce via job-level `if`:
```yaml
if: github.event_name == 'pull_request' || github.ref == 'refs/heads/main'
```

### 3. Never silence failures with `|| true`
```yaml
# ❌ WRONG — swallows real errors
run: npm run lint || true

# ✅ CORRECT — fails the job
run: npm run lint
```
Exception: security scan tools (`npm audit --json`, ZAP) may produce JSON reports
with non-zero exit codes. Write the report first, then assert the level separately.

### 4. Security scan gates
Every pipeline follows the **layered security model**:
```
SCA (dependency)  →  SAST (code)  →  Container scan  →  DAST (runtime)
   npm audit           CodeQL           Trivy               ZAP
  (blocks PR)      (informational)    (blocks push)    (informational)
```

- `npm audit --audit-level=high` → **hard gate** (blocks PR merge)
- `CodeQL` → `continue-on-error: true` (findings visible, not blocking)
- `Trivy` severity `CRITICAL,HIGH` → **hard gate** (blocks Docker push)
- `OWASP ZAP` → `continue-on-error: true` (informational, report uploaded)

### 5. Concurrency — cancel stale runs
Always include at the workflow level:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### 6. `paths` filter — only trigger on relevant changes
```yaml
paths:
  - "frontend/**"
  - ".github/workflows/ci-frontend.yaml"
```

### 7. Docker — single job, step-level visibility
Keep Docker as **one job** (`docker`) with named steps inside it.
Step-level `if` conditions control what runs on PRs vs main:
```yaml
- name: 🛡️ Trivy - Scan for CRITICAL & HIGH CVEs
  # always runs (no if)

- name: 🚀 Push Docker image
  if: github.event_name != 'pull_request'  # ← skipped on PRs, shown as grey
```

### 8. Summary job
Always include a summary job that runs `if: always()` and reports all job statuses
to `$GITHUB_STEP_SUMMARY` as a markdown table.

---

## Service Files

- [frontend.md](frontend.md) — Next.js + TypeScript frontend CI

---

## Required GitHub Secrets / Variables

| Name | Type | Used for |
| :--- | :--- | :--- |
| `vars.DOCKERHUB_USERNAME` | Repository Variable | Docker image namespace |
| `secrets.DOCKERHUB_TOKEN` | Repository Secret | Docker Hub push authentication |

**How to get `DOCKERHUB_TOKEN`:**
1. hub.docker.com → Account Settings → Security → New Access Token
2. Name: `tracedata-ci`, Permission: Read & Write
3. Add to: Repo Settings → Secrets and variables → Actions → Secrets
