import { create } from "zustand";

import type { SessionUser } from "@/lib/types";

type Toast = {
  id: number;
  title: string;
  tone?: "success" | "error" | "info";
};

type AppState = {
  session: SessionUser | null;
  toasts: Toast[];
  setSession: (session: SessionUser | null) => void;
  pushToast: (toast: Omit<Toast, "id">) => void;
  dismissToast: (id: number) => void;
};

export const useAppStore = create<AppState>((set) => ({
  session: null,
  toasts: [],
  setSession: (session) => set({ session }),
  pushToast: (toast) =>
    set((state) => ({
      toasts: [...state.toasts, { id: Date.now() + Math.floor(Math.random() * 1000), ...toast }],
    })),
  dismissToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((toast) => toast.id !== id),
    })),
}));
