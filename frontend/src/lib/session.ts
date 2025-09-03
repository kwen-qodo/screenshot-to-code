// src/lib/session.ts
// User session management and action tracking utility
// Follows best practices for unique IDs, browser storage, and clean typing
//
// SECURITY WARNING:
// - DO NOT log any sensitive personal information (PII), credentials, tokens, or secrets in actions.
// - Payloads are stored as JSON in sessionStorage and may be read or manipulated by malicious scripts or browser extensions.
// - Always sanitize and validate user-controlled content before storage and especially before rendering in the UI.
// - This storage is NOT safe for trust boundaries or confidential data.
//

export type SessionAction = {
  type: string; // e.g., 'NAVIGATE', 'CLICK', ...
  payload?: Record<string, unknown>;
  timestamp: number;
};

const SESSION_ID_KEY = 'session_id';

// Generate a RFC4122-compliant v4 UUID (no external dep)
function uuidv4(): string {
  // @ts-ignore - Crypto API browser support
  return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
    (
      Number(c) ^
      crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (Number(c) / 4))
    ).toString(16)
  );
}

// Get or initialize a session ID, persisted for the browser session
export function getSessionId(): string {
  let id = sessionStorage.getItem(SESSION_ID_KEY);
  if (!id) {
    id = uuidv4();
    sessionStorage.setItem(SESSION_ID_KEY, id);
  }
  return id;
}

// Log a user action in sessionStorage (appends to the action log)
/**
 * logSessionAction
 * 
 * SECURITY:
 *   - Do NOT log sensitive data such as passwords, tokens, user emails, or personally identifiable data.
 *   - All payloads in actions are persisted as plaintext in sessionStorage, which is accessible client-side.
 *   - If action.payload contains keys like "token", "password", "email", or other sensitive patterns, a warning will be issued in dev mode.
 *   - Do NOT log or render user-controlled content without proper escaping/sanitizing downstream (XSS risk).
 */
export function logSessionAction(action: Omit<SessionAction, 'timestamp'>) {
  // Security/runtime check for sensitive key names in payload
  if (
    typeof window !== 'undefined' &&
    process.env.NODE_ENV !== 'production' &&
    typeof action.payload === 'object' &&
    action.payload !== null
  ) {
    const forbiddenKeys = ['token', 'password', 'secret', 'credential', 'email'];
    for (const k of Object.keys(action.payload)) {
      if (forbiddenKeys.some(f => k.toLowerCase().includes(f))) {
        // eslint-disable-next-line no-console
        console.warn(
          `[SECURITY] Action payload contains sensitive field ("${k}"). Do NOT log PII or secrets in session actions.`
        );
      }
    }
  }
  const entry: SessionAction = {
    ...action,
    timestamp: Date.now(),
  };
  const rawLog = sessionStorage.getItem('session_actions');
  const actions: SessionAction[] = rawLog ? JSON.parse(rawLog) : [];
  actions.push(entry);
  sessionStorage.setItem('session_actions', JSON.stringify(actions));
}

// Retrieve the entire session action log
export function getSessionActions(): SessionAction[] {
  const rawLog = sessionStorage.getItem('session_actions');
  return rawLog ? JSON.parse(rawLog) : [];
}

// (Optional) Clear the log (e.g. for testing/debugging)
export function clearSessionActions() {
  sessionStorage.removeItem('session_actions');
}
