"use client";

import { useEffect } from "react";

export interface ShortcutHandlers {
  onCtrlK?: () => void;
  onCtrlEnter?: () => void;
  onCtrlS?: () => void;
  onCtrlShiftP?: () => void;
  onEsc?: () => void;
}

export function useKeyboardShortcuts(handlers: ShortcutHandlers) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // 1. Esc handler (always active, doesn't need modifiers)
      if (event.key === "Escape") {
        if (handlers.onEsc) {
          event.preventDefault();
          handlers.onEsc();
        }
        return;
      }

      // Check Ctrl modifiers (or Cmd on macOS)
      const isCtrl = event.ctrlKey || event.metaKey;
      if (!isCtrl) return;

      // 2. Ctrl + K (Command Palette toggle)
      if (event.key.toLowerCase() === "k") {
        if (handlers.onCtrlK) {
          event.preventDefault();
          handlers.onCtrlK();
        }
        return;
      }

      // 3. Ctrl + S (Save template)
      if (event.key.toLowerCase() === "s") {
        if (handlers.onCtrlS) {
          event.preventDefault();
          handlers.onCtrlS();
        }
        return;
      }

      // 4. Ctrl + Enter (Send message / Run test)
      if (event.key === "Enter") {
        if (handlers.onCtrlEnter) {
          event.preventDefault();
          handlers.onCtrlEnter();
        }
        return;
      }

      // 5. Ctrl + Shift + P (Actions selector / Palette)
      if (event.key.toLowerCase() === "p" && event.shiftKey) {
        if (handlers.onCtrlShiftP) {
          event.preventDefault();
          handlers.onCtrlShiftP();
        }
        return;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [handlers]);
}
