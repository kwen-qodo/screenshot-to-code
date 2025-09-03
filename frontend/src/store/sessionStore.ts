// src/store/sessionStore.ts
// Zustand store for user session tracking and session action log
// Follows best practices: typed store, action methods, session persistence
//
// SECURITY WARNING (see ../lib/session.ts):
// - NEVER store sensitive data (PII, credentials, tokens, secrets) in action payloads.
// - sessionId, action log, and all session storage are visible and modifiable from any script in this browser context.
// - If rendering actions to the UI, sanitize content to prevent XSS attacks.

import { create } from 'zustand';
import { getSessionId, logSessionAction, getSessionActions, clearSessionActions, SessionAction } from '../lib/session';

interface SessionState {
  sessionId: string;
  actions: SessionAction[];
  logAction: (type: string, payload?: Record<string, unknown>) => void;
  refreshActions: () => void;
  clearActions: () => void;
}

export const useSessionStore = create<SessionState>((set, get) => ({
  sessionId: getSessionId(),
  actions: getSessionActions(),
  logAction: (type, payload) => {
    // SECURITY WARNING: see logSessionAction and above. ALWAYS review payload contents for sensitive data.
    logSessionAction({ type, payload });
    set({ actions: getSessionActions() }); // update live
  },
  refreshActions: () => set({ actions: getSessionActions() }),
  clearActions: () => {
    clearSessionActions();
    set({ actions: [] });
  },
}));
