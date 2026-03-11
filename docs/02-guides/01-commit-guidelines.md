# Tracedata V1 - Commit Message Guidelines

This document defines the commit message standards for Tracedata V1 monorepo.

## Table of Contents

1. [Commit Message Format](#1-commit-message-format)
   - [Structure](#structure)
   - [Components](#components)
2. [Commit Types](#2-commit-types)
3. [Scope Guidelines](#3-scope-guidelines)
   - [Available Scopes](#available-scopes)
   - [Single Scope](#single-scope)
   - [Multiple Scopes](#multiple-scopes)
4. [Writing the Title](#4-writing-the-title)
   - [Rules](#rules)
   - [Good Examples](#good-examples)
   - [Bad Examples](#bad-examples)
5. [Commit Body (Optional)](#5-commit-body-optional)
   - [When to Add Body](#when-to-add-body)
   - [Format](#format)
   - [Example](#example)
6. [Breaking Changes](#6-breaking-changes)
   - [What is a Breaking Change?](#what-is-a-breaking-change)
   - [Format](#format-1)
   - [Branch Naming for Breaking Changes (Optional)](#branch-naming-for-breaking-changes-optional)
7. [Footer References](#7-footer-references)
   - [Closing Issues](#closing-issues)
   - [Related Issues](#related-issues)
8. [Complete Examples](#8-complete-examples)
9. [Common Mistakes](#9-common-mistakes)
10. [Verification Checklist](#10-verification-checklist)
11. [Tools & Automation](#11-tools--automation)
    - [Pre-Commit Hook (Optional)](#pre-commit-hook-optional)
    - [Commitlint Configuration](#commitlint-configuration)
12. [Related Documentation](#12-related-documentation)

---

## 1. Commit Message Format

### Structure

```
TDATA-XX-TYPE(scope): Title Case Summary

Optional body with detailed explanation

Optional footer with breaking changes or issue references
```

### Components

| Component    | Required | Description                              | Example            |
| ------------ | -------- | ---------------------------------------- | ------------------ |
| **TDATA-XX** | Yes      | Jira ticket number                       | `TDATA-42`         |
| **TYPE**     | Yes      | Change category (UPPERCASE)              | `FEAT`, `FIX`      |
| **(scope)**  | Yes      | Target directory (lowercase)             | `(user)`, `(auth)` |
| **Title**    | Yes      | Short summary (Title Case, max 72 chars) | Add Google Login   |
| **Body**     | Optional | Detailed explanation                     | See body section   |
| **Footer**   | Optional | Breaking changes, issue references       | See footer section |

---

## 2. Commit Types

| Type       | When to Use                                      | Example                             |
| ---------- | ------------------------------------------------ | ----------------------------------- |
| `FEAT`     | Adding a new feature                             | Add OAuth login                     |
| `FIX`      | Fixing a bug                                     | Fix JWT expiry handling             |
| `DOCS`     | Documentation only changes                       | Update API documentation            |
| `STYLE`    | Code formatting, missing semicolons (no logic)   | Format code with Prettier           |
| `REFACTOR` | Code change that neither fixes bug nor adds feat | Extract validation logic to service |
| `TEST`     | Adding or updating tests                         | Add unit tests for AuthService      |
| `CHORE`    | Maintenance tasks, dependency updates            | Upgrade Spring Boot to 3.2          |
| `PERF`     | Performance improvements                         | Optimize database queries           |
| `CI`       | CI/CD configuration changes                      | Update GitHub Actions workflow      |
| `BUILD`    | Build system or dependencies                     | Configure Turborepo cache           |
| `REVERT`   | Reverting a previous commit                      | Revert "Add feature X"              |

---

## 3. Scope Guidelines

Scope identifies **which part of the monorepo** is affected.

### Available Scopes

See [CONTRIBUTING.md](./CONTRIBUTING.md#scope-table) for complete scope table.

**Quick Reference:**

- `user` - Customer booking app
- `fleet-ui` - Fleet management UI
- `admin` - Admin dashboard
- `auth` - Auth microservice
- `fleet` - Fleet microservice
- `booking` - Booking microservice
- `ui` - Shared UI components
- `utils` - Shared utilities
- `common` - Shared Java code
- `infra` - Infrastructure, CI/CD, Docker

### Single Scope

Use when change is **clearly owned by one area**:

```bash
TDATA-42-FEAT(user): Add Google Login Button
TDATA-08-FIX(auth): Handle Null JWT Claims
TDATA-33-REFACTOR(ui): Migrate Button to Tailwind v4
```

### Multiple Scopes

Use comma-separated scopes when change **spans multiple areas equally**:

```bash
# Backend API + Frontend integration
TDATA-42-FEAT(auth,user): Add Google OAuth Login Flow

# Shared component + consumer app
TDATA-50-REFACTOR(ui,fleet-ui): Update DatePicker Component

# Cross-service change
TDATA-60-FEAT(fleet,booking): Add Vehicle Availability Check
```

**Rule:** If unsure, use the **primary** scope (the area with most changes).

---

## 4. Writing the Title

### Rules

- Use **Title Case** (capitalize first letter of each major word)
- Use **imperative mood** ("Add feature" not "Added feature")
- **Maximum 72 characters** (including Jira ticket and scope)
- **No period** at the end
- Avoid vague titles like "Fix bug" or "Update code"

### Good Examples

```bash
TDATA-42-FEAT(user): Add Google OAuth Login Button
TDATA-08-FIX(auth): Handle Null JWT Claims Gracefully
TDATA-33-REFACTOR(ui): Extract Button Styles to Tailwind
TDATA-99-CHORE(infra): Upgrade Node.js to v20
```

### Bad Examples

```bash
TDATA-42-FEAT(user): login          # Too vague
TDATA-08-FIX(auth): fixed the bug   # Not imperative, lowercase
TDATA-33-REFACTOR(ui): Updated button component styles and colors  # Too long
TDATA-99-CHORE(infra): stuff        # Meaningless
```

---

## 5. Commit Body (Optional)

Use the body to explain **what** and **why**, not **how** (code shows how).

### When to Add Body

- Complex change needing explanation
- Multiple files changed with different purposes
- Non-obvious decision or trade-off made
- Context helpful for future developers

### Format

- Leave **one blank line** after title
- Wrap at **72 characters** per line
- Use **bullet points** for multiple items
- Focus on **motivation** and **context**

### Example

```bash
TDATA-42-FEAT(fleet): Add Vehicle Inspection Form

- Added InspectionForm component with React Hook Form
- Integrated with fleet-service POST /inspections endpoint
- Added Zod schema validation (mirrors backend validation)
- Updated FleetVehicle model to include lastInspectionDate

This form is required for regulatory compliance in Singapore.
Operators must complete inspections every 6 months.
```

---

## 6. Breaking Changes

### What is a Breaking Change?

A change that **requires other code to be updated** to continue working:

- API endpoint changes (URL, method, request/response structure)
- Database schema changes (column renames, deletions)
- Configuration changes (environment variables renamed)
- Contract changes between services

### Format

Add `BREAKING CHANGE:` in commit **footer**:

```bash
TDATA-50-FEAT(auth): Change JWT Structure

Migrate JWT from 'sub' claim to 'userId' claim for consistency
across all services. This improves clarity and follows our
internal API standards.

BREAKING CHANGE: JWT token structure changed. All services
consuming auth-service tokens must update JWT validation to
use 'userId' claim instead of 'sub' claim. Migration guide
available at docs/migrations/jwt-structure-v2.md
```

### Branch Naming for Breaking Changes (Optional)

Add `!` to indicate breaking change:

```bash
feat/TDATA-50-Setup-Example  # Breaking change
```

---

## 7. Footer References

### Closing Issues

Use footer to close Jira tickets:

```bash
TDATA-42-FEAT(user): Add Login Page

Closes TDATA-42
```

Or multiple tickets:

```bash
TDATA-42-FEAT(user,auth): Add OAuth Login Flow

Closes TDATA-42, TDATA-43
```

### Related Issues

Reference related tickets without closing:

```bash
TDATA-55-FIX(booking): Fix Date Validation Logic

Related to TDATA-50, TDATA-52
```

---

## 8. Complete Examples

### Example 1: Simple Feature

```bash
TDATA-42-FEAT(user): Add Google Login Button
```

### Example 2: Bug Fix with Body

```bash
TDATA-08-FIX(auth): Handle Null JWT Claims

JWT validation was failing when 'roles' claim was missing,
causing 500 errors for users with incomplete profiles.

Added null check and default to empty array if roles claim
is missing. This matches behavior of other services.

Closes TDATA-08
```

### Example 3: Refactoring with Explanation

```bash
TDATA-33-REFACTOR(ui): Extract Button Styles to Tailwind Classes

Moved inline Tailwind classes to component variants using
class-variance-authority. This improves:
- Type safety (TypeScript knows valid variants)
- Consistency (same button style everywhere)
- Bundle size (reduced CSS duplication)

No behavior changes. All existing button props still work.
```

### Example 4: Breaking Change

```bash
TDATA-50-FEAT(auth): Migrate JWT to UUID-Based Claims

Changed JWT structure to use UUID-based 'userId' claim instead
of email-based 'sub' claim. This provides:
- Better privacy (email not exposed in tokens)
- Immutability (userId never changes, email can)
- Consistency (all services use UUID references)

BREAKING CHANGE: JWT structure changed. Services must update:
1. Change jwt.getClaim('sub') to jwt.getClaim('userId')
2. Update @PreAuthorize expressions if using 'sub'
3. Clear existing JWT cookies (force re-login)

Migration guide: docs/migrations/jwt-uuid-migration.md
Closes TDATA-50
```

### Example 5: Multi-Scope Change

```bash
TDATA-60-FEAT(fleet,booking): Add Real-Time Availability Check

- Added fleet-service endpoint: GET /vehicles/{id}/availability
- Booking-service now calls fleet before creating booking
- Prevents double-booking race condition

Updated API contract documented in docs/api/fleet-booking-integration.md

Closes TDATA-60
```

### Example 6: Chore

```bash
TDATA-99-CHORE(infra): Upgrade Turborepo to v2.0

Upgraded from Turborepo v1.13 to v2.0 for improved caching.

Changes:
- Updated turbo.json to v2 config format
- Migrated pipeline to tasks
- Enabled remote caching in CI

Build times reduced by ~30% in CI.
```

---

## 9. Common Mistakes

### Mistake 1: Vague Titles

```bash
# Bad
TDATA-42-FIX(user): Fix issue

# Good
TDATA-42-FIX(user): Fix Login Button Not Responding on Mobile
```

### Mistake 2: Missing Scope

```bash
# Bad
TDATA-42-FEAT: Add login

# Good
TDATA-42-FEAT(user): Add Google Login Button
```

### Mistake 3: Wrong Type

```bash
# Bad (Should be FEAT)
TDATA-42-FIX(ui): Add new button component

# Good
TDATA-42-FEAT(ui): Add Primary Button Component
```

### Mistake 4: Past Tense

```bash
# Bad
TDATA-42-FEAT(user): Added login page

# Good
TDATA-42-FEAT(user): Add Login Page
```

### Mistake 5: Too Long

```bash
# Bad
TDATA-42-FEAT(user): Add google oauth login button with loading state and error handling

# Good
TDATA-42-FEAT(user): Add Google OAuth Login Button
# Details in commit body if needed
```

---

## 10. Verification Checklist

Before committing, verify:

- [ ] Jira ticket number included (TDATA-XX)
- [ ] Type is correct and UPPERCASE (FEAT, FIX, etc.)
- [ ] Scope matches directory from scope table
- [ ] Title is Title Case and imperative mood
- [ ] Title is under 72 characters
- [ ] No period at end of title
- [ ] Body added if change is complex (optional)
- [ ] Breaking changes documented in footer (if applicable)
- [ ] Jira ticket closed in footer (if applicable)

---

## 11. Tools & Automation

### Pre-Commit Hook (Optional)

Validate commit messages automatically:

```bash
# .husky/commit-msg
#!/bin/sh
npx --no -- commitlint --edit "$1"
```

### Commitlint Configuration

```javascript
// commitlint.config.js
module.exports = {
  parserPreset: {
    parserOpts: {
      headerPattern: /^TDATA-\d+-([A-Z]+)\((.+)\): (.+)$/,
      headerCorrespondence: ["type", "scope", "subject"],
    },
  },
  rules: {
    "type-enum": [
      2,
      "always",
      [
        "FEAT",
        "FIX",
        "DOCS",
        "STYLE",
        "REFACTOR",
        "TEST",
        "CHORE",
        "PERF",
        "CI",
        "BUILD",
        "REVERT",
      ],
    ],
    "scope-enum": [
      2,
      "always",
      [
        "user",
        "fleet-ui",
        "admin",
        "ui",
        "utils",
        "auth",
        "fleet",
        "booking",
        "common",
        "infra",
      ],
    ],
    "subject-case": [2, "always", "sentence-case"],
    "header-max-length": [2, "always", 72],
  },
};
```

---

## 12. Related Documentation

- [CONTRIBUTING.md](./CONTRIBUTING.md) - Full contributing guide with scope table
- [GIT_WORKFLOW.md](./GIT_WORKFLOW.md) - Branching strategy and workflow
- [CODE_STANDARDS.md](./CODE_STANDARDS.md) - Code quality standards

---

**Remember:** Good commit messages help future developers (including future you) understand **why** changes were made. Take the extra 30 seconds to write clear, descriptive commits.
