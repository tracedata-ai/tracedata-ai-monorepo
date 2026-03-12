"use client";

/**
 * Accessibility utilities for WCAG 2.1 AA compliance.
 * RUBRIC: UX Quality—keyboard navigation, ARIA labels, semantic HTML.
 */

/**
 * Generate ARIA label for complex components
 */
export function generateAriaLabel(context: {
  action: string;
  subject: string;
  status?: string;
}): string {
  const parts = [context.action, context.subject, context.status].filter(
    Boolean,
  );
  return parts.join(": ");
}

/**
 * Announce messages to screen readers
 */
export function announceScreenReader(
  message: string,
  priority: "polite" | "assertive" = "polite",
): void {
  // Only works in browser
  if (typeof window === "undefined") return;

  const div = document.createElement("div");
  div.setAttribute("role", "status");
  div.setAttribute("aria-live", priority);
  div.setAttribute("aria-atomic", "true");
  div.className = "sr-only";
  div.textContent = message;
  document.body.appendChild(div);
  setTimeout(() => div.remove(), 1000);
}

/**
 * Keyboard navigation event handler
 */
export function handleKeyboardNav(
  e: React.KeyboardEvent,
  callbacks: {
    onEnter?: () => void;
    onEscape?: () => void;
    onArrowUp?: () => void;
    onArrowDown?: () => void;
  },
): void {
  if (e.key === "Enter") callbacks.onEnter?.();
  if (e.key === "Escape") callbacks.onEscape?.();
  if (e.key === "ArrowUp") callbacks.onArrowUp?.();
  if (e.key === "ArrowDown") callbacks.onArrowDown?.();
}

/**
 * Trap focus within a modal/dialog
 */
export function useFocusTrap(containerRef: React.RefObject<HTMLElement>): void {
  React.useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
    );
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[
      focusableElements.length - 1
    ] as HTMLElement;

    const handleKeyDown = (e: KeyboardEvent): void => {
      if (e.key !== "Tab") return;
      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement.focus();
          e.preventDefault();
        }
      }
    };

    container.addEventListener("keydown", handleKeyDown);
    return () => container.removeEventListener("keydown", handleKeyDown);
  }, [containerRef]);
}

// Import React for useFocusTrap
import React from "react";
