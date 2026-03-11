# Commit Message Guidelines (Tracedata V1)

We use conventional commits formatted as: `TDATA-XX-TYPE(scope): Title Case Summary`

## 1. Components & Rules
- **Ticket (TDATA-XX):** Jira ticket number.
- **Type:** `FEAT` (new feature), `FIX` (bug), `DOCS` (documentation), `STYLE` (formatting), `REFACTOR` (code structure), `TEST` (tests), `CHORE` (maintenance), `PERF` (performance), `CI` (pipeline), `BUILD` (tooling), `REVERT`.
- **Scope:** `frontend`, `agents`, `infra`, `docs`. For multiple, use comma-separation (e.g. `agents,frontend`).
- **Title:** max 72 chars, Title Case, imperative mood ("Add feature", not "Added"), no ending period.
- **Body:** Leave one blank line. Wrap at 72 chars. Explain what and why.
- **Footer:** Use for `BREAKING CHANGE: <desc>` or closing tickets (`Closes TDATA-XX`).

## 2. Examples

```bash
TDATA-42-FEAT(frontend): Add Google OAuth Login Button
TDATA-08-FIX(agents): Handle Missing Telemetry Data
TDATA-50-REFACTOR(infra,agents): Update PostgreSQL Connection
```

## 3. Commitlint Config
Required scopes are enforced via standard configuration:

```javascript
// commitlint.config.js
module.exports = {
  // ...
  rules: {
    "type-enum": [2, "always", ["FEAT", "FIX", "DOCS", "STYLE", "REFACTOR", "TEST", "CHORE", "PERF", "CI", "BUILD", "REVERT"]],
    "scope-enum": [2, "always", ["frontend", "agents", "infra", "docs"]],
    "subject-case": [2, "always", "sentence-case"],
    "header-max-length": [2, "always", 72],
  },
};
```
