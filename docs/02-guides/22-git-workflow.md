# Git Workflow (Trunk-Based Development)

TraceData uses Trunk-Based Development with a CI-validated, always-deployable `main` branch.

## 1. Core Principles
- **Main is sacred:** Every commit triggers CI/CD. The branch is always production-ready.
- **Short-lived branches:** Feature branches live for **1-2 days** max. Merge small, incremental changes frequently.
- **Feature flags:** Merge incomplete features to `main` hidden behind flags, instead of hoarding long-lived branches.

## 2. Branch Hierarchy

| Prefix | Purpose | Lifetime | Protected? | Target | Merge Rule |
|---|---|---|---|---|---|
| `main` | Production trunk | Permanent | Yes | N/A | Direct pushes blocked |
| `feature/` | Standard development | 1-2 days | No | `main` | Squash merge, 1 approval, CI passed |
| `hotfix/` | Critical prod bugs | Hours | No | `main` | Squash merge, 1 fast-track approval, CI passed |
| `experiment/`| Spikes & PoCs | 1-7 days | No | N/A | Convert to feature branch prior to merging |

*Note: No `develop`, `release`, or `staging` branches exist. We deploy `main` directly.*

## 3. Branch Naming Convention

**Format:** `<type>/<scope>-<ticket>-<short-description>`
- Use kebab-case. Description should be 2-4 words. Scope must match `frontend`, `agents`, `infra`, or `docs`.
- **Examples:** `feature/frontend-42-login-page`, `hotfix/agents-99-telemetry-fix`.

## 4. Work Lifecycle (Feature)

1. `git checkout main && git pull`
2. `git checkout -b feature/frontend-42-login`
3. Commit small increments locally, pushing daily for backup.
4. `git fetch origin && git rebase origin/main` to sync before PR.
5. Create Pull Request (keep PRs under 300 LOC changed).
6. Await CI pass and 1 teammate approval.
7. Click "Squash and Merge".
8. Delete branch immediately after merging.

## 5. Releases & Deployments

- **Continuous Deployment:** Merging to `main` auto-deploys to staging. Manual approval triggers production deployment.
- **Sprints & Tags:** Create a semver git tag (e.g. `v1.2.0`) at sprint boundaries for GitHub Releases.
