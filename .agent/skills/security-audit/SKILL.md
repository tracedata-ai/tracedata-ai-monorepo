---
description: Security Audit and Threat Modeling (STRIDE)
name: security-audit
---

# Security Audit Skill

As a Senior Engineer, your skill is to intercept any new FastAPI routes I write and verify them against the STRIDE threat model. If I forget to add an `OAuth` dependency, you must flag it before I commit.

## Guidelines

1. **Intercept New Routes**: When new FastAPI routes are added, verify they include appropriate security dependencies.
2. **STRIDE Analysis**: Apply the STRIDE threat model to identify potential vulnerabilities:
   - **Spoofing**: Ensure strong authentication.
   - **Tampering**: Validate input and ensure integrity.
   - **Repudiation**: Ensure actionable logging.
   - **Information Disclosure**: Prevent data leaks (e.g., PII in logs/responses).
   - **Denial of Service**: Check for rate limiting or resource exhaustion risks.
   - **Elevation of Privilege**: Verify authorization checks (RBAC).
3. **Dependency Checks**: Flag missing `OAuth2PasswordBearer` or `Depends(get_current_user)` where required.
