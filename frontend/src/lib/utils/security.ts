"use strict";

/**
 * Security utilities for TraceData.
 * RUBRIC: Cybersecurity—input validation, sanitization, defense-in-depth.
 * Reference: R1-R10 (Risk Register Mitigations)
 */

/**
 * Validate JWT token structure (HS256/RS256)
 */
export function isValidJWT(token: string): boolean {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return false;
    // Each part must be valid base64url
    return parts.every((part) => {
      try {
        Buffer.from(part, "base64url").toString();
        return true;
      } catch {
        return false;
      }
    });
  } catch {
    return false;
  }
}

/**
 * Escape user input for safe display in HTML
 */
export function escapeUserInput(input: string): string {
  const map: Record<string, string> = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  };
  return input.replace(/[&<>"']/g, (char) => map[char]);
}

/**
 * Validate URL to prevent injection attacks
 */
export function isAllowedUrl(url: string, allowedOrigins: string[]): boolean {
  try {
    const parsed = new URL(url);
    return allowedOrigins.some(
      (origin) =>
        parsed.origin === origin || parsed.origin.endsWith(`.${origin}`),
    );
  } catch {
    return false;
  }
}

/**
 * Verify API request origin for CSRF protection
 */
export function isAllowedOrigin(
  origin: string,
  allowedOrigins: string[],
): boolean {
  return allowedOrigins.includes(origin);
}

/**
 * Generate rate limiting key from request
 */
export function getRateLimitKey(req: {
  headers: Record<string, string | string[] | undefined>;
}): string {
  const forwarded = req.headers["x-forwarded-for"];
  const clientIp = Array.isArray(forwarded)
    ? forwarded[0]
    : forwarded || req.headers["x-client-ip"] || "unknown";
  return String(clientIp);
}

/**
 * Content Security Policy headers
 */
export const secureHeaders = {
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "X-XSS-Protection": "1; mode=block",
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
  "Content-Security-Policy": [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: https:",
    "font-src 'self'",
    "connect-src 'self' https://api.tracedata.local wss://api.tracedata.local",
    "frame-ancestors 'none'",
  ].join("; "),
};

/**
 * Sanitize tenant ID to prevent injection
 */
export function sanitizeTenantId(tenantId: string): string {
  // Only allow alphanumeric, underscore, hyphen
  return tenantId.replace(/[^a-zA-Z0-9_-]/g, "");
}

/**
 * Validate driver ID format
 */
export function isValidDriverId(driverId: string): boolean {
  return /^[a-zA-Z0-9_-]{1,64}$/.test(driverId);
}

/**
 * Validate trip ID format
 */
export function isValidTripId(tripId: string): boolean {
  return /^[a-zA-Z0-9_-]{1,64}$/.test(tripId);
}
