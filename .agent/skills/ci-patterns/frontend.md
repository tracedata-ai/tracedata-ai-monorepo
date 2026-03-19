# Frontend CI — Next.js + TypeScript

**Workflow file:** `.github/workflows/ci-frontend.yaml`
**Triggers:** Push to `main`/`feature/**`/`hotfix/**` (paths: `frontend/**`), PR to `main`

---

## Job Map

```
lint          ──────────────────┐
type-check    ──────────────────┤──► build ──► docker   (PR/main only)
npm-audit     ──────────────────┘         └──► dast-zap (PR/main only)
codeql-sast                               (PR/main only, independent)
                                               └──► summary
```

## Jobs

### `lint` — ESLint
- Tool: `npm run lint`
- Trigger: all pushes + PRs
- **Hard gate** — never use `|| true`

### `type-check` — TypeScript
- Tool: `npx tsc --noEmit`
- Trigger: all pushes + PRs
- **Hard gate**

### `npm-audit` — Dependency SCA
- Tool: `npm audit --json > npm-audit.json` (report) then `npm audit --audit-level=high` (gate)
- Trigger: all pushes + PRs
- Report uploaded as artifact (`npm-audit-report`, 7 days)
- **Hard gate at HIGH severity**

### `build` — Production bundle
- Tool: `npm run build`
- Needs: `lint`, `type-check`
- Trigger: all pushes + PRs

### `codeql-sast` — Static analysis
- Tool: `github/codeql-action` (javascript-typescript)
- Trigger: PR + main only (`if: github.event_name == 'pull_request' || github.ref == 'refs/heads/main'`)
- `continue-on-error: true` — informational, does not block
- Needs: nothing (runs independently)

### `docker` — Build + Scan + Push (single job)
- Trigger: PR + main only
- Needs: `build`
- **Steps (always run):**
  - `🐳 Build Docker image` — builds `tracedata-frontend:scan`, caches layers in GHA
  - `🛡️ Trivy - Scan for CRITICAL & HIGH CVEs` — **hard gate**, fails job if found
- **Steps (skipped on PRs via `if: github.event_name != 'pull_request'`):**
  - `Extract Docker metadata` — sha, branch, semver, latest tags
  - `Login to Docker Hub` — uses `vars.DOCKERHUB_USERNAME` + `secrets.DOCKERHUB_TOKEN`
  - `🚀 Push Docker image` — pushes with all tags

**Why one job, not three?**
GitHub Actions UI shows step names within a job as individual line items (like lint steps).
Three separate jobs would create three job cards. One job keeps Docker visually contained
and avoids re-building the image across job boundaries.

### `dast-zap` — Dynamic security scan
- Tool: `ghcr.io/zaproxy/zaproxy:stable` ZAP baseline scan
- Trigger: PR + main only
- Needs: `build`
- `continue-on-error: true` — informational
- Starts Next.js production server (`npm run start -- -p 3000`), polls readiness, then scans
- Report uploaded as artifact (`zap-report`, 7 days)

### `unit-test` — (scaffold, currently commented out)
- Uncomment when tests are added
- Tools: `npm run test` + `npm run test:coverage`
- Coverage uploaded as artifact

### `summary` — Pipeline report
- `if: always()` — runs regardless of other job results
- Needs: all jobs above
- Writes markdown table to `$GITHUB_STEP_SUMMARY`

---

## Key Design Decisions

| Decision | Rationale |
| :--- | :--- |
| `feature/**` pushes skip Docker | No staging env — no reason to build/push on every commit |
| Trivy before Docker push | Structurally impossible to push a vulnerable image |
| ZAP `continue-on-error` | DAST findings need human review, not auto-block |
| CodeQL `continue-on-error` | Free tier SAST — informational at this stage |
| Single Docker job | Cleaner UI, no image rebuild across job boundaries |
| `paths` filter | Avoids CI runs when only backend/docs change |

---

## Node.js Caching Pattern

Each job that needs Node.js caches `~/.npm` via `setup-node`:
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: "20"
    cache: "npm"
    cache-dependency-path: frontend/package-lock.json
```
Each job still runs `npm ci` — the cache makes this fast (~10s vs ~60s cold).

---

## Reference
- Upstream CI pattern: `darryl1975/llmapp05` `.github/workflows/llm-frontend-python-ci.yml`
- Security scan additions: Previous project CI (OWASP ZAP, CodeQL, npm audit artifact)
- Container scan: `darryl1975/llmapp05` Trivy integration adapted for Next.js
